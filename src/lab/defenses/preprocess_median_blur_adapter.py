from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from lab.eval.adapter_metadata import adapter_stage_metadata
from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .plugin_registry import register_defense_plugin


@dataclass
@register_defense_plugin("preprocess_median_blur", "median_preprocess")
class PreprocessMedianBlurDefenseAdapter(BaseDefense):
    """Simple preprocessing defense using median blur before inference."""

    kernel_size: int = 3
    name: str = "preprocess_median_blur_adapter"

    def __post_init__(self) -> None:
        k = int(self.kernel_size)
        if k < 3 or k % 2 == 0:
            raise ValueError("kernel_size must be odd and >= 3.")
        self.kernel_size = k

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        processed = cv2.medianBlur(image, self.kernel_size)
        return processed, adapter_stage_metadata(
            "preprocess_median_blur",
            "preprocess",
            kernel_size=self.kernel_size,
        )

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            "preprocess_median_blur",
            "postprocess",
            note="identity_postprocess",
        )
