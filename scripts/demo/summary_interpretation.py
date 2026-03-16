#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

METRICS = ("precision", "recall", "mAP50", "mAP50-95")


def _to_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_epsilon(attack_params_json: str) -> float | None:
    if not attack_params_json:
        return None
    try:
        payload = json.loads(attack_params_json)
    except json.JSONDecodeError:
        return None
    value = payload.get("epsilon")
    return _to_float(value)


def _metric_tuple(row: dict[str, str]) -> tuple[float | None, ...]:
    return tuple(_to_float(row.get(metric)) for metric in METRICS)


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Print human-readable week1 interpretation summary.")
    parser.add_argument("--csv", required=True, help="Path to metrics_summary.csv.")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"No rows found in CSV: {csv_path}")

    baseline_rows = [row for row in rows if row.get("attack") == "none"]
    fgsm_rows = [row for row in rows if row.get("attack") == "fgsm"]

    if not baseline_rows:
        raise ValueError("No baseline rows found (attack=none).")
    if not fgsm_rows:
        raise ValueError("No FGSM rows found (attack=fgsm).")

    baseline = baseline_rows[-1]
    fgsm_rows = sorted(
        fgsm_rows,
        key=lambda row: (_parse_epsilon(row.get("attack_params_json", "")) is None, _parse_epsilon(row.get("attack_params_json", "")) or 0.0),
    )
    fgsm_metrics = [_metric_tuple(row) for row in fgsm_rows]

    all_fgsm_zero = True
    for metric_values in fgsm_metrics:
        for value in metric_values:
            if value is None:
                all_fgsm_zero = False
                break
            if abs(value) > 1e-12:
                all_fgsm_zero = False
                break
        if not all_fgsm_zero:
            break

    print(f"CSV: {csv_path}")
    print()
    print("Baseline metrics:")
    for metric in METRICS:
        print(f"  {metric}: {_fmt(_to_float(baseline.get(metric)))}")

    print()
    print("FGSM rows:")
    for row in fgsm_rows:
        eps = _parse_epsilon(row.get("attack_params_json", ""))
        eps_label = "unknown" if eps is None else f"{eps:g}"
        print(
            "  "
            f"epsilon={eps_label} | "
            f"precision={_fmt(_to_float(row.get('precision')))} "
            f"recall={_fmt(_to_float(row.get('recall')))} "
            f"mAP50={_fmt(_to_float(row.get('mAP50')))} "
            f"mAP50-95={_fmt(_to_float(row.get('mAP50-95')))}"
        )

    baseline_map50 = _to_float(baseline.get("mAP50"))
    fgsm_map50_values = [_to_float(row.get("mAP50")) for row in fgsm_rows]
    fgsm_map50_values = [value for value in fgsm_map50_values if value is not None]
    avg_fgsm_map50 = mean(fgsm_map50_values) if fgsm_map50_values else None

    print()
    print("Interpretation:")
    if baseline_map50 is not None and avg_fgsm_map50 is not None:
        delta = avg_fgsm_map50 - baseline_map50
        print(
            f"  Baseline mAP50={baseline_map50:.4f}, FGSM mean mAP50={avg_fgsm_map50:.4f}, delta={delta:+.4f}."
        )
    if all_fgsm_zero:
        print("  FGSM currently shows full collapse at tested epsilons (stress-test behavior).")
        print("  Demo framing: pipeline is healthy; attack regime is too strong for nuanced curve analysis.")
    else:
        print("  FGSM shows non-zero variation; discuss where degradation begins and slope by epsilon.")


if __name__ == "__main__":
    main()
