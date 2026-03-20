from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from .base_attack import BaseAttack
from .framework_registry import register_attack_plugin


@dataclass
@register_attack_plugin("blur", "gaussian_blur")
class BlurAttackAdapter(BaseAttack):
    """Framework Gaussian blur plugin."""

    kernel_size: int = 9
    name: str = "blur_adapter"

    def __post_init__(self) -> None:
        if self.kernel_size < 3 or self.kernel_size % 2 == 0:
            raise ValueError("Blur kernel_size must be odd and >= 3.")

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del model, kwargs
        blurred = cv2.GaussianBlur(
            image,
            (self.kernel_size, self.kernel_size),
            0,
        )
        return blurred, {
            "attack": "blur",
            "kernel_size": self.kernel_size,
        }
