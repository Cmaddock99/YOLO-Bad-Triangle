from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import adapter_stage_metadata

from .base_defense import BaseDefense
from .framework_registry import register_defense_plugin


@dataclass
@register_defense_plugin("preprocess_jpeg", "jpeg_preprocess")
class PreprocessJPEGDefenseAdapter(BaseDefense):
    """JPEG compression preprocessing defense — removes high-frequency adversarial noise."""

    quality: int = 75
    name: str = "preprocess_jpeg"

    def __post_init__(self) -> None:
        q = int(self.quality)
        if not (1 <= q <= 95):
            raise ValueError("quality must be in [1, 95].")
        self.quality = q

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        _, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        processed = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return processed, adapter_stage_metadata("preprocess_jpeg", "preprocess", quality=self.quality)

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            "preprocess_jpeg", "postprocess", note="identity_postprocess"
        )
