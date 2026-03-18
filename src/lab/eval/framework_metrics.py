from __future__ import annotations

import math
from statistics import median
from typing import Any

from .prediction_schema import PredictionRecord

_VALIDATION_KEYS = ("precision", "recall", "mAP50", "mAP50-95")


def _to_finite_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def sanitize_validation_metrics(raw: dict[str, Any] | None) -> dict[str, float | None]:
    payload = raw or {}
    return {key: _to_finite_float(payload.get(key)) for key in _VALIDATION_KEYS}


def validation_status(metrics: dict[str, float | None]) -> str:
    values = list(metrics.values())
    if all(value is None for value in values):
        return "missing"
    if any(value is None for value in values):
        return "partial"
    return "complete"


def summarize_prediction_metrics(records: list[PredictionRecord]) -> dict[str, Any]:
    image_count = len(records)
    detection_counts = [len(record.get("boxes", [])) for record in records]
    total_detections = sum(detection_counts)
    images_with_detections = sum(1 for count in detection_counts if count > 0)
    images_without_detections = image_count - images_with_detections

    scores: list[float] = []
    for record in records:
        for raw_score in record.get("scores", []):
            score = _to_finite_float(raw_score)
            if score is not None:
                scores.append(score)

    confidence: dict[str, Any] = {
        "count": len(scores),
        "mean": None,
        "median": None,
        "min": None,
        "max": None,
    }
    if scores:
        confidence = {
            "count": len(scores),
            "mean": sum(scores) / len(scores),
            "median": float(median(scores)),
            "min": min(scores),
            "max": max(scores),
        }

    return {
        "image_count": image_count,
        "images_with_detections": images_with_detections,
        "images_without_detections": images_without_detections,
        "total_detections": total_detections,
        "detections_per_image_mean": (total_detections / image_count) if image_count else 0.0,
        "confidence": confidence,
    }
