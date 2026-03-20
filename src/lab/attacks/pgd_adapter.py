from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch

from lab.config.contracts import PIXEL_MAX

from .base_attack import BaseAttack
from .pgd import PGDAttack
from .plugin_registry import register_attack_plugin


@dataclass
@register_attack_plugin("pgd", "ifgsm", "bim")
class PGDAttackAdapter(BaseAttack):
    """Framework adapter that reuses legacy PGD tensor-mode implementation."""

    epsilon: float = 0.016
    alpha: float = 0.002
    steps: int = 20
    random_start: bool = True
    restarts: int = 1
    name: str = "pgd_adapter"
    _legacy: PGDAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._legacy = PGDAttack(
            epsilon=self.epsilon,
            alpha=self.alpha,
            steps=self.steps,
            random_start=self.random_start,
            restarts=self.restarts,
        )

    @staticmethod
    def _to_legacy_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError(
                "PGD framework plugin requires a model for gradient computation."
            )
        return getattr(model, "_legacy", model)

    @staticmethod
    def _image_to_tensor(image: np.ndarray) -> torch.Tensor:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return torch.from_numpy(rgb).float().permute(2, 0, 1).unsqueeze(0) / PIXEL_MAX

    @staticmethod
    def _tensor_to_image(tensor: torch.Tensor) -> np.ndarray:
        rgb = np.rint(
            tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * PIXEL_MAX
        ).clip(0, 255).astype(np.uint8)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        legacy_model = self._to_legacy_model(model)
        target = kwargs.get("target")
        seed = kwargs.get("seed")
        tensor = self._image_to_tensor(image)
        adv_tensor = self._legacy.apply(tensor, legacy_model, target=target, seed=seed)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "pgd",
            "epsilon": self._legacy.epsilon,
            "alpha": self._legacy.alpha,
            "steps": self._legacy.steps,
            "random_start": self._legacy.random_start,
            "restarts": self._legacy.restarts,
        }
