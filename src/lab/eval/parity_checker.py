from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any


_FLOAT_TOLERANCE = 1e-6


def _to_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_last_legacy_row(csv_path: Path) -> dict[str, str]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"legacy metrics CSV not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if row]
    if not rows:
        raise ValueError(f"legacy metrics CSV has no rows: {csv_path}")
    return rows[-1]


def _load_framework_metrics(metrics_json_path: Path) -> dict[str, Any]:
    if not metrics_json_path.is_file():
        raise FileNotFoundError(f"framework metrics.json not found: {metrics_json_path}")
    payload = json.loads(metrics_json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"framework metrics payload is not a mapping: {metrics_json_path}")
    return payload


def _load_prediction_stats(predictions_jsonl_path: Path) -> dict[str, float | int | None]:
    if not predictions_jsonl_path.is_file():
        raise FileNotFoundError(f"framework predictions.jsonl not found: {predictions_jsonl_path}")

    image_count = 0
    total_detections = 0
    images_with_detections = 0
    scores: list[float] = []

    with predictions_jsonl_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            image_count += 1
            parsed = json.loads(line)
            boxes = parsed.get("boxes", [])
            box_count = len(boxes) if isinstance(boxes, list) else 0
            total_detections += box_count
            if box_count > 0:
                images_with_detections += 1
            raw_scores = parsed.get("scores", [])
            if isinstance(raw_scores, list):
                for raw_score in raw_scores:
                    score = _to_optional_float(raw_score)
                    if score is not None:
                        scores.append(score)

    return {
        "image_count": image_count,
        "images_with_detections": images_with_detections,
        "total_detections": total_detections,
        "avg_conf": (sum(scores) / len(scores)) if scores else None,
        "median_conf": float(median(scores)) if scores else None,
    }


def _relative_delta_pct(legacy_value: float, framework_value: float) -> float | None:
    if legacy_value == 0.0:
        return None
    return ((framework_value - legacy_value) / abs(legacy_value)) * 100.0


def compare(
    legacy_csv: str | Path,
    framework_metrics_json: str | Path,
    predictions_jsonl: str | Path,
) -> dict[str, Any]:
    legacy_csv_path = Path(legacy_csv).expanduser().resolve()
    framework_metrics_path = Path(framework_metrics_json).expanduser().resolve()
    predictions_jsonl_path = Path(predictions_jsonl).expanduser().resolve()

    legacy_row = _read_last_legacy_row(legacy_csv_path)
    framework_metrics = _load_framework_metrics(framework_metrics_path)
    prediction_stats = _load_prediction_stats(predictions_jsonl_path)

    framework_predictions = framework_metrics.get("predictions", {})
    framework_validation = framework_metrics.get("validation", {})
    if not isinstance(framework_predictions, dict):
        framework_predictions = {}
    if not isinstance(framework_validation, dict):
        framework_validation = {}

    metric_pairs = [
        (
            "images_with_detections",
            _to_optional_float(legacy_row.get("images_with_detections")),
            _to_optional_float(prediction_stats.get("images_with_detections")),
            0.0,
        ),
        (
            "total_detections",
            _to_optional_float(legacy_row.get("total_detections")),
            _to_optional_float(prediction_stats.get("total_detections")),
            0.0,
        ),
        (
            "avg_conf",
            _to_optional_float(legacy_row.get("avg_conf")),
            _to_optional_float(prediction_stats.get("avg_conf")),
            _FLOAT_TOLERANCE,
        ),
        (
            "median_conf",
            _to_optional_float(legacy_row.get("median_conf")),
            _to_optional_float(prediction_stats.get("median_conf")),
            _FLOAT_TOLERANCE,
        ),
        (
            "precision",
            _to_optional_float(legacy_row.get("precision")),
            _to_optional_float(framework_validation.get("precision")),
            _FLOAT_TOLERANCE,
        ),
        (
            "recall",
            _to_optional_float(legacy_row.get("recall")),
            _to_optional_float(framework_validation.get("recall")),
            _FLOAT_TOLERANCE,
        ),
        (
            "mAP50",
            _to_optional_float(legacy_row.get("mAP50")),
            _to_optional_float(framework_validation.get("mAP50")),
            _FLOAT_TOLERANCE,
        ),
        (
            "mAP50-95",
            _to_optional_float(legacy_row.get("mAP50-95")),
            _to_optional_float(framework_validation.get("mAP50-95")),
            _FLOAT_TOLERANCE,
        ),
    ]

    compared_metrics: list[dict[str, Any]] = []
    fail_count = 0
    compared_count = 0
    worst_metric_delta: dict[str, Any] | None = None

    for metric_name, legacy_value, framework_value, tolerance in metric_pairs:
        if legacy_value is None or framework_value is None:
            compared_metrics.append(
                {
                    "metric": metric_name,
                    "legacy_value": legacy_value,
                    "framework_value": framework_value,
                    "tolerance": tolerance,
                    "status": "SKIP",
                    "delta": None,
                    "relative_delta_pct": None,
                }
            )
            continue

        compared_count += 1
        delta = framework_value - legacy_value
        delta_abs = abs(delta)
        relative_delta_pct = _relative_delta_pct(legacy_value, framework_value)
        status = "PASS" if delta_abs <= tolerance else "FAIL"
        if status == "FAIL":
            fail_count += 1

        metric_result = {
            "metric": metric_name,
            "legacy_value": legacy_value,
            "framework_value": framework_value,
            "tolerance": tolerance,
            "status": status,
            "delta": delta,
            "absolute_delta": delta_abs,
            "relative_delta_pct": relative_delta_pct,
        }
        compared_metrics.append(metric_result)

        if worst_metric_delta is None or delta_abs > float(worst_metric_delta["absolute_delta"]):
            worst_metric_delta = {
                "metric": metric_name,
                "absolute_delta": delta_abs,
                "relative_delta_pct": relative_delta_pct,
            }

    overall_status = "PASS"
    notes: list[str] = []
    if compared_count == 0:
        overall_status = "FAIL"
        notes.append("No comparable parity metrics were available.")
    elif fail_count > 0:
        overall_status = "FAIL"

    framework_summary = {
        "predictions": {
            "image_count_metrics_json": _to_optional_float(framework_predictions.get("image_count")),
            "image_count_predictions_jsonl": _to_optional_float(prediction_stats.get("image_count")),
            "images_with_detections": _to_optional_float(prediction_stats.get("images_with_detections")),
            "total_detections": _to_optional_float(prediction_stats.get("total_detections")),
        },
        "validation_status": framework_validation.get("status"),
    }

    return {
        "overall_status": overall_status,
        "legacy_csv_path": str(legacy_csv_path),
        "framework_metrics_json_path": str(framework_metrics_path),
        "predictions_jsonl_path": str(predictions_jsonl_path),
        "compared_metrics": compared_metrics,
        "compared_metric_count": compared_count,
        "failed_metric_count": fail_count,
        "worst_metric_delta": worst_metric_delta,
        "framework_summary": framework_summary,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
