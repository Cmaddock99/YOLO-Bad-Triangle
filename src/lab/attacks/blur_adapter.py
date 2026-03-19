from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from .base_attack import BaseAttack
from .blur import GaussianBlurAttack
from .plugin_registry import register_attack_plugin


@dataclass
@register_attack_plugin("blur", "gaussian_blur")
class BlurAttackAdapter(BaseAttack):
    """Framework adapter that reuses the existing GaussianBlurAttack behavior."""

    kernel_size: int = 9
    name: str = "blur_adapter"
    _legacy: GaussianBlurAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Reuse legacy validation and parameter behavior.
        self._legacy = GaussianBlurAttack(kernel_size=self.kernel_size)

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del model, kwargs
        blurred = cv2.GaussianBlur(
            image,
            (self._legacy.kernel_size, self._legacy.kernel_size),
            0,
        )
        return blurred, {
            "attack": "blur",
            "kernel_size": self._legacy.kernel_size,
        }
