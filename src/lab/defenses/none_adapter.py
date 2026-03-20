from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lab.eval.adapter_metadata import adapter_stage_metadata
from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .framework_registry import register_defense_plugin


@dataclass
@register_defense_plugin("none", "identity")
class NoDefenseAdapter(BaseDefense):
    """No-op defense adapter for framework compatibility."""

    name: str = "none_defense_adapter"

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        return image, adapter_stage_metadata("none", "preprocess")

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata("none", "postprocess")
