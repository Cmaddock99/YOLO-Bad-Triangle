#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lab.health_checks import (
    latest_rows_by_run,
    load_csv_rows,
    log_event,
    run_metrics_integrity_checks,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sanity-check metrics_summary.csv for stale/mixed rows and flat sweeps."
    )
    parser.add_argument(
        "--csv",
        default="outputs/metrics_summary.csv",
        help="Path to metrics_summary.csv.",
    )
    parser.add_argument(
        "--attack",
        default="fgsm",
        help="Attack name to sanity-check for non-flat sweep behavior.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Metrics CSV not found: {csv_path}")

    rows = load_csv_rows(csv_path=csv_path, require_columns=True)
    if not rows:
        raise ValueError(f"No rows found in metrics CSV: {csv_path}")

    run_metrics_integrity_checks(rows=rows, attack_name=args.attack)
    latest_rows = latest_rows_by_run(rows)

    payload = {
        "status": "ok",
        "csv": str(csv_path),
        "rows_total": len(rows),
        "rows_latest_by_run": len(latest_rows),
        "attack_checked": args.attack,
    }
    print(
        json.dumps(
            payload,
            indent=2,
        )
    )
    log_event(component="metrics-integrity", severity="INFO", message="Metrics integrity PASS")


if __name__ == "__main__":
    main()
