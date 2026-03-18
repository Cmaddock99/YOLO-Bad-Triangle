from __future__ import annotations

from typing import Any, TypedDict


class PredictionRecord(TypedDict):
    """Normalized prediction schema shared across framework components."""

    image_id: str
    boxes: list[list[float]]
    scores: list[float]
    class_ids: list[int]
    metadata: dict[str, Any]
