#!/usr/bin/env python3
"""
Generate a robustness comparison table from defense_eval_matrix run outputs.

Reads all <model>__<attack>__<defense>/ run directories and produces:
  - robustness_table.csv   — machine-readable, one row per run
  - robustness_table.md    — markdown table for reports and demos

Derived metrics:
  attack_effectiveness = (baseline_mAP50 - mAP50) / baseline_mAP50
      Fraction of baseline mAP50 lost to the attack. 0 = no effect, 1 = total degradation.
  defense_recovery = (defended_mAP50 - attack_mAP50) / (baseline_mAP50 - attack_mAP50)
      Fraction of the attack-induced loss recovered by the defense.
      1.0 = full recovery, 0.0 = no recovery. Null when baseline ≈ attack (< 0.001 delta).

Usage:
  python scripts/generate_robustness_table.py
  python scripts/generate_robustness_table.py --runs-root outputs/defense_eval --output-root outputs/reports
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def _parse_run_name(name: str) -> tuple[str, str, str] | None:
    """Parse <model>__<attack>__<defense> convention. Returns None if format doesn't match."""
    parts = name.split("__")
    if len(parts) < 2:
        return None
    model = parts[0]
    attack = parts[1]
    defense = parts[2] if len(parts) > 2 else "none"
    return model, attack, defense


def _extract_metrics(run_dir: Path) -> dict[str, float | None]:
    metrics = _read_json(run_dir / "metrics.json")
    validation = metrics.get("validation", {})
    return {
        "mAP50": _to_float(validation.get("mAP50")),
        "mAP50_95": _to_float(validation.get("mAP50-95")),
        "precision": _to_float(validation.get("precision")),
        "recall": _to_float(validation.get("recall")),
    }


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round(value: float | None, decimals: int = 3) -> str:
    if value is None:
        return ""
    return str(round(value, decimals))


def collect_runs(runs_root: Path) -> list[dict[str, Any]]:
    rows = []
    for run_dir in sorted(runs_root.iterdir()):
        if not run_dir.is_dir():
            continue
        parsed = _parse_run_name(run_dir.name)
        if parsed is None:
            continue
        model, attack, defense = parsed
        m = _extract_metrics(run_dir)
        rows.append({
            "run_name": run_dir.name,
            "model": model,
            "attack": attack,
            "defense": defense,
            "mAP50": m["mAP50"],
            "mAP50_95": m["mAP50_95"],
            "precision": m["precision"],
            "recall": m["recall"],
        })
    return rows


def compute_derived_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Build baseline index: (model,) → mAP50
    baselines: dict[str, float] = {}
    for row in rows:
        if row["attack"] == "none" and row["defense"] == "none":
            if row["mAP50"] is not None:
                baselines[row["model"]] = row["mAP50"]

    # Build attack index: (model, attack) → best mAP50 with defense=none
    attack_results: dict[tuple[str, str], float] = {}
    for row in rows:
        if row["defense"] == "none" and row["attack"] != "none":
            if row["mAP50"] is not None:
                attack_results[(row["model"], row["attack"])] = row["mAP50"]

    enriched = []
    for row in rows:
        row = dict(row)
        model = row["model"]
        attack = row["attack"]
        mAP50 = row["mAP50"]
        baseline = baselines.get(model)

        # attack_effectiveness: only meaningful for attack rows (defense=none, attack!=none)
        if attack == "none" or row["defense"] != "none":
            row["attack_effectiveness"] = None
        elif baseline is not None and mAP50 is not None and baseline > 0:
            row["attack_effectiveness"] = (baseline - mAP50) / baseline
        else:
            row["attack_effectiveness"] = None

        # defense_recovery: only meaningful for defense rows (defense!=none)
        if row["defense"] == "none":
            row["defense_recovery"] = None
        else:
            attack_mAP50 = attack_results.get((model, attack))
            if (
                baseline is not None
                and attack_mAP50 is not None
                and mAP50 is not None
                and abs(baseline - attack_mAP50) > 0.001
            ):
                row["defense_recovery"] = (mAP50 - attack_mAP50) / (baseline - attack_mAP50)
            else:
                row["defense_recovery"] = None

        enriched.append(row)

    return enriched


_CSV_FIELDS = [
    "model", "attack", "defense",
    "mAP50", "mAP50_95", "precision", "recall",
    "attack_effectiveness", "defense_recovery",
]


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _round(row.get(k)) if isinstance(row.get(k), float) else (row.get(k) or "") for k in _CSV_FIELDS})


def write_markdown(rows: list[dict[str, Any]], output_path: Path) -> None:
    header = "| model | attack | defense | mAP50 | precision | recall | attack_eff | def_recovery |"
    separator = "|-------|--------|---------|-------|-----------|--------|------------|--------------|"
    lines = [header, separator]
    for row in rows:
        lines.append(
            f"| {row['model']} "
            f"| {row['attack']} "
            f"| {row['defense']} "
            f"| {_round(row.get('mAP50'))} "
            f"| {_round(row.get('precision'))} "
            f"| {_round(row.get('recall'))} "
            f"| {_round(row.get('attack_effectiveness'))} "
            f"| {_round(row.get('defense_recovery'))} |"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate robustness comparison table from run outputs.")
    parser.add_argument(
        "--runs-root",
        default="outputs/defense_eval_matrix",
        help="Root directory containing <model>__<attack>__<defense> run folders.",
    )
    parser.add_argument(
        "--output-root",
        default="outputs/reports",
        help="Directory where robustness_table.csv and robustness_table.md are written.",
    )
    args = parser.parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()

    if not runs_root.is_dir():
        raise FileNotFoundError(f"runs-root not found: {runs_root}")

    rows = collect_runs(runs_root)
    if not rows:
        print(f"No valid run directories found under {runs_root}")
        return

    rows = compute_derived_metrics(rows)

    csv_path = output_root / "robustness_table.csv"
    md_path = output_root / "robustness_table.md"
    write_csv(rows, csv_path)
    write_markdown(rows, md_path)

    print(f"Runs processed: {len(rows)}")
    print(f"CSV:      {csv_path}")
    print(f"Markdown: {md_path}")
    print()

    # Print a quick console summary
    print(f"{'model':<12} {'attack':<12} {'defense':<20} {'mAP50':>6} {'atk_eff':>8} {'def_rec':>8}")
    print("-" * 72)
    for row in rows:
        print(
            f"{row['model']:<12} {row['attack']:<12} {row['defense']:<20} "
            f"{_round(row.get('mAP50')):>6} "
            f"{_round(row.get('attack_effectiveness')):>8} "
            f"{_round(row.get('defense_recovery')):>8}"
        )


if __name__ == "__main__":
    main()
