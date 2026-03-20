#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.migration import diagnose_failure, write_health_failure_report
from lab.health_checks import (
    append_rolling_baseline_history,
    baseline_freshness_check,
    load_config_preflight_stats,
    load_rolling_baseline,
    validate_profile_expectations,
    validate_system_health_summary_payload,
)

REQUIRED_METRICS_COLUMNS = [
    "schema_version",
    "run_name",
    "MODEL",
    "attack",
    "defense",
    "images_with_detections",
    "total_detections",
    "avg_conf",
    "precision",
    "recall",
    "mAP50",
    "mAP50-95",
]
REQUIRED_PARITY_DELTA_KEYS = [
    "detection_worst_relative_pct",
    "confidence_worst_relative_pct",
]
SYSTEM_HEALTH_SUMMARY_SCHEMA_VERSION = "system_health_summary/v1"
AUTO_FIX_STAGE_ALLOWLIST = {"artifacts", "data_consistency", "parity_report"}


def _run(command: list[str], *, stage: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"src:{existing_pythonpath}" if existing_pythonpath else "src"
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"{stage} failed (exit {proc.returncode}): {' '.join(command)}")
    return proc


def _latest_shadow_run(shadow_root: Path) -> Path:
    candidates = sorted(
        [path for path in shadow_root.iterdir() if path.is_dir() and (path / "parity_report.json").is_file()],
        key=lambda p: p.name,
    )
    if not candidates:
        raise FileNotFoundError(f"No shadow runs with parity_report.json under {shadow_root}")
    return candidates[-1]


def _validate_csv_integrity(path: Path, required_columns: list[str]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not path.is_file():
        return False, [f"missing file: {path}"]
    if path.stat().st_size <= 0:
        return False, [f"empty file: {path}"]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        missing = [col for col in required_columns if col not in headers]
        if missing:
            issues.append(f"missing required columns: {missing}")
        rows = list(reader)
        if not rows:
            issues.append("no rows present")
        for metric_col in ("precision", "recall", "mAP50", "mAP50-95"):
            if metric_col in headers and rows:
                if all(str(row.get(metric_col, "")).strip().lower() in {"", "nan", "none", "null"} for row in rows):
                    issues.append(f"NaN-only metric field: {metric_col}")
    return len(issues) == 0, issues


def _validate_markdown_nonempty(path: Path) -> tuple[bool, list[str]]:
    if not path.is_file():
        return False, [f"missing file: {path}"]
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return False, [f"empty markdown: {path}"]
    return True, []


def _read_json_mapping(path: Path, *, stage: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"{stage}: missing file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{stage}: failed to parse JSON file={path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{stage}: invalid JSON mapping file={path} type={type(payload).__name__}")
    return payload


def _validate_parity_report(path: Path) -> tuple[bool, list[str], dict[str, Any]]:
    issues: list[str] = []
    if not path.is_file():
        return False, [f"missing file: {path}"], {}
    if path.stat().st_size <= 0:
        return False, [f"empty file: {path}"], {}
    try:
        payload = _read_json_mapping(path, stage="artifact_validation")
    except (FileNotFoundError, ValueError) as exc:
        return False, [str(exc)], {}
    required = ["parity_pass", "delta_summary"]
    for key in required:
        if key not in payload:
            issues.append(f"missing key in parity report: {key}")
    if "delta_summary" in payload and not isinstance(payload.get("delta_summary"), dict):
        issues.append("invalid delta_summary payload type")
    return len(issues) == 0, issues, payload


def _data_consistency_check(
    *,
    parity_report: dict[str, Any],
    detection_threshold_pct: float,
    confidence_threshold_pct: float,
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    delta = parity_report.get("delta_summary", {})
    if not isinstance(delta, dict):
        return False, ["delta_summary missing or invalid in parity report"]
    missing_metrics = [key for key in REQUIRED_PARITY_DELTA_KEYS if key not in delta]
    if missing_metrics:
        issues.append(f"missing expected parity metrics: {missing_metrics}")
    detection = abs(float(delta.get("detection_worst_relative_pct") or 0.0))
    confidence = abs(float(delta.get("confidence_worst_relative_pct") or 0.0))
    if detection > detection_threshold_pct:
        issues.append(
            f"detection drift {detection:.4f}% exceeds threshold {detection_threshold_pct:.4f}%"
        )
    if confidence > confidence_threshold_pct:
        issues.append(
            f"confidence drift {confidence:.4f}% exceeds threshold {confidence_threshold_pct:.4f}%"
        )
    if math.isnan(detection) or math.isnan(confidence):
        issues.append("drift contains NaN")
    return len(issues) == 0, issues


def _build_current_snapshot(
    *,
    metrics_csv: Path,
    experiment_table_md: Path,
    parity_report: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    rows: list[dict[str, str]] = []
    try:
        with metrics_csv.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error) as exc:
        issues.append(f"failed reading metrics csv for regression snapshot: {exc}")
    _assert_required_metrics_for_drift(rows=rows, metrics_csv=metrics_csv)

    detections_total = 0
    images_with_detections_total = 0
    avg_conf_values: list[float] = []
    for row in rows:
        try:
            detections_total += int(float(str(row.get("total_detections", "0") or "0")))
        except ValueError:
            continue
        try:
            images_with_detections_total += int(float(str(row.get("images_with_detections", "0") or "0")))
        except ValueError:
            continue
        try:
            avg_conf_values.append(float(str(row.get("avg_conf", "nan") or "nan")))
        except ValueError:
            pass
    avg_conf_mean = sum(avg_conf_values) / len(avg_conf_values) if avg_conf_values else 0.0
    conf_p25_values: list[float] = []
    conf_p50_values: list[float] = []
    conf_p75_values: list[float] = []
    for row in rows:
        for key, bucket in (
            ("p25_conf", conf_p25_values),
            ("median_conf", conf_p50_values),
            ("p75_conf", conf_p75_values),
        ):
            try:
                bucket.append(float(str(row.get(key, "nan") or "nan")))
            except ValueError:
                continue
    delta = parity_report.get("delta_summary", {})
    if not isinstance(delta, dict):
        delta = {}
        issues.append("parity delta summary missing for regression snapshot")
    return (
        {
            "detection_worst_relative_pct": float(delta.get("detection_worst_relative_pct") or 0.0),
            "confidence_worst_relative_pct": float(delta.get("confidence_worst_relative_pct") or 0.0),
            "total_detections": detections_total,
            "images_with_detections": images_with_detections_total,
            "avg_conf_mean": avg_conf_mean,
            "avg_conf_p25": (sum(conf_p25_values) / len(conf_p25_values)) if conf_p25_values else 0.0,
            "avg_conf_p50": (sum(conf_p50_values) / len(conf_p50_values)) if conf_p50_values else 0.0,
            "avg_conf_p75": (sum(conf_p75_values) / len(conf_p75_values)) if conf_p75_values else 0.0,
            "metrics_summary_size_bytes": metrics_csv.stat().st_size if metrics_csv.is_file() else 0,
            "experiment_table_size_bytes": experiment_table_md.stat().st_size if experiment_table_md.is_file() else 0,
        },
        issues,
    )


def _assert_required_metrics_for_drift(*, rows: list[dict[str, str]], metrics_csv: Path) -> None:
    if not rows:
        raise ValueError(f"drift precondition failed: no rows in {metrics_csv}")
    required_columns = [
        "total_detections",
        "images_with_detections",
        "avg_conf",
        "median_conf",
    ]
    optional_quantile_columns = ["p25_conf", "p75_conf"]
    missing_columns = [col for col in required_columns if all(col not in row for row in rows)]
    if missing_columns:
        raise ValueError(
            f"drift precondition failed: missing required metric columns in {metrics_csv}: {missing_columns}"
        )
    for col in required_columns:
        has_value = any(str(row.get(col, "")).strip().lower() not in {"", "nan", "none", "null"} for row in rows)
        if not has_value:
            raise ValueError(f"drift precondition failed: metric '{col}' missing/empty across all rows in {metrics_csv}")
    missing_optional_quantiles = [
        col
        for col in optional_quantile_columns
        if all(str(row.get(col, "")).strip().lower() in {"", "nan", "none", "null"} for row in rows)
    ]
    if missing_optional_quantiles:
        print(
            "WARNING: drift precondition optional quantiles missing across all rows in "
            f"{metrics_csv}: {missing_optional_quantiles}. Continuing with available confidence metrics."
        )


def _schema_check(framework_run_dir: Path, legacy_csv: Path) -> tuple[bool, list[str]]:
    try:
        _run(
            [
                sys.executable,
                str(ROOT / "scripts/ci/validate_output_schemas.py"),
                "--framework-run-dir",
                str(framework_run_dir),
                "--legacy-compat-csv",
                str(legacy_csv),
            ],
            stage="schema_validation",
        )
        return True, []
    except Exception as exc:
        return False, [str(exc)]


def _load_regression_baseline(path: Path, allow_missing: bool) -> tuple[dict[str, Any], list[str]]:
    if not path.is_file():
        if allow_missing:
            return {}, ["baseline report missing; allowed by flag"]
        return {}, [f"baseline report missing: {path}"]
    try:
        payload = _read_json_mapping(path, stage="regression_baseline")
    except (FileNotFoundError, ValueError) as exc:
        return {}, [str(exc)]
    return payload, []


def _regression_check(
    *,
    baseline: dict[str, Any],
    current_snapshot: dict[str, Any],
    max_regression_pct: float,
    max_size_drift_pct: float,
) -> tuple[bool, list[str], dict[str, Any]]:
    issues: list[str] = []
    if not baseline:
        return False, ["missing baseline for regression comparison"], {
            "regression_detected": True,
            "regression_summary": "baseline missing",
        }
    baseline_detection = float(baseline.get("detection_worst_relative_pct", 0.0))
    baseline_conf = float(baseline.get("confidence_worst_relative_pct", 0.0))
    baseline_total_detections = float(baseline.get("total_detections", 0.0))
    baseline_images_with_det = float(baseline.get("images_with_detections", 0.0))
    baseline_avg_conf = float(baseline.get("avg_conf_mean", 0.0))
    baseline_conf_p25 = float(baseline.get("avg_conf_p25", 0.0))
    baseline_conf_p50 = float(baseline.get("avg_conf_p50", 0.0))
    baseline_conf_p75 = float(baseline.get("avg_conf_p75", 0.0))
    baseline_metrics_size = float(baseline.get("metrics_summary_size_bytes", 0.0))
    baseline_table_size = float(baseline.get("experiment_table_size_bytes", 0.0))

    current_detection = abs(float(current_snapshot.get("detection_worst_relative_pct") or 0.0))
    current_conf = abs(float(current_snapshot.get("confidence_worst_relative_pct") or 0.0))
    current_total_detections = float(current_snapshot.get("total_detections", 0.0))
    current_images_with_det = float(current_snapshot.get("images_with_detections", 0.0))
    current_avg_conf = float(current_snapshot.get("avg_conf_mean", 0.0))
    current_conf_p25 = float(current_snapshot.get("avg_conf_p25", 0.0))
    current_conf_p50 = float(current_snapshot.get("avg_conf_p50", 0.0))
    current_conf_p75 = float(current_snapshot.get("avg_conf_p75", 0.0))
    current_metrics_size = float(current_snapshot.get("metrics_summary_size_bytes", 0.0))
    current_table_size = float(current_snapshot.get("experiment_table_size_bytes", 0.0))

    detection_jump = current_detection - baseline_detection
    confidence_jump = current_conf - baseline_conf
    if detection_jump > max_regression_pct:
        issues.append(
            f"detection regression +{detection_jump:.4f}% > {max_regression_pct:.4f}% over baseline"
        )
    if confidence_jump > max_regression_pct:
        issues.append(
            f"confidence regression +{confidence_jump:.4f}% > {max_regression_pct:.4f}% over baseline"
        )
    detection_count_jump = abs(current_total_detections - baseline_total_detections)
    if baseline_total_detections > 0:
        detection_count_jump_pct = (detection_count_jump / baseline_total_detections) * 100.0
        if detection_count_jump_pct > max_regression_pct:
            issues.append(
                f"total_detections drift {detection_count_jump_pct:.4f}% > {max_regression_pct:.4f}%"
            )
    images_count_jump = abs(current_images_with_det - baseline_images_with_det)
    if baseline_images_with_det > 0:
        images_count_jump_pct = (images_count_jump / baseline_images_with_det) * 100.0
        if images_count_jump_pct > max_regression_pct:
            issues.append(
                f"images_with_detections drift {images_count_jump_pct:.4f}% > {max_regression_pct:.4f}%"
            )
    conf_dist_jump = abs(current_avg_conf - baseline_avg_conf)
    if conf_dist_jump > max_regression_pct / 100.0:
        issues.append(
            f"confidence distribution mean drift {conf_dist_jump:.6f} > {max_regression_pct / 100.0:.6f}"
        )
    for name, current_value, baseline_value in (
        ("p25", current_conf_p25, baseline_conf_p25),
        ("p50", current_conf_p50, baseline_conf_p50),
        ("p75", current_conf_p75, baseline_conf_p75),
    ):
        jump = abs(current_value - baseline_value)
        if jump > max_regression_pct / 100.0:
            issues.append(
                f"confidence distribution {name} drift {jump:.6f} > {max_regression_pct / 100.0:.6f}"
            )

    def _size_drift_pct(current: float, baseline_value: float) -> float:
        if baseline_value <= 0:
            return 0.0
        return abs(current - baseline_value) / baseline_value * 100.0

    metrics_size_drift = _size_drift_pct(current_metrics_size, baseline_metrics_size)
    table_size_drift = _size_drift_pct(current_table_size, baseline_table_size)
    if metrics_size_drift > max_size_drift_pct:
        issues.append(
            f"metrics_summary.csv size drift {metrics_size_drift:.2f}% > {max_size_drift_pct:.2f}%"
        )
    if table_size_drift > max_size_drift_pct:
        issues.append(
            f"experiment_table.md size drift {table_size_drift:.2f}% > {max_size_drift_pct:.2f}%"
        )

    return len(issues) == 0, issues, {
        "regression_detected": len(issues) > 0,
        "regression_summary": "; ".join(issues) if issues else "no regression detected",
    }


def _auto_fix(
    *,
    issue_stage: str,
    demo_output_root: Path,
    parity_config: Path,
    demo_profile: str,
) -> tuple[list[str], list[str]]:
    performed: list[str] = []
    blocked: list[str] = []
    if issue_stage not in AUTO_FIX_STAGE_ALLOWLIST:
        blocked.append(f"blocked stage '{issue_stage}' not in allowlist")
        return performed, blocked
    if issue_stage == "artifacts":
        # regenerate expected demo artifacts using existing framework-first flow
        _run(
            [
                "bash",
                str(ROOT / "scripts/demo/run_demo_package.sh"),
                "fast",
                "--profile",
                demo_profile,
                "--output-root",
                str(demo_output_root),
            ],
            stage="auto_fix_demo_artifacts",
        )
        performed.append("Regenerated demo artifacts via demo fast path.")
    elif issue_stage in {"data_consistency", "parity_report"}:
        _run(
            [
                sys.executable,
                str(ROOT / "run_shadow_parity.py"),
                "--config",
                str(parity_config),
            ],
            stage="auto_fix_parity_rerun",
        )
        performed.append("Regenerated parity report via run_shadow_parity.")
    return performed, blocked


def main() -> None:
    parser = argparse.ArgumentParser(description="Global system health check for framework-first migration.")
    parser.add_argument("--parity-config", default="configs/parity_test.yaml")
    parser.add_argument("--demo-profile", default="demo")
    parser.add_argument("--demo-output-root", default="outputs/health_demo")
    parser.add_argument("--health-output-root", default="outputs/system_health")
    parser.add_argument("--shadow-root", default="outputs/shadow_parity")
    parser.add_argument("--baseline-report", default="outputs/system_health/baseline_report_latest.json")
    parser.add_argument("--baseline-history", default="outputs/system_health/baseline_history.jsonl")
    parser.add_argument("--health-log", default="outputs/migration_state/system_health_log.jsonl")
    parser.add_argument("--max-detection-drift-pct", type=float, default=5.0)
    parser.add_argument("--max-confidence-drift-pct", type=float, default=5.0)
    parser.add_argument("--max-regression-pct", type=float, default=2.0)
    parser.add_argument("--max-output-size-drift-pct", type=float, default=30.0)
    parser.add_argument("--baseline-window", type=int, default=10)
    parser.add_argument("--baseline-max-age-hours", type=float, default=168.0)
    parser.add_argument("--fail-on-stale-baseline", action="store_true")
    parser.add_argument("--allow-missing-baseline", action="store_true")
    parser.add_argument("--auto-fix", action="store_true")
    parser.add_argument("--skip-execution", action="store_true")
    args = parser.parse_args()

    health_output_root = Path(args.health_output_root).expanduser().resolve()
    health_output_root.mkdir(parents=True, exist_ok=True)
    demo_output_root = Path(args.demo_output_root).expanduser().resolve()
    parity_config = Path(args.parity_config).expanduser().resolve()
    baseline_path = Path(args.baseline_report).expanduser().resolve()
    baseline_history_path = Path(args.baseline_history).expanduser().resolve()
    shadow_root = Path(args.shadow_root).expanduser().resolve()
    correlation_id = os.environ.get("MIGRATION_CORRELATION_ID", "")

    results = {
        "execution": {"ok": True, "issues": []},
        "artifacts": {"ok": True, "issues": []},
        "schema": {"ok": True, "issues": []},
        "regression": {"ok": True, "issues": []},
        "data_consistency": {"ok": True, "issues": []},
    }
    diagnostics_payload: dict[str, Any] = {}
    auto_fix_actions: list[str] = []
    auto_fix_blocked_actions: list[str] = []
    regression_summary: dict[str, Any] = {"regression_detected": False, "regression_summary": "not_run"}

    try:
        # Profile/data preflight before any expensive execution commands.
        preflight_stats = load_config_preflight_stats(
            config_path=ROOT / "configs/lab_framework_phase5.yaml",
            attack_name="fgsm",
        )
        preflight_stats.update(
            {
                "expected_attack_rows": 1,
                "fgsm_present": True,
                "fgsm_required": True,
            }
        )
        validate_profile_expectations(args.demo_profile, preflight_stats)

        # A. Execution health
        if not args.skip_execution:
            _run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_unified.py"),
                    "run-one",
                    "--config",
                    "configs/lab_framework_phase5.yaml",
                    "--set",
                    "runner.run_name=health_single_run",
                    "--set",
                    "runner.max_images=2",
                    "--set",
                    "validation.enabled=false",
                    "--set",
                    f"runner.output_root={health_output_root / 'framework_runs'}",
                ],
                stage="execution_single_run",
            )
            _run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_unified.py"),
                    "sweep",
                    "--config",
                    "configs/lab_framework_phase5.yaml",
                    "--runs-root",
                    str(health_output_root / "sweep_runs"),
                    "--report-root",
                    str(health_output_root / "sweep_reports"),
                    "--attacks",
                    "fgsm",
                    "--validation-enabled",
                ],
                stage="execution_sweep",
            )
            # Ensure demo pipeline regenerates adapter-backed artifacts from current framework runs.
            for stale in (demo_output_root / "metrics_summary.csv", demo_output_root / "experiment_table.md"):
                if stale.is_file():
                    stale.unlink()
            _run(
                [
                    "bash",
                    str(ROOT / "scripts/demo/run_demo_package.sh"),
                    "fast",
                    "--profile",
                    args.demo_profile,
                    "--output-root",
                    str(demo_output_root),
                    "--framework-runs-root",
                    str(health_output_root / "sweep_runs"),
                ],
                stage="execution_demo",
            )

        # B. Artifact integrity
        metrics_csv = demo_output_root / "metrics_summary.csv"
        table_md = demo_output_root / "experiment_table.md"
        shadow_run = _latest_shadow_run(shadow_root)
        parity_report_path = shadow_run / "parity_report.json"
        csv_ok, csv_issues = _validate_csv_integrity(
            metrics_csv,
            required_columns=REQUIRED_METRICS_COLUMNS,
        )
        md_ok, md_issues = _validate_markdown_nonempty(table_md)
        parity_ok, parity_issues, parity_report = _validate_parity_report(parity_report_path)
        artifact_issues = csv_issues + md_issues + parity_issues
        if artifact_issues:
            results["artifacts"]["ok"] = False
            results["artifacts"]["issues"] = artifact_issues
            if args.auto_fix:
                performed, blocked = _auto_fix(
                    issue_stage="artifacts",
                    demo_output_root=demo_output_root,
                    parity_config=parity_config,
                    demo_profile=args.demo_profile,
                )
                auto_fix_actions.extend(performed)
                auto_fix_blocked_actions.extend(blocked)
                csv_ok, csv_issues = _validate_csv_integrity(
                    metrics_csv,
                    required_columns=REQUIRED_METRICS_COLUMNS,
                )
                md_ok, md_issues = _validate_markdown_nonempty(table_md)
                parity_ok, parity_issues, parity_report = _validate_parity_report(parity_report_path)
                artifact_issues = csv_issues + md_issues + parity_issues
                results["artifacts"]["ok"] = len(artifact_issues) == 0
                results["artifacts"]["issues"] = artifact_issues

        # C. Data consistency
        consistency_ok, consistency_issues = _data_consistency_check(
            parity_report=parity_report,
            detection_threshold_pct=float(args.max_detection_drift_pct),
            confidence_threshold_pct=float(args.max_confidence_drift_pct),
        )
        if not consistency_ok:
            results["data_consistency"]["ok"] = False
            results["data_consistency"]["issues"] = consistency_issues
            if args.auto_fix:
                performed, blocked = _auto_fix(
                    issue_stage="data_consistency",
                    demo_output_root=demo_output_root,
                    parity_config=parity_config,
                    demo_profile=args.demo_profile,
                )
                auto_fix_actions.extend(performed)
                auto_fix_blocked_actions.extend(blocked)

        # D. Schema validation
        framework_run_dir = shadow_run / "framework"
        framework_candidates = sorted([p for p in framework_run_dir.iterdir() if p.is_dir()], key=lambda p: p.name)
        if not framework_candidates:
            raise FileNotFoundError(f"No framework run directories found in {framework_run_dir}")
        schema_ok, schema_issues = _schema_check(framework_candidates[-1], metrics_csv)
        if not schema_ok:
            results["schema"]["ok"] = False
            results["schema"]["issues"] = schema_issues

        # E. Regression detection
        baseline_payload, baseline_issues = load_rolling_baseline(
            history_path=baseline_history_path,
            window=int(args.baseline_window),
        )
        if baseline_issues:
            fallback_payload, fallback_issues = _load_regression_baseline(
                baseline_path,
                allow_missing=bool(args.allow_missing_baseline),
            )
            if fallback_payload:
                baseline_payload = fallback_payload
            baseline_issues.extend(fallback_issues)
        else:
            freshness_ok, freshness_issue = baseline_freshness_check(
                baseline=baseline_payload,
                max_age_hours=float(args.baseline_max_age_hours),
            )
            if not freshness_ok:
                baseline_issues.append(freshness_issue)
                if args.fail_on_stale_baseline:
                    results["regression"]["ok"] = False
                    results["regression"]["issues"].append(freshness_issue)

        current_snapshot, snapshot_issues = _build_current_snapshot(
            metrics_csv=metrics_csv,
            experiment_table_md=table_md,
            parity_report=parity_report,
        )
        if snapshot_issues:
            results["regression"]["ok"] = False
            results["regression"]["issues"].extend(snapshot_issues)

        baseline_payload_legacy, _ = _load_regression_baseline(
            baseline_path,
            allow_missing=bool(args.allow_missing_baseline),
        )
        if not baseline_payload and baseline_payload_legacy:
            baseline_payload = baseline_payload_legacy
        if baseline_issues and not args.allow_missing_baseline:
            results["regression"]["ok"] = False
            results["regression"]["issues"] = baseline_issues
            regression_summary = {
                "regression_detected": True,
                "regression_summary": "; ".join(baseline_issues),
            }
        elif baseline_issues and args.allow_missing_baseline:
            regression_summary = {
                "regression_detected": False,
                "regression_summary": "baseline bootstrap mode (allowed missing baseline)",
            }
        else:
            reg_ok, reg_issues, regression_summary = _regression_check(
                baseline=baseline_payload,
                current_snapshot=current_snapshot,
                max_regression_pct=float(args.max_regression_pct),
                max_size_drift_pct=float(args.max_output_size_drift_pct),
            )
            if not reg_ok:
                results["regression"]["ok"] = False
                results["regression"]["issues"].extend(reg_issues)

        # Persist latest baseline snapshot for subsequent runs.
        baseline_out = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            **current_snapshot,
        }
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(baseline_out, indent=2, sort_keys=True), encoding="utf-8")
        append_rolling_baseline_history(history_path=baseline_history_path, snapshot=baseline_out)

    except Exception as exc:
        results["execution"]["ok"] = False
        results["execution"]["issues"].append(str(exc))

    overall_pass = all(bool(entry["ok"]) for entry in results.values())
    passed_count = sum(1 for entry in results.values() if entry["ok"])
    system_health_score = round((passed_count / len(results)) * 100.0, 2)

    top_issue = ""
    for section, payload in results.items():
        if not payload["ok"] and payload["issues"]:
            top_issue = payload["issues"][0]
            break
    diagnosis = {}
    if not overall_pass:
        failure_stage = next((name for name, payload in results.items() if not payload["ok"]), "unknown")
        diagnosis = diagnose_failure(
            {
                "failure_type": (
                    "schema_mismatch"
                    if failure_stage == "schema"
                    else "artifact_validation"
                    if failure_stage == "artifacts"
                    else "parity_failure"
                    if failure_stage == "data_consistency"
                    else "regression_warning"
                    if failure_stage == "regression"
                    else "execution_failure"
                ),
                "component": failure_stage,
                "stage": failure_stage,
                "likely_cause": top_issue,
                "artifact_path": str((demo_output_root / "metrics_summary.csv")),
                "required_columns": REQUIRED_METRICS_COLUMNS,
            }
        )
        write_health_failure_report(
            health_output_root / "health_failure_report.md",
            diagnosis,
            {
                "results": results,
                "system_health_score": system_health_score,
                "regression_summary": regression_summary,
            },
        )

    summary = {
        "schema_version": SYSTEM_HEALTH_SUMMARY_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_pass": overall_pass,
        "system_health_score": system_health_score,
        "debug_confidence_score": diagnosis.get("debug_confidence_score", 1.0 if overall_pass else 0.7),
        "results": results,
        "regression": regression_summary,
        "auto_fix_actions": auto_fix_actions,
        "auto_fix_blocked_actions": auto_fix_blocked_actions,
        "status": "PASS" if overall_pass else "FAIL",
        "stage": "system_health",
        "issues": [top_issue] if top_issue else [],
        "commands": ["python run_system_health_check.py --parity-config configs/parity_test.yaml"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
    }
    validate_system_health_summary_payload(repo_root=ROOT, summary=summary)
    summary_path = health_output_root / "system_health_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    regression_path = health_output_root / "regression_result.json"
    regression_path.write_text(json.dumps(regression_summary, indent=2, sort_keys=True), encoding="utf-8")
    health_log_path = Path(args.health_log).expanduser().resolve()
    health_log_path.parent.mkdir(parents=True, exist_ok=True)
    with health_log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "PASS" if overall_pass else "FAIL",
                    "stage": "system_health",
                    "issues": [top_issue] if top_issue else [],
                    "commands": ["python run_system_health_check.py --parity-config configs/parity_test.yaml"],
                    "system_health_score": system_health_score,
                    "regression_detected": regression_summary.get("regression_detected", False),
                    "correlation_id": correlation_id,
                }
            )
            + "\n"
        )

    print(f"SYSTEM HEALTH: {'PASS' if overall_pass else 'FAIL'}")
    print(f"Execution: {'✅' if results['execution']['ok'] else '❌'}")
    print(f"Artifacts: {'✅' if results['artifacts']['ok'] else '❌'}")
    print(f"Data Consistency: {'✅' if results['data_consistency']['ok'] else '❌'}")
    print(f"Schema: {'✅' if results['schema']['ok'] else '❌'}")
    print(
        f"Regression: {'✅' if results['regression']['ok'] else '⚠️' if results['regression']['issues'] else '✅'}"
    )
    if not overall_pass:
        print(f"Top Issue:\n{top_issue or 'Unknown'}")
        if diagnosis:
            fixes = diagnosis.get("suggested_fixes", [])
            if fixes:
                print(f"Fix Hint:\n{fixes[0]}")
            print(f"Confidence: {diagnosis.get('debug_confidence_score', 0.7)}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
