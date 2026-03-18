from __future__ import annotations

from pathlib import Path
from typing import Any

from .prediction_schema import PredictionRecord


def normalize_ultralytics_result(result: Any, *, model_name: str) -> PredictionRecord:
    """Convert one Ultralytics result object into framework prediction schema."""
    image_path = Path(str(getattr(result, "path", "unknown_image")))
    boxes_xyxy: list[list[float]] = []
    scores: list[float] = []
    class_ids: list[int] = []

    boxes = getattr(result, "boxes", None)
    if boxes is not None and getattr(boxes, "xyxy", None) is not None:
        boxes_xyxy = [[float(v) for v in row] for row in boxes.xyxy.cpu().tolist()]
        if getattr(boxes, "conf", None) is not None:
            scores = [float(v) for v in boxes.conf.cpu().tolist()]
        if getattr(boxes, "cls", None) is not None:
            class_ids = [int(v) for v in boxes.cls.cpu().tolist()]

    return {
        "image_id": image_path.name,
        "boxes": boxes_xyxy,
        "scores": scores,
        "class_ids": class_ids,
        "metadata": {
            "model": model_name,
            "source_path": str(image_path),
            "orig_shape": list(getattr(result, "orig_shape", []) or []),
        },
    }
