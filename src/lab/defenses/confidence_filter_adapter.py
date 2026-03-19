from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .plugin_registry import register_defense_plugin


@dataclass
@register_defense_plugin("confidence_filter", "conf_filter")
class ConfidenceFilterDefenseAdapter(BaseDefense):
    """Postprocess defense that removes low-confidence detections."""

    threshold: float = 0.5
    name: str = "confidence_filter_adapter"

    def __post_init__(self) -> None:
        threshold = float(self.threshold)
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("threshold must be in [0, 1].")
        self.threshold = threshold

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        return image, {
            "defense": "confidence_filter",
            "stage": "preprocess",
            "note": "identity_preprocess",
        }

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        filtered: list[PredictionRecord] = []
        removed_total = 0
        for record in predictions:
            scores = list(record.get("scores", []))
            keep_indices = [idx for idx, score in enumerate(scores) if float(score) >= self.threshold]
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
            "defense": "confidence_filter",
            "stage": "postprocess",
            "threshold": self.threshold,
            "removed_detections": removed_total,
        }
