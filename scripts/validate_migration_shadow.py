#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


KEY_COLUMNS = ("run_name", "MODEL", "attack", "defense")
METRIC_COLUMNS = ("precision", "recall", "mAP50", "mAP50-95", "avg_conf")


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(str(row.get(name, "")).strip() for name in KEY_COLUMNS)


def _to_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _abs_metric_delta(a: dict[str, str], b: dict[str, str], metric: str) -> float | None:
    va = _to_float(a.get(metric))
    vb = _to_float(b.get(metric))
    if va is None or vb is None:
        return None
    return abs(va - vb)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare legacy CSV and framework-compatible CSV for shadow migration gate."
    )
    parser.add_argument("--legacy-csv", required=True)
    parser.add_argument("--compat-csv", required=True)
    parser.add_argument(
        "--max-metric-delta",
        type=float,
        default=1e-6,
        help="Maximum acceptable absolute per-metric delta for equivalent rows.",
    )
    args = parser.parse_args()

    legacy_csv = Path(args.legacy_csv).expanduser().resolve()
    compat_csv = Path(args.compat_csv).expanduser().resolve()
    if not legacy_csv.is_file():
        raise FileNotFoundError(f"Legacy CSV not found: {legacy_csv}")
    if not compat_csv.is_file():
        raise FileNotFoundError(f"Compat CSV not found: {compat_csv}")

    legacy_rows = _read_rows(legacy_csv)
    compat_rows = _read_rows(compat_csv)
    legacy_by_key = {_key(row): row for row in legacy_rows}
    compat_by_key = {_key(row): row for row in compat_rows}

    shared = sorted(set(legacy_by_key).intersection(compat_by_key))
    missing_in_compat = sorted(set(legacy_by_key).difference(compat_by_key))
    missing_in_legacy = sorted(set(compat_by_key).difference(legacy_by_key))

    failures: list[str] = []
    max_observed = 0.0
    for key in shared:
        left = legacy_by_key[key]
        right = compat_by_key[key]
        for metric in METRIC_COLUMNS:
            delta = _abs_metric_delta(left, right, metric)
            if delta is None:
                continue
            max_observed = max(max_observed, delta)
            if delta > args.max_metric_delta:
                failures.append(
                    f"{key} metric={metric} delta={delta:.8f} > threshold={args.max_metric_delta:.8f}"
                )

    status = "PASS"
    if missing_in_compat or failures:
        status = "FAIL"

    result = {
        "status": status,
        "legacy_csv": str(legacy_csv),
        "compat_csv": str(compat_csv),
        "legacy_rows": len(legacy_rows),
        "compat_rows": len(compat_rows),
        "shared_keys": len(shared),
        "missing_in_compat": len(missing_in_compat),
        "missing_in_legacy": len(missing_in_legacy),
        "max_observed_metric_delta": max_observed,
        "failure_count": len(failures),
        "sample_failures": failures[:10],
    }
    print(json.dumps(result, indent=2))
    if status == "FAIL":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
