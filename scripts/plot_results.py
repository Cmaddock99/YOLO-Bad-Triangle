from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.container import BarContainer

METRIC_COLUMNS = ["precision", "recall", "mAP50", "mAP50-95"]


def resolve_metrics_csv(csv_path: str | None = None) -> Path:
    if csv_path:
        explicit = Path(csv_path)
        if not explicit.is_file():
            raise FileNotFoundError(f"CSV not found: {explicit}")
        return explicit

    candidates = [
        Path("results/metrics_summary.csv"),
        Path("outputs/metrics_summary.csv"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No metrics CSV found. Expected one of: "
        + ", ".join(str(path) for path in candidates)
    )


def save_no_data_chart(output_path: Path, title: str, reason: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        f"No valid data\n{reason}",
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def annotate_bars(ax: plt.Axes, *, fmt: str = "{:.3f}") -> None:
    """Write numeric value labels above each bar."""
    label_count = 0
    for container in ax.containers:
        if not isinstance(container, BarContainer):
            continue
        labels: list[str] = []
        for patch in container.patches:
            if patch is None:
                labels.append("")
                continue
            height = patch.get_height()
            if pd.isna(height):
                labels.append("")
            else:
                labels.append(fmt.format(float(height)))
        if labels:
            ax.bar_label(container, labels=labels, padding=2, fontsize=8)
            label_count += len([label for label in labels if label])
    print(f"Added {label_count} bar-value annotations.")


def build_context_suffix(df: pd.DataFrame) -> str:
    parts: list[str] = []
    if "MODEL" in df.columns:
        models = sorted(str(value) for value in df["MODEL"].dropna().unique())
        if models:
            parts.append(f"model={','.join(models)}")
    if "conf" in df.columns:
        confs = sorted(pd.to_numeric(df["conf"], errors="coerce").dropna().unique())
        if len(confs) == 1:
            parts.append(f"conf={confs[0]:.2f}")
        elif confs:
            parts.append(f"conf={min(confs):.2f}-{max(confs):.2f}")
    if "run_name" in df.columns:
        parts.append(f"runs={len(df['run_name'].dropna())}")
    return " | ".join(parts)


def aggregate_by_attack(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Aggregate repeated runs per attack using mean/std for metrics."""
    grouped = df.groupby("attack", dropna=False)
    agg = grouped[metrics].agg(["mean", "std"])
    agg.columns = [f"{metric}_{stat}" for metric, stat in agg.columns]
    agg = agg.reset_index()
    for metric in metrics:
        std_col = f"{metric}_std"
        if std_col in agg.columns:
            agg[std_col] = agg[std_col].fillna(0.0)
    if "MODEL" in df.columns:
        agg["MODEL"] = ",".join(sorted(str(value) for value in df["MODEL"].dropna().unique()))
    if "conf" in df.columns:
        agg["conf"] = pd.to_numeric(df["conf"], errors="coerce").mean()
    agg["run_name"] = grouped.size().reindex(agg["attack"]).values
    return agg


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot experiment metrics from CSV.")
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Optional path to metrics_summary.csv (defaults to auto-detect results/ then outputs/).",
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Aggregate repeated runs by attack and plot mean +/- std error bars.",
    )
    parser.add_argument(
        "--filter-conf",
        type=float,
        default=None,
        help="Optional confidence filter (e.g. --filter-conf 0.5).",
    )
    args = parser.parse_args()

    metrics_file = resolve_metrics_csv(args.csv)
    print(f"Using metrics CSV: {metrics_file}")

    df = pd.read_csv(metrics_file)
    print(f"Loaded {len(df)} rows.")
    print("DataFrame columns:")
    print(list(df.columns))

    if args.filter_conf is not None:
        if "conf" not in df.columns:
            print("WARNING: --filter-conf provided but CSV has no 'conf' column; skipping filter.")
        else:
            before = len(df)
            conf_numeric = pd.to_numeric(df["conf"], errors="coerce")
            df = df[conf_numeric.round(6) == round(float(args.filter_conf), 6)].copy()
            print(
                f"Applied conf filter: conf={args.filter_conf}. "
                f"Rows kept: {len(df)} / {before}"
            )
            if df.empty:
                print("WARNING: No rows matched --filter-conf; plots will be no-data charts.")

    if "attack" not in df.columns:
        print("WARNING: 'attack' column missing. Using run_name as x-axis labels.")
        if "run_name" in df.columns:
            df["attack"] = df["run_name"].astype(str)
        else:
            df["attack"] = [f"row_{idx}" for idx in df.index]

    for metric in METRIC_COLUMNS:
        if metric not in df.columns:
            print(f"WARNING: Metric column '{metric}' missing from CSV; filling with NaN.")
            df[metric] = pd.NA
        df[metric] = pd.to_numeric(df[metric], errors="coerce")

    debug_cols = ["attack"] + METRIC_COLUMNS
    print("\nSelected metrics columns (after numeric coercion):")
    print(df[debug_cols])
    if args.aggregate:
        print("\nAggregate mode enabled: plotting per-attack mean +/- std.")
        df = aggregate_by_attack(df, METRIC_COLUMNS)
        for metric in METRIC_COLUMNS:
            mean_col = f"{metric}_mean"
            std_col = f"{metric}_std"
            if mean_col in df.columns:
                df[metric] = df[mean_col]
            if std_col in df.columns:
                df[f"{metric}_yerr"] = df[std_col]
        print("Aggregated rows:")
        print(df[["attack"] + [f"{metric}_mean" for metric in METRIC_COLUMNS]])
    context_suffix = build_context_suffix(df)
    if context_suffix:
        print(f"Plot context: {context_suffix}")

    plots_dir = metrics_file.parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    valid_counts = {}
    for metric in METRIC_COLUMNS:
        valid_counts[metric] = int(df[metric].notna().sum())
        if valid_counts[metric] == 0:
            print(
                f"WARNING: Metric '{metric}' has 0 valid numeric rows; "
                "its plot data is unavailable."
            )
        else:
            print(f"Metric '{metric}' valid numeric rows: {valid_counts[metric]}")

    # Plot 1: mAP50 by attack
    map50_df = df.dropna(subset=["mAP50"])
    map50_path = plots_dir / "attack_vs_map50.png"
    if map50_df.empty:
        reason = "Metric 'mAP50' is empty or non-numeric for all rows."
        print(f"Skipping data plot for mAP50: {reason}")
        save_no_data_chart(
            output_path=map50_path,
            title="Attack Impact on YOLO Detection (mAP50)",
            reason=reason,
        )
        print(f"Saved no-data chart: {map50_path}")
    else:
        yerr_map50 = map50_df["mAP50_yerr"] if "mAP50_yerr" in map50_df.columns else None
        ax = map50_df.plot(
            kind="bar",
            x="attack",
            y="mAP50",
            yerr=yerr_map50,
            legend=False,
            figsize=(10, 5),
            capsize=4,
        )
        title = "Attack Impact on YOLO Detection (mAP50)"
        if context_suffix:
            title = f"{title}\n{context_suffix}"
        ax.set_title(title)
        ax.set_ylabel("mAP50")
        ax.set_xlabel("Attack Type")
        annotate_bars(ax)
        plt.tight_layout()
        plt.savefig(map50_path)
        plt.close()
        print(f"Saved plot: {map50_path}")

    # Plot 2: precision/recall by attack (plot whichever metrics are valid)
    pr_metrics = [metric for metric in ["precision", "recall"] if valid_counts[metric] > 0]
    pr_path = plots_dir / "precision_recall.png"
    if not pr_metrics:
        reason = "Both 'precision' and 'recall' are empty or non-numeric."
        print(f"Skipping data plot for precision/recall: {reason}")
        save_no_data_chart(
            output_path=pr_path,
            title="Precision vs Recall by Attack",
            reason=reason,
        )
        print(f"Saved no-data chart: {pr_path}")
    else:
        pr_df = df.dropna(subset=pr_metrics)
        if pr_df.empty:
            reason = (
                "No rows contain values for all plotted metrics: "
                + ", ".join(pr_metrics)
            )
            print(f"Skipping data plot for precision/recall: {reason}")
            save_no_data_chart(
                output_path=pr_path,
                title="Precision vs Recall by Attack",
                reason=reason,
            )
            print(f"Saved no-data chart: {pr_path}")
        else:
            yerr_pr = None
            yerr_cols = [f"{metric}_yerr" for metric in pr_metrics]
            if all(col in pr_df.columns for col in yerr_cols):
                yerr_pr = pr_df[yerr_cols]
                yerr_pr.columns = pr_metrics
            ax = pr_df.plot(
                kind="bar",
                x="attack",
                y=pr_metrics,
                yerr=yerr_pr,
                figsize=(10, 5),
                capsize=4,
            )
            title = "Precision vs Recall by Attack"
            if context_suffix:
                title = f"{title}\n{context_suffix}"
            ax.set_title(title)
            ax.set_ylabel("Score")
            ax.set_xlabel("Attack")
            annotate_bars(ax)
            plt.tight_layout()
            plt.savefig(pr_path)
            plt.close()
            print(f"Saved plot: {pr_path} (metrics: {', '.join(pr_metrics)})")

    print(f"\nPlot output directory: {plots_dir}")


if __name__ == "__main__":
    main()
