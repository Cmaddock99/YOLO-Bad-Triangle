#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

METRICS = ["precision", "recall", "mAP50", "mAP50-95"]


def _resolve_latest_week1_csv() -> Path:
    outputs_dir = Path("outputs")
    week1_dirs = sorted(
        [path for path in outputs_dir.iterdir() if path.is_dir() and path.name.startswith("week1_")]
    )
    if not week1_dirs:
        raise FileNotFoundError("No outputs/week1_* directories found.")
    csv_path = week1_dirs[-1] / "metrics_summary.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"Missing metrics_summary.csv in latest week1 dir: {csv_path.parent}")
    return csv_path


def _extract_epsilon(attack_params_json: str) -> float | None:
    if not attack_params_json:
        return None
    try:
        params = json.loads(attack_params_json)
    except json.JSONDecodeError:
        return None
    value = params.get("epsilon")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _prepare_rows(csv_path: Path) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    df = pd.read_csv(csv_path)
    if "attack" not in df.columns:
        raise ValueError("CSV is missing required 'attack' column.")
    for metric in METRICS:
        if metric not in df.columns:
            df[metric] = pd.NA
        df[metric] = pd.to_numeric(df[metric], errors="coerce")

    baseline_rows = df[df["attack"] == "none"].copy()
    fgsm_rows = df[df["attack"] == "fgsm"].copy()
    if baseline_rows.empty or fgsm_rows.empty:
        raise ValueError("Need both baseline ('attack=none') and FGSM ('attack=fgsm') rows.")

    baseline = baseline_rows.iloc[-1]
    if "attack_params_json" not in fgsm_rows.columns:
        raise ValueError("CSV missing 'attack_params_json'; cannot infer FGSM epsilon.")
    fgsm_rows["epsilon"] = fgsm_rows["attack_params_json"].fillna("").map(_extract_epsilon)
    fgsm_rows = fgsm_rows.dropna(subset=["epsilon"]).sort_values("epsilon")
    if fgsm_rows.empty:
        raise ValueError("No FGSM rows with parseable epsilon found in 'attack_params_json'.")
    return df, baseline, fgsm_rows


def _plot_snapshot(csv_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _, baseline, fgsm_rows = _prepare_rows(csv_path)
    created: list[Path] = []

    # Plot 1: Baseline vs FGSM bars for each metric.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes_flat = axes.flatten()
    labels = ["baseline"] + [f"fgsm e={eps:g}" for eps in fgsm_rows["epsilon"].tolist()]
    for idx, metric in enumerate(METRICS):
        ax = axes_flat[idx]
        values = [baseline[metric]] + fgsm_rows[metric].tolist()
        colors = ["#1f77b4"] + ["#d62728"] * len(fgsm_rows)
        bars = ax.bar(labels, values, color=colors)
        ax.set_title(metric)
        ax.set_ylim(0.0, 1.0)
        ax.tick_params(axis="x", rotation=25)
        for bar, value in zip(bars, values):
            if pd.notna(value):
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    float(value) + 0.015,
                    f"{float(value):.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )
    fig.suptitle("Current Week1 Snapshot: Baseline vs FGSM", fontsize=14)
    fig.tight_layout()
    bars_path = output_dir / "baseline-vs-fgsm-metrics.png"
    fig.savefig(bars_path, dpi=160)
    plt.close(fig)
    created.append(bars_path)

    # Plot 2: FGSM epsilon trend lines with baseline reference.
    fig, ax = plt.subplots(figsize=(10, 6))
    x = fgsm_rows["epsilon"]
    for metric in METRICS:
        ax.plot(x, fgsm_rows[metric], marker="o", linewidth=2, label=f"FGSM {metric}")
        baseline_value = baseline[metric]
        if pd.notna(baseline_value):
            ax.axhline(
                y=float(baseline_value),
                linestyle="--",
                linewidth=1.2,
                alpha=0.6,
                label=f"Baseline {metric}",
            )
    ax.set_title("FGSM Epsilon Trend with Baseline References")
    ax.set_xlabel("FGSM epsilon")
    ax.set_ylabel("Metric value")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    trend_path = output_dir / "fgsm-epsilon-trend.png"
    fig.savefig(trend_path, dpi=160)
    plt.close(fig)
    created.append(trend_path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a concise week1 metrics visual snapshot.")
    parser.add_argument(
        "--csv",
        default=None,
        help="Optional path to metrics_summary.csv (defaults to latest outputs/week1_*/metrics_summary.csv).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory for generated plots (defaults to <csv_dir>/plots).",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv) if args.csv else _resolve_latest_week1_csv()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    output_dir = Path(args.output_dir) if args.output_dir else (csv_path.parent / "plots")

    created = _plot_snapshot(csv_path=csv_path, output_dir=output_dir)
    print(f"CSV: {csv_path}")
    for path in created:
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()
