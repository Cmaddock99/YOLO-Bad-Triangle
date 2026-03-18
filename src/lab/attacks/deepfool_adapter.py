from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from .base_attack import BaseAttack
from .deepfool import DeepFoolAttack
from .plugin_registry import register_attack_plugin


@dataclass
@register_attack_plugin("deepfool")
class DeepFoolAttackAdapter(BaseAttack):
    """Framework adapter that reuses legacy DeepFool-style transform."""

    epsilon: float = 0.8
    steps: int = 3
    name: str = "deepfool_adapter"
    _legacy: DeepFoolAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._legacy = DeepFoolAttack(epsilon=self.epsilon, steps=self.steps)

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        # DeepFool-style legacy implementation is model-agnostic in this repo.
        del model
        seed = kwargs.get("seed")
        rng = np.random.default_rng(seed)

        adv = image.astype(np.float32).copy()
        for _ in range(self._legacy.steps):
            gray = cv2.cvtColor(np.clip(adv, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            grad_norm = np.sqrt((grad_x**2) + (grad_y**2)) + 1e-6
            grad_dir = np.stack([grad_x / grad_norm, grad_y / grad_norm], axis=-1)
            perturb = np.zeros_like(adv, dtype=np.float32)
            perturb[..., 0] = grad_dir[..., 0]
            perturb[..., 1] = grad_dir[..., 1]
            perturb[..., 2] = -grad_dir[..., 0]
            jitter = rng.normal(0.0, 0.15, size=adv.shape).astype(np.float32)
            adv = adv + (self._legacy.epsilon * perturb) + jitter

        attacked = np.clip(adv, 0, 255).astype(np.uint8)
        return attacked, {
            "attack": "deepfool",
            "epsilon": self._legacy.epsilon,
            "steps": self._legacy.steps,
            "limitations": (
                "This implementation is a lightweight DeepFool-style approximation "
                "and does not optimize exact detector decision boundaries."
            ),
        }
