from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch

from lab.attacks.base_attack import BaseAttack
from lab.attacks.fgsm_edge_mask import FGSMSobelEdgeMaskAttack
from lab.attacks.framework_registry import register_attack_plugin
from lab.attacks.objective import AttackObjective
from lab.config.contracts import ATTACK_OBJECTIVE_UNTARGETED, PIXEL_MAX


@dataclass
@register_attack_plugin("fgsm_edge_mask", "localized_fgsm_edge_patch")
class FGSMSobelEdgeMaskAttackAdapter(BaseAttack):
    epsilon: float = 0.008
    edge_threshold: int = 40
    edge_dilate: int = 1
    objective_mode: str = ATTACK_OBJECTIVE_UNTARGETED
    target_class: int | None = None
    preserve_weight: float = 0.25
    attack_roi: tuple[float, float, float, float] | list[float] | str | None = None
    name: str = "fgsm_edge_mask_adapter"
    _impl: FGSMSobelEdgeMaskAttack = field(init=False, repr=False)
    _objective: AttackObjective = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._objective = AttackObjective.from_kwargs(
            mode=self.objective_mode,
            target_class=self.target_class,
            preserve_weight=self.preserve_weight,
            attack_roi=self.attack_roi,
        )
        self._impl = FGSMSobelEdgeMaskAttack(
            epsilon=self.epsilon,
            edge_threshold=self.edge_threshold,
            edge_dilate=self.edge_dilate,
            objective=self._objective,
        )

    @staticmethod
    def _resolve_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError("FGSM edge-mask plugin requires a model.")
        return model

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
        resolved_model = self._resolve_model(model)
        target = kwargs.get("target")
        tensor = self._image_to_tensor(image)
        adv_tensor = self._impl._apply_to_tensor(tensor, resolved_model, target=target)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "fgsm_edge_mask",
            "epsilon": self._impl.epsilon,
            "edge_threshold": self._impl.edge_threshold,
            "edge_dilate": self._impl.edge_dilate,
            **self._objective.to_dict(),
        }
