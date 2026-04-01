from __future__ import annotations

from statistics import median
from typing import Any

from .coco_labels import COCO_CLASS_NAMES
from .derived_metrics import to_finite_float
from .prediction_schema import PredictionRecord

_VALIDATION_KEYS = ("precision", "recall", "mAP50", "mAP50-95")
VALIDATION_STATUS_MISSING = "missing"
VALIDATION_STATUS_PARTIAL = "partial"
VALIDATION_STATUS_COMPLETE = "complete"
VALIDATION_STATUS_ERROR = "error"
VALIDATION_STATUS_VALUES = (
    VALIDATION_STATUS_MISSING,
    VALIDATION_STATUS_PARTIAL,
    VALIDATION_STATUS_COMPLETE,
    VALIDATION_STATUS_ERROR,
)


def sanitize_validation_metrics(raw: dict[str, Any] | None) -> dict[str, float | None]:
    payload = raw or {}
    return {key: to_finite_float(payload.get(key)) for key in _VALIDATION_KEYS}


def validation_status(metrics: dict[str, float | None]) -> str:
    values = list(metrics.values())
    if all(value is None for value in values):
        return VALIDATION_STATUS_MISSING
    if any(value is None for value in values):
        return VALIDATION_STATUS_PARTIAL
    return VALIDATION_STATUS_COMPLETE


def is_validation_success(status: object) -> bool:
    return str(status or "").strip().lower() == VALIDATION_STATUS_COMPLETE


def summarize_prediction_metrics(records: list[PredictionRecord]) -> dict[str, Any]:
    image_count = len(records)
    detection_counts = [len(record.get("boxes", [])) for record in records]
    total_detections = sum(detection_counts)
    images_with_detections = sum(1 for count in detection_counts if count > 0)
    images_without_detections = image_count - images_with_detections

    scores: list[float] = []
    for record in records:
        for raw_score in record.get("scores", []):
            score = to_finite_float(raw_score)
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

    per_class_raw: dict[int, dict] = {}
    for record in records:
        for class_id, raw_score in zip(record.get("class_ids", []), record.get("scores", [])):
            cid = int(class_id)
            entry = per_class_raw.setdefault(cid, {"count": 0, "scores": []})
            entry["count"] += 1
            score = to_finite_float(raw_score)
            if score is not None:
                entry["scores"].append(score)

    per_class: dict[str, Any] = {}
    for cid, entry in sorted(per_class_raw.items()):
        class_scores = entry["scores"]
        per_class[str(cid)] = {
            "count": entry["count"],
            "mean_confidence": (sum(class_scores) / len(class_scores)) if class_scores else None,
            "class_name": COCO_CLASS_NAMES.get(cid, f"class_{cid}"),
        }

    return {
        "image_count": image_count,
        "images_with_detections": images_with_detections,
        "images_without_detections": images_without_detections,
        "total_detections": total_detections,
        "detections_per_image_mean": (total_detections / image_count) if image_count else 0.0,
        "confidence": confidence,
        "per_class": per_class,
    }
