from __future__ import annotations

from typing import Any

from .prediction_schema import PredictionRecord


def filter_predictions_by_confidence(
    predictions: list[PredictionRecord],
    *,
    threshold: float,
) -> tuple[list[PredictionRecord], dict[str, Any]]:
    filtered: list[PredictionRecord] = []
    removed_total = 0
    for record in predictions:
        scores = list(record.get("scores", []))
        keep_indices = [idx for idx, score in enumerate(scores) if float(score) >= threshold]
        removed_total += max(0, len(scores) - len(keep_indices))
        filtered.append(
            {
                "image_id": record["image_id"],
                "boxes": [record["boxes"][idx] for idx in keep_indices],
                "scores": [record["scores"][idx] for idx in keep_indices],
                "class_ids": [record["class_ids"][idx] for idx in keep_indices],
                "metadata": dict(record.get("metadata", {})),
            }
        )
    return filtered, {
        "threshold": threshold,
        "removed_detections": removed_total,
    }
