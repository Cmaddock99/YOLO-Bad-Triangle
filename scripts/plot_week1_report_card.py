#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

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


def _prepare_data(csv_path: Path) -> tuple[pd.Series, pd.DataFrame, pd.Series, dict[str, Any]]:
    df = pd.read_csv(csv_path)
    for metric in METRICS:
        if metric not in df.columns:
            df[metric] = pd.NA
        df[metric] = pd.to_numeric(df[metric], errors="coerce")

    baseline_rows = df[df["attack"] == "none"].copy()
    fgsm_rows = df[df["attack"] == "fgsm"].copy()
    if baseline_rows.empty or fgsm_rows.empty:
        raise ValueError("Need baseline and FGSM rows in CSV to build report card.")

    baseline = baseline_rows.iloc[-1]
    if "attack_params_json" not in fgsm_rows.columns:
        fgsm_rows["epsilon"] = pd.NA
    else:
        fgsm_rows["epsilon"] = fgsm_rows["attack_params_json"].fillna("").map(_extract_epsilon)
    if fgsm_rows["epsilon"].dropna().empty:
        fgsm_rows = fgsm_rows.copy()
        fgsm_rows["epsilon"] = pd.Series(range(1, len(fgsm_rows) + 1), index=fgsm_rows.index, dtype="float64")
        print(
            "WARNING: No FGSM rows with parseable epsilon found in attack_params_json; "
            "using FGSM row order index for report card rendering."
        )
    fgsm_rows = fgsm_rows.sort_values("epsilon")

    worst_fgsm = fgsm_rows.iloc[-1]
    fgsm_metric_frame = fgsm_rows[METRICS].apply(pd.to_numeric, errors="coerce")
    fgsm_all_zero = bool((fgsm_metric_frame.fillna(1.0).abs() <= 1e-12).all(axis=1).all())
    baseline_metric_values = pd.to_numeric(baseline[METRICS], errors="coerce").fillna(0.0)
    baseline_nonzero = bool((baseline_metric_values > 0.0).all())

    summary = {
        "rows": len(df),
        "session_id": str(df.get("run_session_id", pd.Series([""])).dropna().iloc[-1])
        if "run_session_id" in df.columns and not df["run_session_id"].dropna().empty
        else "",
        "fgsm_count": len(fgsm_rows),
        "fgsm_all_zero": fgsm_all_zero,
        "baseline_nonzero": baseline_nonzero,
    }
    return baseline, fgsm_rows, worst_fgsm, summary


def _badge(ax: plt.Axes, x: float, y: float, text: str, ok: bool) -> None:
    color = "#1a7f37" if ok else "#b42318"
    box = FancyBboxPatch(
        (x, y),
        0.22,
        0.065,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=0,
        facecolor=color,
        alpha=0.95,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    ax.text(
        x + 0.11,
        y + 0.033,
        text,
        ha="center",
        va="center",
        color="white",
        fontsize=10,
        fontweight="bold",
        transform=ax.transAxes,
    )


def _metric_line(
    ax: plt.Axes,
    *,
    y: float,
    label: str,
    baseline: float,
    fgsm: float,
) -> None:
    delta = fgsm - baseline
    ax.text(0.06, y, label, fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.text(0.36, y, f"{baseline:.3f}", fontsize=11, transform=ax.transAxes)
    ax.text(0.56, y, f"{fgsm:.3f}", fontsize=11, transform=ax.transAxes)
    delta_color = "#b42318" if delta < 0 else "#1a7f37"
    ax.text(
        0.79,
        y,
        f"{delta:+.3f}",
        fontsize=11,
        color=delta_color,
        fontweight="bold",
        transform=ax.transAxes,
    )


def _render_report_card(
    *,
    csv_path: Path,
    baseline: pd.Series,
    worst_fgsm: pd.Series,
    summary: dict[str, Any],
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis("off")

    # Background card.
    card = FancyBboxPatch(
        (0.03, 0.06),
        0.94,
        0.88,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        edgecolor="#d0d5dd",
        facecolor="#f8fafc",
        transform=ax.transAxes,
    )
    ax.add_patch(card)

    ax.text(
        0.06,
        0.90,
        "YOLO Week1 Robustness Report Card",
        fontsize=18,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.06,
        0.86,
        f"Source: {csv_path}",
        fontsize=9,
        color="#475467",
        transform=ax.transAxes,
    )
    ax.text(
        0.06,
        0.82,
        f"Rows={summary['rows']} | FGSM runs={summary['fgsm_count']} | Session={summary['session_id'] or 'n/a'}",
        fontsize=10,
        color="#344054",
        transform=ax.transAxes,
    )

    _badge(ax, 0.72, 0.88, "BASELINE OK" if summary["baseline_nonzero"] else "BASELINE FAIL", summary["baseline_nonzero"])
    _badge(ax, 0.72, 0.80, "FGSM COLLAPSE" if summary["fgsm_all_zero"] else "FGSM VARIES", not summary["fgsm_all_zero"])

    ax.text(0.06, 0.73, "Metric", fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.text(0.36, 0.73, "Baseline", fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.56,
        0.73,
        f"Worst FGSM (e={float(worst_fgsm['epsilon']):g})",
        fontsize=11,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(0.79, 0.73, "Delta", fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.plot([0.06, 0.93], [0.715, 0.715], color="#98a2b3", linewidth=1, transform=ax.transAxes)

    y_positions = [0.66, 0.58, 0.50, 0.42]
    for y, metric in zip(y_positions, METRICS):
        baseline_value = float(baseline[metric]) if pd.notna(baseline[metric]) else 0.0
        fgsm_value = float(worst_fgsm[metric]) if pd.notna(worst_fgsm[metric]) else 0.0
        _metric_line(ax, y=y, label=metric, baseline=baseline_value, fgsm=fgsm_value)

    narrative = (
        "Interpretation: baseline metrics are healthy while FGSM rows collapse to zero.\n"
        "This indicates current attack settings are over-saturating model performance,\n"
        "so epsilon calibration is needed before claiming nuanced robustness trends."
    )
    ax.text(0.06, 0.23, narrative, fontsize=11, color="#101828", transform=ax.transAxes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def _render_report_card_by_epsilon(
    *,
    csv_path: Path,
    baseline: pd.Series,
    fgsm_rows: pd.DataFrame,
    summary: dict[str, Any],
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.axis("off")

    card = FancyBboxPatch(
        (0.02, 0.05),
        0.96,
        0.90,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        edgecolor="#d0d5dd",
        facecolor="#f8fafc",
        transform=ax.transAxes,
    )
    ax.add_patch(card)

    ax.text(
        0.05,
        0.91,
        "YOLO Week1 Report Card (Baseline vs Each FGSM Epsilon)",
        fontsize=16,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.05,
        0.875,
        f"Source: {csv_path}",
        fontsize=9,
        color="#475467",
        transform=ax.transAxes,
    )
    ax.text(
        0.05,
        0.845,
        f"Rows={summary['rows']} | FGSM runs={summary['fgsm_count']} | Session={summary['session_id'] or 'n/a'}",
        fontsize=10,
        color="#344054",
        transform=ax.transAxes,
    )

    _badge(
        ax,
        0.73,
        0.885,
        "BASELINE OK" if summary["baseline_nonzero"] else "BASELINE FAIL",
        summary["baseline_nonzero"],
    )
    _badge(
        ax,
        0.73,
        0.81,
        "FGSM COLLAPSE" if summary["fgsm_all_zero"] else "FGSM VARIES",
        not summary["fgsm_all_zero"],
    )

    epsilon_rows = fgsm_rows.sort_values("epsilon")
    epsilon_labels = [f"e={float(eps):g}" for eps in epsilon_rows["epsilon"].tolist()]
    columns = ["Metric", "Baseline", *epsilon_labels]
    x_positions = [0.05, 0.30]
    if epsilon_labels:
        start_x = 0.48
        usable_width = 0.47
        step = usable_width / max(len(epsilon_labels), 1)
        x_positions.extend([start_x + idx * step for idx in range(len(epsilon_labels))])

    header_y = 0.74
    for x, col in zip(x_positions, columns):
        ax.text(x, header_y, col, fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.plot([0.05, 0.95], [header_y - 0.02, header_y - 0.02], color="#98a2b3", linewidth=1, transform=ax.transAxes)

    row_ys = [0.66, 0.58, 0.50, 0.42]
    for metric, y in zip(METRICS, row_ys):
        baseline_val = float(baseline[metric]) if pd.notna(baseline[metric]) else 0.0
        ax.text(x_positions[0], y, metric, fontsize=11, fontweight="bold", transform=ax.transAxes)
        ax.text(x_positions[1], y, f"{baseline_val:.3f}", fontsize=11, transform=ax.transAxes)
        for idx, (_, fgsm_row) in enumerate(epsilon_rows.iterrows()):
            fgsm_val = float(fgsm_row[metric]) if pd.notna(fgsm_row[metric]) else 0.0
            delta = fgsm_val - baseline_val
            cell_text = f"{fgsm_val:.3f}\n({delta:+.3f})"
            cell_color = "#b42318" if delta < 0 else "#1a7f37"
            ax.text(
                x_positions[2 + idx],
                y,
                cell_text,
                fontsize=10,
                color=cell_color,
                transform=ax.transAxes,
                ha="left",
            )

    narrative = (
        "Each FGSM epsilon column shows absolute metric and delta vs baseline in parentheses.\n"
        "Use this slide to discuss where degradation starts and whether effects are monotonic."
    )
    ax.text(0.05, 0.23, narrative, fontsize=10.5, color="#101828", transform=ax.transAxes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a one-page week1 robustness report card image.")
    parser.add_argument(
        "--csv",
        default=None,
        help="Optional metrics_summary.csv path. Defaults to latest outputs/week1_*/metrics_summary.csv.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional PNG output path. Defaults to <csv_dir>/plots/robustness-report-card.png.",
    )
    parser.add_argument(
        "--variant",
        choices=["worst", "by-epsilon", "both"],
        default="both",
        help="Report variant to render.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv) if args.csv else _resolve_latest_week1_csv()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    baseline, fgsm_rows, worst_fgsm, summary = _prepare_data(csv_path)

    if args.variant == "worst":
        output_path = (
            Path(args.output)
            if args.output
            else csv_path.parent / "plots" / "robustness-report-card.png"
        )
        _render_report_card(
            csv_path=csv_path,
            baseline=baseline,
            worst_fgsm=worst_fgsm,
            summary=summary,
            output_path=output_path,
        )
        print(f"Wrote: {output_path}")
        return

    if args.variant == "by-epsilon":
        output_path = (
            Path(args.output)
            if args.output
            else csv_path.parent / "plots" / "robustness-report-card-by-epsilon.png"
        )
        _render_report_card_by_epsilon(
            csv_path=csv_path,
            baseline=baseline,
            fgsm_rows=fgsm_rows,
            summary=summary,
            output_path=output_path,
        )
        print(f"Wrote: {output_path}")
        return

    # variant=both
    output_worst = (
        Path(args.output)
        if args.output
        else csv_path.parent / "plots" / "robustness-report-card.png"
    )
    _render_report_card(
        csv_path=csv_path,
        baseline=baseline,
        worst_fgsm=worst_fgsm,
        summary=summary,
        output_path=output_worst,
    )
    output_by_epsilon = csv_path.parent / "plots" / "robustness-report-card-by-epsilon.png"
    _render_report_card_by_epsilon(
        csv_path=csv_path,
        baseline=baseline,
        fgsm_rows=fgsm_rows,
        summary=summary,
        output_path=output_by_epsilon,
    )
    print(f"Wrote: {output_worst}")
    print(f"Wrote: {output_by_epsilon}")


if __name__ == "__main__":
    main()
