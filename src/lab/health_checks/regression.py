from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


METRIC_KEYS = ("precision", "recall", "mAP50", "mAP50-95")
PROFILE_DEFAULT_ATTACK = {
    "week1-demo": "fgsm",
    "week1-stress": "fgsm",
    "custom": "fgsm",
}

REQUIRED_COLUMNS = {
    "run_name",
    "MODEL",
    "attack",
    "conf",
    "seed",
    "precision",
    "recall",
    "mAP50",
    "mAP50-95",
    "config_fingerprint",
    "attack_params_json",
}


def to_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_tuple(row: dict[str, str]) -> tuple[float | None, ...]:
    return tuple(to_float(row.get(key)) for key in METRIC_KEYS)


def load_csv_rows(*, csv_path: Path, require_columns: bool = False) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        if require_columns:
            missing = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
            if missing:
                raise ValueError(
                    f"Missing required columns in {csv_path}: {', '.join(sorted(missing))}"
                )
        return list(reader)


def latest_rows_by_run(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        run_name = row.get("run_name", "")
        if run_name:
            latest[run_name] = row
    return list(latest.values())


def latest_session_id(rows: list[dict[str, str]]) -> str | None:
    with_session = [
        row
        for row in rows
        if row.get("run_session_id") and row.get("run_started_at_utc")
    ]
    if not with_session:
        return None
    latest = max(with_session, key=lambda row: row.get("run_started_at_utc", ""))
    return latest.get("run_session_id")


def choose_attack_name(*, profile: str, attack: str | None) -> str:
    return attack or PROFILE_DEFAULT_ATTACK.get(profile, "fgsm")


def filter_rows_by_session(rows: list[dict[str, str]], *, session_id: str | None) -> list[dict[str, str]]:
    if not session_id:
        return rows
    return [row for row in rows if row.get("run_session_id") == session_id]


def assert_no_fingerprint_collision(rows: list[dict[str, str]]) -> None:
    by_run: dict[str, set[str]] = {}
    for row in rows:
        run = row.get("run_name", "")
        fp = row.get("config_fingerprint", "")
        if not run:
            continue
        by_run.setdefault(run, set()).add(fp)
    bad = [run for run, fps in by_run.items() if len(fps) > 1]
    if bad:
        raise ValueError(
            "Found run_name entries with multiple config fingerprints "
            f"(stale/mixed rows): {', '.join(sorted(bad))}"
        )


def assert_attack_sweeps_not_flat(rows: list[dict[str, str]], *, attack_name: str) -> None:
    attack_rows = [row for row in rows if row.get("attack") == attack_name]
    if len(attack_rows) < 2:
        return

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in attack_rows:
        key = (row.get("MODEL", ""), row.get("conf", ""), row.get("seed", ""))
        groups.setdefault(key, []).append(row)

    suspicious: list[str] = []
    for key, group in groups.items():
        attack_param_variants = {
            row.get("attack_params_json", "")
            for row in group
            if row.get("attack_params_json")
        }
        if len(attack_param_variants) < 2:
            continue
        metrics = {metric_tuple(row) for row in group}
        if len(metrics) == 1:
            metric = next(iter(metrics))
            all_zero = metric == (0.0, 0.0, 0.0, 0.0)
            if not all_zero:
                suspicious.append(
                    f"model={key[0]} conf={key[1]} seed={key[2]} "
                    f"(flat metrics across {len(attack_param_variants)} attack params)"
                )
    if suspicious:
        raise ValueError(
            "Detected unchanged validation metrics across attack sweep unexpectedly:\n"
            + "\n".join(f"- {line}" for line in suspicious)
        )


def assert_attack_sweep_nonflat_strict(rows: list[dict[str, str]], *, attack_name: str) -> None:
    attack_rows = [row for row in rows if row.get("attack") == attack_name]
    if len(attack_rows) < 2:
        raise ValueError(
            f"Need at least two '{attack_name}' rows to check sweep trend, found {len(attack_rows)}."
        )
    params = {
        row.get("attack_params_json", "")
        for row in attack_rows
        if row.get("attack_params_json")
    }
    if len(params) < 2:
        raise ValueError(
            f"Need multiple attack param variants for '{attack_name}' sweep, found {len(params)}."
        )
    metric_set = {metric_tuple(row) for row in attack_rows}
    if len(metric_set) == 1:
        only = next(iter(metric_set))
        if any(value not in (0.0, None) for value in only):
            raise ValueError(
                f"All '{attack_name}' sweep rows have identical non-zero metrics; suspicious flat trend."
            )


def assert_metrics_present(rows: list[dict[str, str]]) -> None:
    missing = []
    for row in rows:
        values = metric_tuple(row)
        if any(value is None for value in values):
            missing.append(row.get("run_name", "<unknown>"))
    if missing:
        raise ValueError(
            "Some rows are missing validation metrics; run validation may be stale/disabled: "
            + ", ".join(sorted(set(missing)))
        )


def assert_baseline_differs(rows: list[dict[str, str]], *, attack_name: str) -> None:
    baseline_rows = [row for row in rows if row.get("attack") == "none"]
    attack_rows = [row for row in rows if row.get("attack") == attack_name]
    if not baseline_rows or not attack_rows:
        return
    baseline_metrics = {metric_tuple(row) for row in baseline_rows}
    attack_metrics = {metric_tuple(row) for row in attack_rows}
    if baseline_metrics.intersection(attack_metrics) == baseline_metrics:
        raise ValueError(
            f"Baseline and '{attack_name}' metrics are identical across compared rows; check data routing."
        )


def assert_not_all_zero_attack(
    rows: list[dict[str, str]],
    *,
    attack_name: str,
    zero_epsilon: float,
) -> None:
    attack_rows = [row for row in rows if row.get("attack") == attack_name]
    if not attack_rows:
        return

    def _is_all_zero(metric_values: tuple[float | None, ...]) -> bool:
        if any(value is None for value in metric_values):
            return False
        return all(abs(float(value)) <= zero_epsilon for value in metric_values)

    if all(_is_all_zero(metric_tuple(row)) for row in attack_rows):
        raise ValueError(
            f"All '{attack_name}' rows have ~zero validation metrics "
            f"(<= {zero_epsilon:g}); attack appears fully collapsed."
        )


def run_metrics_integrity_checks(*, rows: list[dict[str, str]], attack_name: str) -> None:
    latest_rows = latest_rows_by_run(rows)
    assert_no_fingerprint_collision(latest_rows)
    assert_attack_sweeps_not_flat(latest_rows, attack_name=attack_name)


def run_fgsm_sanity_checks(
    *,
    rows: list[dict[str, str]],
    attack_name: str,
    session_id: str | None,
    fail_on_all_zero_attack: bool,
    zero_epsilon: float,
) -> list[dict[str, str]]:
    latest_rows = latest_rows_by_run(rows)
    scoped_rows = filter_rows_by_session(latest_rows, session_id=session_id)
    if not scoped_rows:
        raise ValueError("No rows left after applying run-session filter.")
    assert_metrics_present(scoped_rows)
    assert_attack_sweep_nonflat_strict(scoped_rows, attack_name=attack_name)
    assert_baseline_differs(scoped_rows, attack_name=attack_name)
    if fail_on_all_zero_attack:
        assert_not_all_zero_attack(
            scoped_rows,
            attack_name=attack_name,
            zero_epsilon=zero_epsilon,
        )
    return scoped_rows


def parity_delta_values(report: dict[str, Any]) -> tuple[float, float]:
    delta_summary = report.get("delta_summary", {})
    if not isinstance(delta_summary, dict):
        raise ValueError("parity report has invalid 'delta_summary' payload")
    detection = abs(float(delta_summary.get("detection_worst_relative_pct") or 0.0))
    confidence = abs(float(delta_summary.get("confidence_worst_relative_pct") or 0.0))
    return detection, confidence


def parity_threshold_failures(
    *,
    returncode: int,
    detection_abs_pct: float,
    confidence_abs_pct: float,
    max_detection_delta_pct: float,
    max_confidence_delta_pct: float,
) -> list[str]:
    failures: list[str] = []
    if returncode != 0:
        failures.append(f"run_shadow_parity returned non-zero exit code: {returncode}")
    if detection_abs_pct > max_detection_delta_pct:
        failures.append(
            f"detection delta {detection_abs_pct:.4f}% exceeds threshold {max_detection_delta_pct:.4f}%"
        )
    if confidence_abs_pct > max_confidence_delta_pct:
        failures.append(
            f"confidence delta {confidence_abs_pct:.4f}% exceeds threshold {max_confidence_delta_pct:.4f}%"
        )
    return failures


def append_rolling_baseline_history(*, history_path: Path, snapshot: dict[str, Any]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot, sort_keys=True) + "\n")


def load_rolling_baseline(*, history_path: Path, window: int) -> tuple[dict[str, Any], list[str]]:
    if not history_path.is_file():
        return {}, [f"rolling baseline history missing: {history_path}"]
    rows: list[dict[str, Any]] = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    if not rows:
        return {}, [f"rolling baseline history empty: {history_path}"]

    recent = rows[-max(window, 1) :]
    keys = [
        "detection_worst_relative_pct",
        "confidence_worst_relative_pct",
        "total_detections",
        "images_with_detections",
        "avg_conf_mean",
        "avg_conf_p25",
        "avg_conf_p50",
        "avg_conf_p75",
        "metrics_summary_size_bytes",
        "experiment_table_size_bytes",
    ]
    averaged: dict[str, Any] = {}
    for key in keys:
        values: list[float] = []
        for row in recent:
            try:
                values.append(float(row.get(key, 0.0)))
            except (TypeError, ValueError):
                continue
        averaged[key] = (sum(values) / len(values)) if values else 0.0
    averaged["generated_at_utc"] = str(recent[-1].get("generated_at_utc", ""))
    averaged["window_size"] = len(recent)
    return averaged, []


def baseline_freshness_check(*, baseline: dict[str, Any], max_age_hours: float) -> tuple[bool, str]:
    stamp = str(baseline.get("generated_at_utc", "")).strip()
    if not stamp:
        return False, "baseline missing generated_at_utc"
    try:
        generated = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return False, f"invalid baseline generated_at_utc: {stamp}"
    age_hours = (datetime.now(timezone.utc) - generated).total_seconds() / 3600.0
    if age_hours > max_age_hours:
        return False, f"baseline stale: age_hours={age_hours:.2f} > max_age_hours={max_age_hours:.2f}"
    return True, ""
