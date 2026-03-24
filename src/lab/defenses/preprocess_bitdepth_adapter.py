from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import adapter_stage_metadata

from .base_defense import BaseDefense
from .framework_registry import register_defense_plugin


@dataclass
@register_defense_plugin("preprocess_bit_depth", "bit_depth")
class PreprocessBitDepthDefenseAdapter(BaseDefense):
    """Bit-depth reduction defense — quantize pixel values to N bits.

    Removes fine-grained adversarial perturbations (FGSM/PGD operate at sub-bit granularity).
    At 5 bits: 32 discrete levels per channel, drops 3 LSBs.
    """

    bits: int = 5
    name: str = "preprocess_bit_depth"

    def __post_init__(self) -> None:
        b = int(self.bits)
        if not (1 <= b <= 7):
            raise ValueError("bits must be in [1, 7].")
        self.bits = b

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        shift = 8 - self.bits
        quantized = ((image.astype(np.uint16) >> shift) << shift).clip(0, 255).astype(np.uint8)
        return quantized, adapter_stage_metadata("preprocess_bit_depth", "preprocess", bits=self.bits)

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            "preprocess_bit_depth", "postprocess", note="identity_postprocess"
        )
