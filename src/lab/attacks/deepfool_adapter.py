from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from .base_attack import BaseAttack
from .framework_registry import register_attack_plugin


@dataclass
@register_attack_plugin("deepfool")
class DeepFoolAttackAdapter(BaseAttack):
    """Framework DeepFool-style plugin."""

    epsilon: float = 0.8
    steps: int = 3
    name: str = "deepfool_adapter"

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("DeepFool steps must be >= 1.")
        if self.epsilon <= 0:
            raise ValueError("DeepFool epsilon must be > 0.")

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
        for _ in range(self.steps):
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
            adv = adv + (self.epsilon * perturb) + jitter

        attacked = np.clip(adv, 0, 255).astype(np.uint8)
        return attacked, {
            "attack": "deepfool",
            "epsilon": self.epsilon,
            "steps": self.steps,
            "limitations": (
                "This implementation is a lightweight DeepFool-style approximation "
                "and does not optimize exact detector decision boundaries."
            ),
        }
