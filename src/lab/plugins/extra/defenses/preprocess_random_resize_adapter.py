from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from lab.defenses.base_defense import BaseDefense
from lab.defenses.framework_registry import register_defense_plugin
from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import adapter_stage_metadata


@dataclass
@register_defense_plugin("preprocess_random_resize", "random_resize")
class PreprocessRandomResizeDefenseAdapter(BaseDefense):
    """Input randomization defense."""

    scale_factor_low: float = 0.9
    scale_factor_high: float = 1.0
    seed: int = -1
    name: str = "preprocess_random_resize"

    def __post_init__(self) -> None:
        if not (0.5 <= self.scale_factor_low <= self.scale_factor_high <= 1.0):
            raise ValueError(
                "scale_factor_low must be in [0.5, scale_factor_high] and scale_factor_high <= 1.0."
            )

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        h, w = image.shape[:2]
        rng = random.Random(self.seed) if self.seed >= 0 else random
        scale = rng.uniform(self.scale_factor_low, self.scale_factor_high)
        new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
        resized = cv2.resize(image, (new_w, new_h))
        padded = cv2.copyMakeBorder(
            resized,
            0,
            h - new_h,
            0,
            w - new_w,
            cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )
        return padded, adapter_stage_metadata(
            "preprocess_random_resize",
            "preprocess",
            scale=round(scale, 4),
            new_h=new_h,
            new_w=new_w,
        )

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            "preprocess_random_resize",
            "postprocess",
            note="identity_postprocess",
        )
