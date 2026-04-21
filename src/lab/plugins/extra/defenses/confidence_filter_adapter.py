from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lab.defenses.base_defense import BaseDefense
from lab.defenses.framework_registry import register_defense_plugin
from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import (
    adapter_stage_metadata,
    filter_predictions_by_confidence,
)


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
        return image, adapter_stage_metadata(
            "confidence_filter",
            "preprocess",
            note="identity_preprocess",
        )

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        filtered, summary = filter_predictions_by_confidence(
            predictions,
            threshold=self.threshold,
        )
        return filtered, adapter_stage_metadata(
            "confidence_filter",
            "postprocess",
            **summary,
        )
