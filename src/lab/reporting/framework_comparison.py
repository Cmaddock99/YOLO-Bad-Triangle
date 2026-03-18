from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
    except Exception:
        return {}


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


def _as_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def write_summary_csv(records: list[FrameworkRunRecord], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_name",
        "run_dir",
        "model",
        "attack",
        "defense",
        "seed",
        "prediction_count",
        "images_with_detections",
        "total_detections",
        "avg_confidence",
        "validation_status",
        "precision",
        "recall",
        "mAP50",
        "mAP50-95",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
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
                }
            )


def build_comparison_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.defense, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, defense, seed), runs in grouped.items():
        baseline = next((run for run in runs if run.attack == "none"), None)
        for run in runs:
            if run.attack == "none":
                continue
            row = {
                "model": model,
                "defense": defense,
                "seed": seed,
                "baseline_run": baseline.run_name if baseline else "",
                "attack_run": run.run_name,
                "attack": run.attack,
                "baseline_mAP50": baseline.map50 if baseline else None,
                "attack_mAP50": run.map50,
                "mAP50_drop": (
                    (baseline.map50 - run.map50)
                    if baseline and baseline.map50 is not None and run.map50 is not None
                    else None
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
            }
            rows.append(row)
    return rows


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

    lines.extend(
        [
            "## Run Inventory",
            "",
            "| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |",
            "|---|---|---|---|---|---:|---:|",
        ]
    )
    for record in records:
        map50 = "" if record.map50 is None else f"{record.map50:.4f}"
        conf = "" if record.avg_confidence is None else f"{record.avg_confidence:.4f}"
        lines.append(
            f"| `{record.run_name}` | `{record.model}` | `{record.attack}` | `{record.defense}` | "
            f"`{record.validation_status}` | {map50} | {conf} |"
        )

    comparison_rows = build_comparison_rows(records)
    lines.extend(["", "## Baseline vs Attack Deltas", ""])
    if not comparison_rows:
        lines.append("No baseline/attack pairs found in discovered runs.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Model | Defense | Seed | Attack run | Attack | mAP50 drop | Avg conf drop |",
            "|---|---|---:|---|---|---:|---:|",
        ]
    )
    for row in comparison_rows:
        map_drop = "" if row["mAP50_drop"] is None else f"{float(row['mAP50_drop']):.4f}"
        conf_drop = "" if row["avg_conf_drop"] is None else f"{float(row['avg_conf_drop']):.4f}"
        lines.append(
            f"| `{row['model']}` | `{row['defense']}` | {row['seed']} | "
            f"`{row['attack_run']}` | `{row['attack']}` | {map_drop} | {conf_drop} |"
        )
    return "\n".join(lines)
