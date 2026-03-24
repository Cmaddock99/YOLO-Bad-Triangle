from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from .base_attack import BaseAttack
from .framework_registry import register_attack_plugin


@dataclass
@register_attack_plugin("jpeg_attack")
class JPEGAttackAdapter(BaseAttack):
    """JPEG compression attack — quantizes DCT coefficients, destroying high-frequency model features."""

    quality: int = 75
    name: str = "jpeg_attack"

    def __post_init__(self) -> None:
        q = int(self.quality)
        if not (1 <= q <= 95):
            raise ValueError("quality must be in [1, 95].")
        self.quality = q

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del model, kwargs
        _, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        compressed = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return compressed, {"attack": "jpeg_attack", "quality": self.quality}
