#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.eval import generate_experiment_table


def _save_empty_plot(path: Path, title: str, message: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(title)
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _first_existing_column(df: pd.DataFrame, *candidates: str) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def plot_map50_by_attack(df: pd.DataFrame, output_path: Path) -> None:
    map50_col = _first_existing_column(df, "mAP50", "map50")
    attack_col = _first_existing_column(df, "attack")
    if map50_col is None or attack_col is None:
        _save_empty_plot(
            output_path,
            "mAP50 by attack",
            "Required columns are missing in metrics_summary.csv.",
        )
        return

    frame = df[[attack_col, map50_col]].copy()
    frame["attack"] = frame[attack_col].fillna("unknown").replace("", "unknown")
    frame["map50"] = pd.to_numeric(frame[map50_col], errors="coerce")
    frame = frame.dropna(subset=["map50"])

    if frame.empty:
        _save_empty_plot(
            output_path,
            "mAP50 by attack",
            "No numeric mAP50 values found. Enable validation to collect mAP50 metrics.",
        )
        return

    summary = frame.groupby("attack", as_index=False)["map50"].mean()
    summary = summary.sort_values(by="map50", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(summary["attack"], summary["map50"], color="#1f77b4")
    ax.set_title("Average mAP50 by attack")
    ax.set_xlabel("Attack")
    ax.set_ylabel("mAP50")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_defense_improvement(df: pd.DataFrame, output_path: Path) -> None:
    map50_col = _first_existing_column(df, "mAP50", "map50")
    defense_col = _first_existing_column(df, "defense")
    attack_col = _first_existing_column(df, "attack")
    model_col = _first_existing_column(df, "MODEL", "model")
    if map50_col is None or defense_col is None or attack_col is None or model_col is None:
        _save_empty_plot(
            output_path,
            "Defense improvement",
            "Required columns are missing in metrics_summary.csv.",
        )
        return

    frame = df.copy()
    frame["map50"] = pd.to_numeric(frame[map50_col], errors="coerce")
    frame = frame.dropna(subset=["map50"])
    if frame.empty:
        _save_empty_plot(
            output_path,
            "Defense improvement",
            "No numeric mAP50 values found. Enable validation to collect mAP50 metrics.",
        )
        return

    frame["defense_norm"] = (
        frame[defense_col].fillna("none").replace("", "none").astype(str).str.lower()
    )
    key_columns = [model_col, attack_col]
    for optional_col in ("conf", "iou", "imgsz", "seed"):
        if optional_col in frame.columns:
            key_columns.append(optional_col)

    baseline = frame[frame["defense_norm"] == "none"].copy()
    defended = frame[frame["defense_norm"] != "none"].copy()
    if baseline.empty or defended.empty:
        _save_empty_plot(
            output_path,
            "Defense improvement",
            "Need both baseline (defense=none) and defended runs with mAP50.",
        )
        return

    baseline = (
        baseline.groupby(key_columns, as_index=False)["map50"]
        .mean()
        .rename(columns={"map50": "baseline_map50"})
    )
    defended = defended[key_columns + ["defense_norm", "map50"]]
    merged = defended.merge(baseline, on=key_columns, how="inner")
    if merged.empty:
        _save_empty_plot(
            output_path,
            "Defense improvement",
            "No defended runs could be matched to baseline runs.",
        )
        return

    merged["map50_improvement"] = merged["map50"] - merged["baseline_map50"]
    summary = (
        merged.groupby("defense_norm", as_index=False)["map50_improvement"]
        .mean()
        .sort_values(by="map50_improvement", ascending=False)
    )

    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in summary["map50_improvement"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(summary["defense_norm"], summary["map50_improvement"], color=colors)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Average mAP50 improvement vs baseline defense=none")
    ax.set_xlabel("Defense")
    ax.set_ylabel("mAP50 delta")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate markdown table and plots from metrics_summary.csv."
    )
    parser.add_argument(
        "--input_csv",
        default="outputs/metrics_summary.csv",
        help="Path to metrics_summary.csv file.",
    )
    parser.add_argument(
        "--output_md",
        default="experiment_table.md",
        help="Path for generated markdown experiment table.",
    )
    parser.add_argument(
        "--plots_dir",
        default="outputs/plots",
        help="Directory for generated plot images.",
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_md = Path(args.output_md)
    plots_dir = Path(args.plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    row_count, table_path = generate_experiment_table(
        csv_path=input_csv, markdown_path=output_md
    )
    print(f"Generated table: {table_path} ({row_count} row(s))")

    df = pd.read_csv(input_csv)
    map50_attack_path = plots_dir / "map50_by_attack.png"
    defense_improvement_path = plots_dir / "defense_improvement.png"

    plot_map50_by_attack(df, map50_attack_path)
    plot_defense_improvement(df, defense_improvement_path)

    print(f"Generated plot: {map50_attack_path}")
    print(f"Generated plot: {defense_improvement_path}")


if __name__ == "__main__":
    main()
