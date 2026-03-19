from __future__ import annotations

from typing import Any, TypedDict


class PredictionRecord(TypedDict):
    """Normalized prediction schema shared across framework components."""

    image_id: str
    boxes: list[list[float]]
    scores: list[float]
    class_ids: list[int]
    metadata: dict[str, Any]


def validate_prediction_record(record: dict[str, Any], *, index: int) -> None:
    required = ("image_id", "boxes", "scores", "class_ids", "metadata")
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(
            f"Prediction record at index {index} missing required keys: {', '.join(missing)}"
        )
    if not isinstance(record["image_id"], str) or not record["image_id"].strip():
        raise ValueError(f"Prediction record at index {index} has invalid image_id.")
    if not isinstance(record["boxes"], list):
        raise ValueError(f"Prediction record at index {index} has non-list boxes.")
    if not isinstance(record["scores"], list):
        raise ValueError(f"Prediction record at index {index} has non-list scores.")
    if not isinstance(record["class_ids"], list):
        raise ValueError(f"Prediction record at index {index} has non-list class_ids.")
    if not isinstance(record["metadata"], dict):
        raise ValueError(f"Prediction record at index {index} has non-dict metadata.")
    length = len(record["scores"])
    if len(record["boxes"]) != length or len(record["class_ids"]) != length:
        raise ValueError(
            f"Prediction record at index {index} has mismatched lengths for boxes/scores/class_ids."
        )


def validate_prediction_records(records: list[PredictionRecord]) -> None:
    for idx, record in enumerate(records):
        validate_prediction_record(record, index=idx)
