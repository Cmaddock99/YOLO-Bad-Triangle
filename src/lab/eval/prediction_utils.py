from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .prediction_schema import PredictionRecord


def adapter_stage_metadata(defense: str, stage: str, **extra: Any) -> dict[str, Any]:
    return {
        "defense": defense,
        "stage": stage,
        **extra,
    }


def write_predictions_jsonl(records: Iterable[PredictionRecord], output_path: Path) -> None:
    """Persist normalized prediction records as JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


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
