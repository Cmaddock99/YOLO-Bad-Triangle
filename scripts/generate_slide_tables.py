#!/usr/bin/env python3
"""Generate slide-ready tables from canonical summary artifacts.

This script reads canonical summary artifacts and writes:
  - outputs/report_tables/<run_name>/headline_table.csv
  - outputs/report_tables/<run_name>/attack_defense_matrix.csv
  - outputs/report_tables/<run_name>/per_class_table.csv
  - outputs/report_tables/<run_name>/appendix_table.csv

Primary inputs (from --summary-dir):
  - headline_metrics.csv
  - per_class_vulnerability.csv
  - summary.json
  - warnings.json

Optional provenance inputs:
  - framework_run_summary.csv from --report-dir (or inferred path)
  - run_summary.json / resolved_config.yaml under runs_root inferred from summary.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
import yaml


SENTINEL_MISSING = "MISSING"
SENTINEL_NA = "N/A"
SENTINEL_NULL = "NULL"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt_float(value: float | None, decimals: int = 3) -> str:
    if value is None:
        return SENTINEL_NULL
    return f"{value:.{decimals}f}"


def _fmt_pct(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return SENTINEL_NULL
    return f"{value * 100:.{decimals}f}"


def _nonblank(value: Any, fallback: str = SENTINEL_MISSING) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _derive_git_commit() -> tuple[str, str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        commit = result.stdout.strip()
        if result.returncode == 0 and commit:
            return commit, "current_repo_state_non_authoritative"
    except OSError:
        pass
    return SENTINEL_MISSING, SENTINEL_MISSING


def _discover_run_artifacts(
    runs_root: Path | None,
) -> tuple[list[str], dict[str, dict[str, Any]], dict[str, Path]]:
    run_dirs: list[str] = []
    summaries: dict[str, dict[str, Any]] = {}
    configs: dict[str, Path] = {}
    if runs_root is None or not runs_root.is_dir():
        return run_dirs, summaries, configs
    for run_dir in sorted(path for path in runs_root.iterdir() if path.is_dir()):
        run_dirs.append(run_dir.name)
        summary_path = run_dir / "run_summary.json"
        if summary_path.is_file():
            payload = _read_json(summary_path)
            if payload:
                summaries[run_dir.name] = payload
        resolved_path = run_dir / "resolved_config.yaml"
        if resolved_path.is_file():
            configs[run_dir.name] = resolved_path
    return run_dirs, summaries, configs


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_epsilon(run_summary: dict[str, Any]) -> str:
    attack = run_summary.get("attack")
    if not isinstance(attack, dict):
        return SENTINEL_NA
    params = attack.get("params")
    if not isinstance(params, dict):
        return SENTINEL_NA
    epsilon = params.get("epsilon")
    if epsilon is None:
        epsilon = params.get("eps")
    if epsilon is None:
        return SENTINEL_NA
    return str(epsilon)


def _worst_class_by_attack_run(per_class_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in per_class_rows:
        attack_run = str(row.get("attack_run") or "")
        if not attack_run:
            continue
        drop = _to_float(row.get("detection_drop"))
        if drop is None:
            continue
        current = result.get(attack_run)
        if current is None or drop > float(current["detection_drop"]):
            result[attack_run] = {
                "class_id": row.get("class_id"),
                "class_name": row.get("class_name"),
                "detection_drop": drop,
                "detection_recovery_normalized": _to_float(row.get("detection_recovery_normalized")),
            }
    return result


def _build_headline_table(
    headline_rows: list[dict[str, str]],
    per_class_rows: list[dict[str, str]],
    run_summaries: dict[str, dict[str, Any]],
    run_name: str,
    git_commit: str,
    git_commit_source: str,
) -> list[dict[str, str]]:
    worst_lookup = _worst_class_by_attack_run(per_class_rows)
    output: list[dict[str, str]] = []
    for row in headline_rows:
        attack_run = str(row.get("attack_run") or "")
        worst = worst_lookup.get(attack_run, {})
        summary = run_summaries.get(attack_run, {})
        output.append(
            {
                "run_name": run_name,
                "model": _nonblank(row.get("model")),
                "seed": _nonblank(row.get("seed")),
                "attack": _nonblank(row.get("attack"), fallback=SENTINEL_NA),
                "defense": _nonblank(row.get("defense"), fallback=SENTINEL_NA),
                "attack_run": _nonblank(attack_run),
                "defended_run": _nonblank(row.get("defended_run"), fallback=SENTINEL_NA),
                "epsilon": _extract_epsilon(summary),
                "baseline_total_detections": _nonblank(row.get("baseline_total_detections"), fallback=SENTINEL_NULL),
                "attack_total_detections": _nonblank(row.get("attack_total_detections"), fallback=SENTINEL_NULL),
                "defended_total_detections": _nonblank(row.get("defended_total_detections"), fallback=SENTINEL_NULL),
                "detection_drop_pct": _fmt_pct(_to_float(row.get("detection_drop"))),
                "detection_recovery_pct": _fmt_pct(_to_float(row.get("detection_recovery_normalized"))),
                "baseline_mAP50": _fmt_float(_to_float(row.get("baseline_mAP50"))),
                "attack_mAP50": _fmt_float(_to_float(row.get("attack_mAP50"))),
                "defended_mAP50": _fmt_float(_to_float(row.get("defended_mAP50"))),
                "mAP50_drop": _fmt_float(_to_float(row.get("mAP50_drop"))),
                "mAP50_recovery": _fmt_pct(_to_float(row.get("mAP50_recovery_normalized"))),
                "worst_class": _nonblank(worst.get("class_name"), fallback=SENTINEL_NA),
                "worst_class_drop_pct": _fmt_pct(_to_float(worst.get("detection_drop"))),
                "worst_class_recovery_pct": _fmt_pct(_to_float(worst.get("detection_recovery_normalized"))),
                "validation_status": _nonblank(row.get("validation_status"), fallback=SENTINEL_MISSING),
                "git_commit": git_commit,
                "git_commit_source": git_commit_source,
            }
        )
    return output


def _build_attack_defense_matrix(
    headline_rows: list[dict[str, str]],
    run_summaries: dict[str, dict[str, Any]],
    run_name: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in headline_rows:
        attack_run = str(row.get("attack_run") or "")
        run_summary = run_summaries.get(attack_run, {})
        rows.append(
            {
                "run_name": run_name,
                "model": str(row.get("model") or ""),
                "seed": str(row.get("seed") or ""),
                "attack": str(row.get("attack") or ""),
                "defense": str(row.get("defense") or ""),
                "attack_run": attack_run,
                "defended_run": str(row.get("defended_run") or ""),
                "objective_mode": str(row.get("objective_mode") or ""),
                "target_class": str(row.get("target_class") or ""),
                "attack_roi": str(row.get("attack_roi") or ""),
                "epsilon": _extract_epsilon(run_summary),
                "baseline_mAP50": str(row.get("baseline_mAP50") or ""),
                "attack_mAP50": str(row.get("attack_mAP50") or ""),
                "defended_mAP50": str(row.get("defended_mAP50") or ""),
                "mAP50_drop": str(row.get("mAP50_drop") or ""),
                "mAP50_recovery_normalized": str(row.get("mAP50_recovery_normalized") or ""),
                "baseline_avg_conf": str(row.get("baseline_avg_conf") or ""),
                "attack_avg_conf": str(row.get("attack_avg_conf") or ""),
                "defended_avg_conf": str(row.get("defended_avg_conf") or ""),
                "avg_conf_drop": str(row.get("avg_conf_drop") or ""),
                "avg_conf_recovery_normalized": str(row.get("avg_conf_recovery_normalized") or ""),
                "baseline_total_detections": str(row.get("baseline_total_detections") or ""),
                "attack_total_detections": str(row.get("attack_total_detections") or ""),
                "defended_total_detections": str(row.get("defended_total_detections") or ""),
                "detection_drop": str(row.get("detection_drop") or ""),
                "detection_recovery_normalized": str(row.get("detection_recovery_normalized") or ""),
                "validation_status": str(row.get("validation_status") or ""),
            }
        )
    return rows


def _build_per_class_table(per_class_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in per_class_rows:
        class_id = str(row.get("class_id") or "")
        if not class_id:
            continue
        class_name = str(row.get("class_name") or f"class_{class_id}")
        key = f"{class_id}:{class_name}"
        drop = _to_float(row.get("detection_drop"))
        if drop is None:
            continue
        current = grouped.get(key)
        if current is None or drop > float(current["detection_drop"]):
            grouped[key] = {
                "class_id": class_id,
                "class_name": class_name,
                "attack": row.get("attack") or SENTINEL_NA,
                "attack_run": row.get("attack_run") or SENTINEL_NA,
                "baseline_count": row.get("baseline_count"),
                "attack_count": row.get("attack_count"),
                "defended_count": row.get("defended_count"),
                "detection_drop": drop,
                "detection_recovery_normalized": _to_float(row.get("detection_recovery_normalized")),
            }
    ranked = sorted(
        grouped.values(),
        key=lambda item: float(item["detection_drop"]),
        reverse=True,
    )
    out: list[dict[str, str]] = []
    for idx, item in enumerate(ranked, start=1):
        out.append(
            {
                "rank": str(idx),
                "class_id": str(item["class_id"]),
                "class_name": str(item["class_name"]),
                "attack": _nonblank(item["attack"], fallback=SENTINEL_NA),
                "attack_run": _nonblank(item["attack_run"], fallback=SENTINEL_NA),
                "baseline_count": _nonblank(item.get("baseline_count"), fallback=SENTINEL_NULL),
                "attack_count": _nonblank(item.get("attack_count"), fallback=SENTINEL_NULL),
                "defended_count": _nonblank(item.get("defended_count"), fallback=SENTINEL_NULL),
                "detection_drop": _fmt_float(_to_float(item.get("detection_drop")), decimals=6),
                "detection_recovery_normalized": _fmt_float(
                    _to_float(item.get("detection_recovery_normalized")),
                    decimals=6,
                ),
            }
        )
    return out


def _config_fingerprint(config_paths: list[Path]) -> tuple[str, str]:
    if not config_paths:
        return SENTINEL_MISSING, SENTINEL_MISSING
    hashes: set[str] = set()
    for path in config_paths:
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        hashes.add(digest)
    if not hashes:
        return SENTINEL_MISSING, SENTINEL_MISSING
    if len(hashes) == 1:
        digest = next(iter(hashes))
        return digest[:12], "resolved_config_sha256"
    return "MULTIPLE", "resolved_config_sha256"


def _choose_baseline_summary(run_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    baseline = run_summaries.get("baseline_none")
    if baseline:
        return baseline
    for run_name in sorted(run_summaries):
        payload = run_summaries[run_name]
        attack = payload.get("attack")
        defense = payload.get("defense")
        attack_name = ""
        defense_name = ""
        if isinstance(attack, dict):
            attack_name = str(attack.get("name") or "").strip().lower()
        if isinstance(defense, dict):
            defense_name = str(defense.get("name") or "").strip().lower()
        if attack_name in {"", "none", "identity"} and defense_name in {"", "none", "identity"}:
            return payload
    for run_name in sorted(run_summaries):
        return run_summaries[run_name]
    return {}


def _build_appendix_table(
    *,
    run_name: str,
    summary_dir: Path,
    report_dir: Path | None,
    runs_root: Path | None,
    run_dirs: list[str],
    warning_count: int,
    headline_rows: list[dict[str, str]],
    per_class_rows: list[dict[str, str]],
    framework_rows_count: int,
    run_summaries: dict[str, dict[str, Any]],
    run_configs: dict[str, Path],
    git_commit: str,
    git_commit_source: str,
) -> list[dict[str, str]]:
    source_files = [
        str(summary_dir / "headline_metrics.csv"),
        str(summary_dir / "per_class_vulnerability.csv"),
        str(summary_dir / "summary.json"),
        str(summary_dir / "warnings.json"),
    ]
    if report_dir is not None:
        source_files.append(str(report_dir / "framework_run_summary.csv"))
    if runs_root is not None:
        source_files.append(str(runs_root))

    if run_dirs:
        run_names = run_dirs
    elif run_summaries:
        run_names = sorted(run_summaries.keys())
    else:
        run_names = [run_name]

    rows: list[dict[str, str]] = []
    for run_dir_name in run_names:
        run_summary = run_summaries.get(run_dir_name, {})
        config_path = run_configs.get(run_dir_name)
        config_payload = _read_yaml_mapping(config_path) if config_path is not None else {}

        model_summary = run_summary.get("model") if isinstance(run_summary.get("model"), dict) else {}
        predict_summary = run_summary.get("predict") if isinstance(run_summary.get("predict"), dict) else {}
        validation_summary = (
            run_summary.get("validation")
            if isinstance(run_summary.get("validation"), dict)
            else {}
        )

        model_cfg = config_payload.get("model") if isinstance(config_payload.get("model"), dict) else {}
        predict_cfg = config_payload.get("predict") if isinstance(config_payload.get("predict"), dict) else {}
        validation_cfg = (
            config_payload.get("validation")
            if isinstance(config_payload.get("validation"), dict)
            else {}
        )
        runner_cfg = config_payload.get("runner") if isinstance(config_payload.get("runner"), dict) else {}

        config_fp, config_fp_source = _config_fingerprint(
            [config_path] if config_path is not None else []
        )
        per_row_sources = list(source_files)
        if config_path is not None:
            per_row_sources.append(str(config_path))
        if runs_root is not None:
            run_summary_path = runs_root / run_dir_name / "run_summary.json"
            if run_summary_path.is_file():
                per_row_sources.append(str(run_summary_path))

        rows.append(
            {
                "run_name": run_name,
                "run_dir_name": run_dir_name,
                "summary_dir": str(summary_dir),
                "report_dir": str(report_dir) if report_dir is not None else SENTINEL_MISSING,
                "runs_root": str(runs_root) if runs_root is not None else SENTINEL_MISSING,
                "model": _nonblank(
                    model_summary.get("name", model_cfg.get("name")),
                    fallback=SENTINEL_MISSING,
                ),
                "seed": _nonblank(
                    run_summary.get("seed", runner_cfg.get("seed")),
                    fallback=SENTINEL_MISSING,
                ),
                "dataset": _nonblank(
                    validation_summary.get("dataset", validation_cfg.get("dataset")),
                    fallback=SENTINEL_MISSING,
                ),
                "predict_conf_threshold": _nonblank(
                    predict_summary.get("conf", predict_cfg.get("conf")),
                    fallback=SENTINEL_MISSING,
                ),
                "predict_iou_threshold": _nonblank(
                    predict_summary.get("iou", predict_cfg.get("iou")),
                    fallback=SENTINEL_MISSING,
                ),
                "predict_imgsz": _nonblank(
                    predict_summary.get("imgsz", predict_cfg.get("imgsz")),
                    fallback=SENTINEL_MISSING,
                ),
                "validation_enabled": _nonblank(
                    validation_summary.get("enabled", validation_cfg.get("enabled")),
                    fallback=SENTINEL_MISSING,
                ),
                "input_image_count": _nonblank(
                    run_summary.get("input_image_count"),
                    fallback=SENTINEL_MISSING,
                ),
                "processed_image_count": _nonblank(
                    run_summary.get("processed_image_count"),
                    fallback=SENTINEL_MISSING,
                ),
                "config_fingerprint": config_fp,
                "config_fingerprint_source": config_fp_source,
                "git_commit": git_commit,
                "git_commit_source": git_commit_source,
                "warning_count": str(warning_count),
                "headline_row_count": str(len(headline_rows)),
                "per_class_row_count": str(len(per_class_rows)),
                "framework_run_summary_row_count": str(framework_rows_count),
                "source_files": ";".join(per_row_sources),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        sys.exit(f"ERROR: No rows available for output: {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate slide-ready report tables from summary artifacts.")
    parser.add_argument(
        "--summary-dir",
        required=True,
        type=Path,
        help="Directory containing headline_metrics.csv, per_class_vulnerability.csv, summary.json, warnings.json.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Optional directory containing framework_run_summary.csv (defaults to outputs/framework_reports/<run_name> when present).",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=None,
        help="Optional framework runs root (defaults to summary.json.runs_root when present).",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Run name for output path (defaults to summary dir name).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (defaults to outputs/report_tables/<run_name>).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary_dir = args.summary_dir.expanduser().resolve()
    if not summary_dir.is_dir():
        raise SystemExit(f"ERROR: summary dir not found: {summary_dir}")

    run_name = args.run_name or summary_dir.name
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else (Path("outputs/report_tables") / run_name).resolve()
    )

    headline_path = summary_dir / "headline_metrics.csv"
    per_class_path = summary_dir / "per_class_vulnerability.csv"
    summary_json_path = summary_dir / "summary.json"
    warnings_json_path = summary_dir / "warnings.json"
    required = [headline_path, per_class_path, summary_json_path, warnings_json_path]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"ERROR: required canonical artifact(s) missing: {', '.join(missing)}")

    summary_payload = _read_json(summary_json_path)
    warnings_payload = _read_json(warnings_json_path)
    warning_count = int(warnings_payload.get("warning_count", 0) or 0)

    runs_root: Path | None = None
    if args.runs_root is not None:
        runs_root = args.runs_root.expanduser().resolve()
    else:
        runs_root_raw = summary_payload.get("runs_root")
        if runs_root_raw:
            runs_root = Path(str(runs_root_raw)).expanduser().resolve()

    report_dir: Path | None
    if args.report_dir is not None:
        report_dir = args.report_dir.expanduser().resolve()
    else:
        inferred = Path("outputs/framework_reports") / run_name
        report_dir = inferred.resolve() if inferred.is_dir() else None

    framework_rows_count = 0
    if report_dir is not None:
        framework_summary_path = report_dir / "framework_run_summary.csv"
        if framework_summary_path.is_file():
            framework_rows_count = len(_read_csv(framework_summary_path))

    headline_rows = _read_csv(headline_path)
    per_class_rows = _read_csv(per_class_path)
    run_dirs, run_summaries, run_configs = _discover_run_artifacts(runs_root)
    git_commit, git_commit_source = _derive_git_commit()

    headline_table = _build_headline_table(
        headline_rows,
        per_class_rows,
        run_summaries,
        run_name,
        git_commit,
        git_commit_source,
    )
    matrix_table = _build_attack_defense_matrix(headline_rows, run_summaries, run_name)
    per_class_table = _build_per_class_table(per_class_rows)
    appendix_table = _build_appendix_table(
        run_name=run_name,
        summary_dir=summary_dir,
        report_dir=report_dir,
        runs_root=runs_root,
        run_dirs=run_dirs,
        warning_count=warning_count,
        headline_rows=headline_rows,
        per_class_rows=per_class_rows,
        framework_rows_count=framework_rows_count,
        run_summaries=run_summaries,
        run_configs=run_configs,
        git_commit=git_commit,
        git_commit_source=git_commit_source,
    )

    _write_csv(output_dir / "headline_table.csv", headline_table)
    _write_csv(output_dir / "attack_defense_matrix.csv", matrix_table)
    _write_csv(output_dir / "per_class_table.csv", per_class_table)
    _write_csv(output_dir / "appendix_table.csv", appendix_table)

    print(f"Wrote tables to: {output_dir}")
    print(f"  headline_table.csv ({len(headline_table)} rows)")
    print(f"  attack_defense_matrix.csv ({len(matrix_table)} rows)")
    print(f"  per_class_table.csv ({len(per_class_table)} rows)")
    print(f"  appendix_table.csv ({len(appendix_table)} rows)")


if __name__ == "__main__":
    main()
