#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


METRIC_KEYS = ("precision", "recall", "mAP50", "mAP50-95")
PROFILE_DEFAULT_ATTACK = {
    "week1-demo": "fgsm",
    "week1-stress": "fgsm",
    "custom": "fgsm",
}


def _to_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _metric_tuple(row: dict[str, str]) -> tuple[float | None, ...]:
    return tuple(_to_float(row.get(key)) for key in METRIC_KEYS)


def _read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        return list(reader)


def _latest_rows_by_run(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        run_name = row.get("run_name", "")
        if run_name:
            latest[run_name] = row
    return list(latest.values())


def _latest_session_id(rows: list[dict[str, str]]) -> str | None:
    with_session = [
        row
        for row in rows
        if row.get("run_session_id") and row.get("run_started_at_utc")
    ]
    if not with_session:
        return None
    latest = max(with_session, key=lambda row: row.get("run_started_at_utc", ""))
    return latest.get("run_session_id")


def _filter_rows(rows: list[dict[str, str]], *, session_id: str | None) -> list[dict[str, str]]:
    if not session_id:
        return rows
    return [row for row in rows if row.get("run_session_id") == session_id]


def _assert_metrics_present(rows: list[dict[str, str]]) -> None:
    missing = []
    for row in rows:
        values = _metric_tuple(row)
        if any(value is None for value in values):
            missing.append(row.get("run_name", "<unknown>"))
    if missing:
        raise ValueError(
            "Some rows are missing validation metrics; run validation may be stale/disabled: "
            + ", ".join(sorted(set(missing)))
        )


def _assert_fgsm_sweep_not_flat(rows: list[dict[str, str]], *, attack_name: str) -> None:
    fgsm_rows = [row for row in rows if row.get("attack") == attack_name]
    if len(fgsm_rows) < 2:
        raise ValueError(
            f"Need at least two '{attack_name}' rows to check sweep trend, found {len(fgsm_rows)}."
        )

    params = {row.get("attack_params_json", "") for row in fgsm_rows if row.get("attack_params_json")}
    if len(params) < 2:
        raise ValueError(
            f"Need multiple attack param variants for '{attack_name}' sweep, found {len(params)}."
        )

    metric_set = {_metric_tuple(row) for row in fgsm_rows}
    if len(metric_set) == 1:
        only = next(iter(metric_set))
        if any(value not in (0.0, None) for value in only):
            raise ValueError(
                f"All '{attack_name}' sweep rows have identical non-zero metrics; suspicious flat trend."
            )


def _assert_baseline_differs(rows: list[dict[str, str]], *, attack_name: str) -> None:
    baseline_rows = [row for row in rows if row.get("attack") == "none"]
    fgsm_rows = [row for row in rows if row.get("attack") == attack_name]
    if not baseline_rows or not fgsm_rows:
        return

    baseline_metrics = {_metric_tuple(row) for row in baseline_rows}
    fgsm_metrics = {_metric_tuple(row) for row in fgsm_rows}
    if baseline_metrics.intersection(fgsm_metrics) == baseline_metrics:
        raise ValueError(
            f"Baseline and '{attack_name}' metrics are identical across compared rows; check data routing."
        )


def _assert_not_all_zero_fgsm(
    rows: list[dict[str, str]],
    *,
    attack_name: str,
    zero_epsilon: float,
) -> None:
    fgsm_rows = [row for row in rows if row.get("attack") == attack_name]
    if not fgsm_rows:
        return

    def is_all_zero(metric_values: tuple[float | None, ...]) -> bool:
        if any(value is None for value in metric_values):
            return False
        return all(abs(float(value)) <= zero_epsilon for value in metric_values)

    if all(is_all_zero(_metric_tuple(row)) for row in fgsm_rows):
        raise ValueError(
            f"All '{attack_name}' rows have ~zero validation metrics "
            f"(<= {zero_epsilon:g}); FGSM appears fully collapsed."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail if attack sweep metrics look unexpectedly unchanged."
    )
    parser.add_argument("--csv", default="outputs/metrics_summary.csv", help="Path to metrics CSV.")
    parser.add_argument(
        "--profile",
        default="week1-demo",
        help="Run profile name used to determine default attack check target.",
    )
    parser.add_argument("--attack", default=None, help="Attack name to check (overrides profile default).")
    parser.add_argument(
        "--run-session-id",
        default=None,
        help="Optional run_session_id to isolate a single fresh run session.",
    )
    parser.add_argument(
        "--use-latest-session",
        action="store_true",
        help="Auto-select latest run_session_id from CSV when present.",
    )
    parser.add_argument(
        "--fail-on-all-zero-fgsm",
        action="store_true",
        help="Fail when all FGSM rows have approximately zero validation metrics.",
    )
    parser.add_argument(
        "--zero-epsilon",
        type=float,
        default=1e-12,
        help="Absolute tolerance used by --fail-on-all-zero-fgsm (default: 1e-12).",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Metrics CSV not found: {csv_path}")
    rows = _read_rows(csv_path)
    if not rows:
        raise ValueError(f"No rows found in metrics CSV: {csv_path}")

    attack_name = args.attack or PROFILE_DEFAULT_ATTACK.get(args.profile, "fgsm")

    session_id = args.run_session_id
    if args.use_latest_session and not session_id:
        session_id = _latest_session_id(rows)

    latest_rows = _latest_rows_by_run(rows)
    scoped_rows = _filter_rows(latest_rows, session_id=session_id)
    if not scoped_rows:
        raise ValueError("No rows left after applying run-session filter.")

    _assert_metrics_present(scoped_rows)
    _assert_fgsm_sweep_not_flat(scoped_rows, attack_name=attack_name)
    _assert_baseline_differs(scoped_rows, attack_name=attack_name)
    if args.fail_on_all_zero_fgsm:
        _assert_not_all_zero_fgsm(
            scoped_rows,
            attack_name=attack_name,
            zero_epsilon=float(args.zero_epsilon),
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "csv": str(csv_path),
                "rows_total": len(rows),
                "rows_latest_by_run": len(latest_rows),
                "rows_checked": len(scoped_rows),
                "attack_checked": attack_name,
                "profile": args.profile,
                "run_session_id": session_id or "",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
