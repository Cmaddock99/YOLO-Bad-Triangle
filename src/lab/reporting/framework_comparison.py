from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .name_normalization import is_none_like, normalize_name


@dataclass
class FrameworkRunRecord:
    run_name: str
    run_dir: Path
    model: str
    attack: str
    defense: str
    seed: int
    prediction_count: int
    images_with_detections: int
    total_detections: int
    avg_confidence: float | None
    validation_status: str
    precision: float | None
    recall: float | None
    map50: float | None
    map50_95: float | None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _as_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def discover_framework_runs(runs_root: Path) -> list[FrameworkRunRecord]:
    records: list[FrameworkRunRecord] = []
    if not runs_root.exists():
        return records

    for run_dir in sorted(path for path in runs_root.iterdir() if path.is_dir()):
        summary_path = run_dir / "run_summary.json"
        metrics_path = run_dir / "metrics.json"
        if not summary_path.is_file() or not metrics_path.is_file():
            continue

        summary = _read_json(summary_path)
        metrics = _read_json(metrics_path)
        predictions = metrics.get("predictions", {})
        validation = metrics.get("validation", {})

        records.append(
            FrameworkRunRecord(
                run_name=run_dir.name,
                run_dir=run_dir,
                model=str((summary.get("model") or {}).get("name", "")),
                attack=str((summary.get("attack") or {}).get("name", "")),
                defense=str((summary.get("defense") or {}).get("name", "")),
                seed=int(summary.get("seed", 0)),
                prediction_count=int(summary.get("prediction_record_count", 0)),
                images_with_detections=int(predictions.get("images_with_detections", 0)),
                total_detections=int(predictions.get("total_detections", 0)),
                avg_confidence=_as_optional_float((predictions.get("confidence") or {}).get("mean")),
                validation_status=str(validation.get("status", "missing")),
                precision=_as_optional_float(validation.get("precision")),
                recall=_as_optional_float(validation.get("recall")),
                map50=_as_optional_float(validation.get("mAP50")),
                map50_95=_as_optional_float(validation.get("mAP50-95")),
            )
        )

    return records


def _effectiveness(baseline: float | None, attacked: float | None) -> float | None:
    """attack_effectiveness = (baseline - attacked) / baseline"""
    if baseline is None or attacked is None or baseline == 0.0:
        return None
    return (baseline - attacked) / baseline


def _recovery(
    baseline: float | None,
    attacked: float | None,
    defended: float | None,
) -> float | None:
    """defense_recovery = (defended - attacked) / (baseline - attacked)"""
    if baseline is None or attacked is None or defended is None:
        return None
    degradation = baseline - attacked
    if abs(degradation) < 1e-9:
        return None  # no attack effect — recovery is undefined
    return (defended - attacked) / degradation


def write_summary_csv(records: list[FrameworkRunRecord], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_name", "run_dir", "model", "attack", "defense", "seed",
        "prediction_count", "images_with_detections", "total_detections",
        "avg_confidence", "validation_status", "precision", "recall",
        "mAP50", "mAP50-95",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({
                "run_name": record.run_name,
                "run_dir": str(record.run_dir),
                "model": record.model,
                "attack": record.attack,
                "defense": record.defense,
                "seed": record.seed,
                "prediction_count": record.prediction_count,
                "images_with_detections": record.images_with_detections,
                "total_detections": record.total_detections,
                "avg_confidence": record.avg_confidence,
                "validation_status": record.validation_status,
                "precision": record.precision,
                "recall": record.recall,
                "mAP50": record.map50,
                "mAP50-95": record.map50_95,
            })


def build_comparison_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    """Build attack-effectiveness rows: baseline vs each attack (no defense)."""
    # Group by (model, seed) — defense is handled separately
    grouped: dict[tuple[str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, seed), runs in grouped.items():
        baseline = next(
            (r for r in runs if is_none_like(r.attack) and is_none_like(r.defense)),
            None,
        )
        for run in runs:
            if is_none_like(run.attack) or not is_none_like(run.defense):
                continue
            row = {
                "model": model,
                "seed": seed,
                "attack_run": run.run_name,
                "attack": normalize_name(run.attack),
                "baseline_mAP50": baseline.map50 if baseline else None,
                "attack_mAP50": run.map50,
                "mAP50_drop": (
                    (baseline.map50 - run.map50)
                    if baseline and baseline.map50 is not None and run.map50 is not None
                    else None
                ),
                "mAP50_effectiveness": _effectiveness(
                    baseline.map50 if baseline else None,
                    run.map50,
                ),
                "baseline_avg_conf": baseline.avg_confidence if baseline else None,
                "attack_avg_conf": run.avg_confidence,
                "avg_conf_drop": (
                    (baseline.avg_confidence - run.avg_confidence)
                    if baseline
                    and baseline.avg_confidence is not None
                    and run.avg_confidence is not None
                    else None
                ),
                "avg_conf_effectiveness": _effectiveness(
                    baseline.avg_confidence if baseline else None,
                    run.avg_confidence,
                ),
            }
            rows.append(row)
    return rows


def build_defense_recovery_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    """Build defense-recovery rows: baseline → attack → attack+defense triples."""
    grouped: dict[tuple[str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, seed), runs in grouped.items():
        baseline = next(
            (r for r in runs if is_none_like(r.attack) and is_none_like(r.defense)),
            None,
        )
        # Find defended runs (has attack AND has defense)
        defended_runs = [r for r in runs if not is_none_like(r.attack) and not is_none_like(r.defense)]
        for defended in defended_runs:
            # Find matching attack-only run
            attacked = next(
                (r for r in runs
                 if normalize_name(r.attack) == normalize_name(defended.attack)
                 and is_none_like(r.defense)),
                None,
            )
            b_map = baseline.map50 if baseline else None
            a_map = attacked.map50 if attacked else None
            d_map = defended.map50

            b_conf = baseline.avg_confidence if baseline else None
            a_conf = attacked.avg_confidence if attacked else None
            d_conf = defended.avg_confidence

            row = {
                "model": model,
                "seed": seed,
                "attack": normalize_name(defended.attack),
                "defense": normalize_name(defended.defense),
                "defended_run": defended.run_name,
                "baseline_mAP50": b_map,
                "attack_mAP50": a_map,
                "defended_mAP50": d_map,
                "mAP50_recovery": _recovery(b_map, a_map, d_map),
                "baseline_avg_conf": b_conf,
                "attack_avg_conf": a_conf,
                "defended_avg_conf": d_conf,
                "avg_conf_recovery": _recovery(b_conf, a_conf, d_conf),
            }
            rows.append(row)
    return rows


def _fmt(value: float | None, decimals: int = 4) -> str:
    return "" if value is None else f"{value:.{decimals}f}"


def _fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value * 100:.1f}%"


def render_markdown_report(records: list[FrameworkRunRecord]) -> str:
    lines = [
        "# Framework Run Comparison Report",
        "",
        f"Total discovered framework runs: **{len(records)}**",
        "",
    ]
    if not records:
        lines.append("No framework runs found.")
        return "\n".join(lines)

    # Run inventory
    lines += [
        "## Run Inventory",
        "",
        "| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for record in records:
        lines.append(
            f"| `{record.run_name}` | `{record.model}` | `{record.attack}` | `{record.defense}` | "
            f"`{record.validation_status}` | {_fmt(record.map50)} | {_fmt(record.avg_confidence)} |"
        )

    # Attack effectiveness
    comparison_rows = build_comparison_rows(records)
    lines += ["", "## Attack Effectiveness", ""]
    if not comparison_rows:
        lines.append("No baseline/attack pairs found.")
    else:
        lines += [
            "| Model | Seed | Attack | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
        for row in comparison_rows:
            lines.append(
                f"| `{row['model']}` | {row['seed']} | `{row['attack']}` | "
                f"{_fmt(row['baseline_mAP50'])} | {_fmt(row['attack_mAP50'])} | "
                f"{_fmt(row['mAP50_drop'])} | {_fmt_pct(row['mAP50_effectiveness'])} |"
            )

    # Defense recovery
    recovery_rows = build_defense_recovery_rows(records)
    lines += ["", "## Defense Recovery", ""]
    if not recovery_rows:
        lines.append("No defended runs found. Run with `--defenses` to enable defense sweep.")
    else:
        lines += [
            "| Model | Attack | Defense | mAP50 attacked | mAP50 defended | Recovery |",
            "|---|---|---|---:|---:|---:|",
        ]
        for row in recovery_rows:
            lines.append(
                f"| `{row['model']}` | `{row['attack']}` | `{row['defense']}` | "
                f"{_fmt(row['attack_mAP50'])} | {_fmt(row['defended_mAP50'])} | "
                f"{_fmt_pct(row['mAP50_recovery'])} |"
            )

    return "\n".join(lines)
