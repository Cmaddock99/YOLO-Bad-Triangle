#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _pick_column(df: pd.DataFrame, *candidates: str) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def _build_experiment_label(df: pd.DataFrame) -> pd.Series:
    if "run_name" in df.columns:
        labels = df["run_name"].astype(str)
    else:
        attack = df.get("attack", "unknown").astype(str)
        defense = df.get("defense", "none").astype(str)
        labels = attack + " | " + defense
    return labels


def _save_placeholder_plot(output_path: Path, title: str, message: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")
    ax.set_title(title)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_map50_by_experiment(df: pd.DataFrame, plots_dir: Path) -> None:
    output_path = plots_dir / "map50_by_experiment.png"
    map50_col = _pick_column(df, "mAP50", "map50")
    if map50_col is None:
        print("Warning: metrics file does not contain an mAP50 column. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "mAP50 by experiment",
            "mAP50 column not found in metrics file.",
        )
        return

    chart_df = df.copy()
    chart_df["experiment"] = _build_experiment_label(chart_df)
    chart_df[map50_col] = pd.to_numeric(chart_df[map50_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[map50_col])

    if chart_df.empty:
        print("Warning: metrics file does not contain mAP50 values. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "mAP50 by experiment",
            "No mAP50 values found in metrics file.",
        )
        return

    # Keep one value per experiment for readability when logs include repeated runs.
    chart_df = chart_df.groupby("experiment", as_index=False)[map50_col].mean()
    chart_df = chart_df.sort_values(map50_col, ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(chart_df["experiment"], chart_df[map50_col], color="steelblue")
    ax.set_title("mAP50 by experiment")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("mAP50")
    ax.set_ylim(0, min(1.0, chart_df[map50_col].max() * 1.1))
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_precision_vs_recall(df: pd.DataFrame, plots_dir: Path) -> None:
    output_path = plots_dir / "precision_vs_recall.png"
    precision_col = _pick_column(df, "precision", "mp")
    recall_col = _pick_column(df, "recall", "mr")
    if precision_col is None or recall_col is None:
        print("Warning: precision/recall columns are missing. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Precision vs Recall",
            "Precision/recall columns were not found in metrics file.",
        )
        return

    chart_df = df.copy()
    chart_df["experiment"] = _build_experiment_label(chart_df)
    chart_df[precision_col] = pd.to_numeric(chart_df[precision_col], errors="coerce")
    chart_df[recall_col] = pd.to_numeric(chart_df[recall_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[precision_col, recall_col])

    if chart_df.empty:
        print("Warning: precision/recall values are unavailable. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Precision vs Recall",
            "No precision/recall values found in metrics file.",
        )
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(chart_df[recall_col], chart_df[precision_col], color="darkorange")
    for _, row in chart_df.iterrows():
        ax.annotate(
            row["experiment"],
            (row[recall_col], row[precision_col]),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points",
        )

    ax.set_title("Precision vs Recall")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_defense_improvement(df: pd.DataFrame, plots_dir: Path) -> None:
    output_path = plots_dir / "defense_improvement.png"
    map50_col = _pick_column(df, "mAP50", "map50")
    if map50_col is None:
        print("Warning: metrics file does not contain an mAP50 column. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Defense improvement comparison",
            "mAP50 column not found in metrics file.",
        )
        return

    if "attack" not in df.columns or "defense" not in df.columns:
        print("Warning: attack/defense columns are missing. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Defense improvement comparison",
            "Attack/defense columns were not found in metrics file.",
        )
        return

    chart_df = df.copy()
    chart_df["attack"] = chart_df["attack"].astype(str)
    chart_df["defense"] = chart_df["defense"].astype(str)
    chart_df[map50_col] = pd.to_numeric(chart_df[map50_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[map50_col])
    if chart_df.empty:
        print("Warning: metrics file does not contain mAP50 values. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Defense improvement comparison",
            "No mAP50 values found in metrics file.",
        )
        return

    baseline = (
        chart_df[chart_df["defense"].str.lower() == "none"]
        .groupby("attack", as_index=False)[map50_col]
        .mean()
        .rename(columns={map50_col: "baseline_map50"})
    )

    defended = (
        chart_df[chart_df["defense"].str.lower() != "none"]
        .groupby(["attack", "defense"], as_index=False)[map50_col]
        .mean()
    )

    merged = defended.merge(baseline, on="attack", how="left").dropna(subset=["baseline_map50"])
    if merged.empty:
        print("Warning: no comparable defended vs baseline mAP50 rows found. Saving placeholder plot.")
        _save_placeholder_plot(
            output_path,
            "Defense improvement comparison",
            "No defended rows with matching baseline rows were found.",
        )
        return

    merged["improvement"] = merged[map50_col] - merged["baseline_map50"]
    merged["label"] = merged["attack"] + " + " + merged["defense"]
    merged = merged.sort_values("improvement", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["seagreen" if value >= 0 else "firebrick" for value in merged["improvement"]]
    ax.bar(merged["label"], merged["improvement"], color=colors)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Defense improvement comparison (mAP50 delta)")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("mAP50 improvement vs no defense")
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment visualizations from metrics_summary.csv.")
    parser.add_argument(
        "--input_csv",
        default="outputs/metrics_summary.csv",
        help="Path to metrics_summary.csv file.",
    )
    parser.add_argument(
        "--output_dir",
        default="outputs/plots",
        help="Directory where plots are saved.",
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    if not input_csv.exists():
        raise FileNotFoundError(f"Metrics file not found: {input_csv}")

    plots_dir = Path(args.output_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    metrics_df = pd.read_csv(input_csv)
    _plot_map50_by_experiment(metrics_df, plots_dir)
    _plot_precision_vs_recall(metrics_df, plots_dir)
    _plot_defense_improvement(metrics_df, plots_dir)
    print(f"Saved plots to {plots_dir}")


if __name__ == "__main__":
    main()
