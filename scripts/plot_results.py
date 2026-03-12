from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

METRIC_COLUMNS = ["precision", "recall", "mAP50", "mAP50-95"]


def resolve_metrics_csv() -> Path:
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


def main() -> None:
    metrics_file = resolve_metrics_csv()
    print(f"Using metrics CSV: {metrics_file}")

    df = pd.read_csv(metrics_file)
    print(f"Loaded {len(df)} rows.")
    print("DataFrame columns:")
    print(list(df.columns))

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
        ax = map50_df.plot(kind="bar", x="attack", y="mAP50", legend=False, figsize=(10, 5))
        ax.set_title("Attack Impact on YOLO Detection (mAP50)")
        ax.set_ylabel("mAP50")
        ax.set_xlabel("Attack Type")
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
            ax = pr_df.plot(kind="bar", x="attack", y=pr_metrics, figsize=(10, 5))
            ax.set_title("Precision vs Recall by Attack")
            ax.set_ylabel("Score")
            ax.set_xlabel("Attack")
            plt.tight_layout()
            plt.savefig(pr_path)
            plt.close()
            print(f"Saved plot: {pr_path} (metrics: {', '.join(pr_metrics)})")

    print(f"\nPlot output directory: {plots_dir}")


if __name__ == "__main__":
    main()
