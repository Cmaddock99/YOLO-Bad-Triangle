#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


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


def _to_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        missing = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
        if missing:
            raise ValueError(
                f"Missing required columns in {csv_path}: {', '.join(sorted(missing))}"
            )
        return list(reader)


def _latest_rows_by_run(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        run_name = row.get("run_name", "")
        if run_name:
            latest[run_name] = row
    return list(latest.values())


def _assert_no_fingerprint_collision(rows: list[dict[str, str]]) -> None:
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


def _assert_attack_sweeps_not_flat(rows: list[dict[str, str]], *, attack_name: str) -> None:
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

        metrics = {
            (
                _to_float(row.get("precision")),
                _to_float(row.get("recall")),
                _to_float(row.get("mAP50")),
                _to_float(row.get("mAP50-95")),
            )
            for row in group
        }
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

    rows = _load_rows(csv_path)
    if not rows:
        raise ValueError(f"No rows found in metrics CSV: {csv_path}")

    latest_rows = _latest_rows_by_run(rows)
    _assert_no_fingerprint_collision(latest_rows)
    _assert_attack_sweeps_not_flat(latest_rows, attack_name=args.attack)

    print(
        json.dumps(
            {
                "status": "ok",
                "csv": str(csv_path),
                "rows_total": len(rows),
                "rows_latest_by_run": len(latest_rows),
                "attack_checked": args.attack,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
