from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .plugin_registry import register_defense_plugin


@dataclass
@register_defense_plugin("none", "identity")
class NoDefenseAdapter(BaseDefense):
    """No-op defense adapter for framework compatibility."""

    name: str = "none_defense_adapter"

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        return image, {"defense": "none", "stage": "preprocess"}

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, {"defense": "none", "stage": "postprocess"}
