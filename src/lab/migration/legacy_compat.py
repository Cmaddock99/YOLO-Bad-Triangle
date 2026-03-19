from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lab.eval.experiment_table import generate_experiment_table
from lab.reporting import discover_framework_runs


@dataclass
class LegacyCompatResult:
    row_count: int
    metrics_csv: Path
    experiment_table_md: Path


_FIELDNAMES = [
    "date",
    "commit",
    "branch",
    "run_name",
    "MODEL",
    "attack",
    "defense",
    "conf",
    "iou",
    "imgsz",
    "seed",
    "images_with_detections",
    "total_detections",
    "avg_conf",
    "median_conf",
    "p25_conf",
    "p75_conf",
    "precision",
    "recall",
    "mAP50",
    "mAP50-95",
    "row_status",
    "missing_metric_fields",
    "error_reason",
    "validation_reason",
    "run_session_id",
    "run_started_at_utc",
    "validation_enabled",
    "validation_data_yaml",
    "validation_labels_dir",
    "transformed_source_dir",
    "transformed_image_count",
    "config_fingerprint",
    "attack_params_json",
    "defense_params_json",
]


def _read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_prediction_quantiles(run_dir: Path) -> tuple[float | None, float | None, float | None]:
    metrics = _read_json_mapping(run_dir / "metrics.json")
    confidence = metrics.get("predictions", {}).get("confidence", {})
    return (
        _to_optional_float(confidence.get("median")),
        _to_optional_float(confidence.get("p25")),
        _to_optional_float(confidence.get("p75")),
    )


def _to_optional_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _row_status(
    *,
    precision: float | None,
    recall: float | None,
    map50: float | None,
    map50_95: float | None,
    validation_status: str,
) -> tuple[str, str]:
    missing = []
    if precision is None:
        missing.append("precision")
    if recall is None:
        missing.append("recall")
    if map50 is None:
        missing.append("mAP50")
    if map50_95 is None:
        missing.append("mAP50-95")
    if missing:
        return "partial", ",".join(missing)
    if validation_status.lower() not in {"ok", "enabled"}:
        return "partial", ""
    return "ok", ""


def write_legacy_compat_artifacts(
    *,
    runs_root: Path,
    output_root: Path,
    conf_default: float = 0.25,
    iou_default: float = 0.7,
    imgsz_default: int = 640,
) -> LegacyCompatResult:
    records = discover_framework_runs(runs_root)
    metrics_csv = output_root / "metrics_summary.csv"
    table_md = output_root / "experiment_table.md"
    output_root.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for record in records:
        run_summary = _read_json_mapping(record.run_dir / "run_summary.json")
        run_meta = run_summary.get("run", {})
        validation_meta = run_summary.get("validation", {})
        attack_meta = run_summary.get("attack", {})
        defense_meta = run_summary.get("defense", {})
        model_meta = run_summary.get("model", {})
        med_conf, p25_conf, p75_conf = _read_prediction_quantiles(record.run_dir)
        status, missing_metric_fields = _row_status(
            precision=record.precision,
            recall=record.recall,
            map50=record.map50,
            map50_95=record.map50_95,
            validation_status=record.validation_status,
        )

        rows.append(
            {
                "date": now_iso,
                "commit": "",
                "branch": "",
                "run_name": record.run_name,
                "MODEL": record.model or str(model_meta.get("name", "")),
                "attack": record.attack,
                "defense": record.defense,
                "conf": _to_optional_float(run_meta.get("conf", conf_default)) or conf_default,
                "iou": _to_optional_float(run_meta.get("iou", iou_default)) or iou_default,
                "imgsz": int(run_meta.get("imgsz", imgsz_default) or imgsz_default),
                "seed": record.seed,
                "images_with_detections": record.images_with_detections,
                "total_detections": record.total_detections,
                "avg_conf": record.avg_confidence,
                "median_conf": med_conf,
                "p25_conf": p25_conf,
                "p75_conf": p75_conf,
                "precision": record.precision,
                "recall": record.recall,
                "mAP50": record.map50,
                "mAP50-95": record.map50_95,
                "row_status": status,
                "missing_metric_fields": missing_metric_fields,
                "error_reason": "",
                "validation_reason": "" if validation_meta.get("enabled") else "validation_disabled",
                "run_session_id": str(run_meta.get("session_id", "")),
                "run_started_at_utc": str(run_meta.get("started_at_utc", "")),
                "validation_enabled": str(bool(validation_meta.get("enabled", False))).lower(),
                "validation_data_yaml": str(validation_meta.get("data_yaml", "")),
                "validation_labels_dir": str(validation_meta.get("labels_dir", "")),
                "transformed_source_dir": str(run_summary.get("transformed_source_dir", "")),
                "transformed_image_count": int(run_summary.get("transformed_image_count", 0) or 0),
                "config_fingerprint": str(run_summary.get("config_fingerprint", "")),
                "attack_params_json": json.dumps(attack_meta.get("params", {}), sort_keys=True),
                "defense_params_json": json.dumps(defense_meta.get("params", {}), sort_keys=True),
            }
        )

    with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in _FIELDNAMES})

    generate_experiment_table(csv_path=metrics_csv, markdown_path=table_md)
    return LegacyCompatResult(
        row_count=len(rows),
        metrics_csv=metrics_csv,
        experiment_table_md=table_md,
    )
