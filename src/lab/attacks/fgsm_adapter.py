from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch

from .base_attack import BaseAttack
from .fgsm import FGSMAttack
from .plugin_registry import register_attack_plugin


@dataclass
@register_attack_plugin("fgsm")
class FGSMAttackAdapter(BaseAttack):
    """Framework adapter that reuses legacy FGSM tensor-mode implementation."""

    epsilon: float = 0.01
    name: str = "fgsm_adapter"
    _legacy: FGSMAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._legacy = FGSMAttack(epsilon=self.epsilon)

    @staticmethod
    def _to_legacy_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError(
                "FGSM framework plugin requires a model for gradient computation."
            )
        return getattr(model, "_legacy", model)

    @staticmethod
    def _image_to_tensor(image: np.ndarray) -> torch.Tensor:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return torch.from_numpy(rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0

    @staticmethod
    def _tensor_to_image(tensor: torch.Tensor) -> np.ndarray:
        rgb = np.rint(
            tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255.0
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
        tensor = self._image_to_tensor(image)
        adv_tensor = self._legacy.apply(tensor, legacy_model, target=target)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "fgsm",
            "epsilon": self._legacy.epsilon,
        }
