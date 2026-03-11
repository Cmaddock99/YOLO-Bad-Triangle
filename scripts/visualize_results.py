#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _normalize_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _resolve_column(columns: list[str], aliases: list[str]) -> str | None:
    normalized_lookup = {_normalize_column_name(col): col for col in columns}
    for alias in aliases:
        hit = normalized_lookup.get(_normalize_column_name(alias))
        if hit:
            return hit
    return None


def _warn(message: str) -> None:
    print(f"[visualize_results][WARN] {message}")


def _info(message: str) -> None:
    print(f"[visualize_results][INFO] {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize experiment metrics from CSV.")
    parser.add_argument(
        "--metrics_csv",
        default="outputs/metrics_summary.csv",
        help="Path to metrics_summary.csv",
    )
    parser.add_argument(
        "--output_dir",
        default="outputs/plots",
        help="Directory where plots are written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.metrics_csv)
    output_dir = Path(args.output_dir)

    if not csv_path.is_file():
        _warn(f"Metrics file not found: {csv_path}")
        _warn("Nothing to plot; exiting without error.")
        return 0

    df = pd.read_csv(csv_path)
    columns = list(df.columns)
    _info(f"Detected CSV columns ({len(columns)}): {columns}")

    precision_col = _resolve_column(columns, ["precision", "mp"])
    recall_col = _resolve_column(columns, ["recall", "mr"])
    map50_col = _resolve_column(columns, ["mAP50", "map50", "MAP50"])
    map5095_col = _resolve_column(
        columns,
        ["mAP50-95", "mAP50_95", "map50_95", "MAP50_95", "map"],
    )

    _info(
        "Resolved metric columns: "
        f"precision={precision_col}, recall={recall_col}, "
        f"mAP50={map50_col}, mAP50-95={map5095_col}"
    )

    run_col = _resolve_column(columns, ["run_name", "experiment_name"])
    if run_col is None:
        _warn("Missing run name column (`run_name` or `experiment_name`); using row index.")
        df["_run_label"] = [f"row_{idx}" for idx in df.index]
        run_col = "_run_label"

    output_dir.mkdir(parents=True, exist_ok=True)

    if map50_col is None:
        _warn("No mAP50 column found in metrics file.")
        _warn("Expected one of: mAP50, map50, MAP50 (case-insensitive).")
    else:
        map50_values = pd.to_numeric(df[map50_col], errors="coerce")
        valid_map50 = map50_values.notna()
        if not valid_map50.any():
            _warn(f"Column '{map50_col}' exists, but no numeric mAP50 values were found.")
        else:
            map_df = df.loc[valid_map50, [run_col]].copy()
            map_df["mAP50"] = map50_values.loc[valid_map50]
            plt.figure(figsize=(10, 5))
            plt.bar(map_df[run_col], map_df["mAP50"])
            plt.title("mAP50 by Run")
            plt.xlabel("Run")
            plt.ylabel("mAP50")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            out_path = output_dir / "map50_by_run.png"
            plt.savefig(out_path, dpi=150)
            plt.close()
            _info(f"Wrote {out_path}")

    plot_metrics: list[tuple[str, str]] = []
    for canonical_name, raw_col in [
        ("precision", precision_col),
        ("recall", recall_col),
        ("mAP50", map50_col),
        ("mAP50-95", map5095_col),
    ]:
        if raw_col is None:
            continue
        numeric_values = pd.to_numeric(df[raw_col], errors="coerce")
        if numeric_values.notna().any():
            plot_metrics.append((canonical_name, raw_col))

    if not plot_metrics:
        _warn("No numeric precision/recall/mAP values available for overview plot.")
        _warn("Exiting without error.")
        return 0

    plt.figure(figsize=(11, 5))
    x_values = list(range(len(df)))
    for canonical_name, raw_col in plot_metrics:
        values = pd.to_numeric(df[raw_col], errors="coerce")
        plt.plot(x_values, values, marker="o", label=canonical_name)
    plt.title("Detection Metrics Overview")
    plt.xlabel("Row Index")
    plt.ylabel("Metric Value")
    plt.legend()
    plt.tight_layout()
    overview_path = output_dir / "metrics_overview.png"
    plt.savefig(overview_path, dpi=150)
    plt.close()
    _info(f"Wrote {overview_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
