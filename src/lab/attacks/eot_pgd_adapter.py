from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch

from lab.config.contracts import ATTACK_OBJECTIVE_UNTARGETED, PIXEL_MAX

from .base_attack import BaseAttack
from .eot_pgd import EOTPGDAttack
from .framework_registry import register_attack_plugin
from .objective import AttackObjective


@dataclass
@register_attack_plugin("eot_pgd")
class EOTPGDAttackAdapter(BaseAttack):
    epsilon: float = 0.016
    alpha: float = 0.0015
    steps: int = 20
    random_start: bool = True
    restarts: int = 1
    eot_samples: int = 4
    scale_jitter: float = 0.1
    translate_frac: float = 0.03
    brightness_jitter: float = 0.08
    contrast_jitter: float = 0.08
    blur_prob: float = 0.25
    objective_mode: str = ATTACK_OBJECTIVE_UNTARGETED
    target_class: int | None = None
    preserve_weight: float = 0.25
    attack_roi: tuple[float, float, float, float] | list[float] | str | None = None
    name: str = "eot_pgd_adapter"
    _impl: EOTPGDAttack = field(init=False, repr=False)
    _objective: AttackObjective = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._objective = AttackObjective.from_kwargs(
            mode=self.objective_mode,
            target_class=self.target_class,
            preserve_weight=self.preserve_weight,
            attack_roi=self.attack_roi,
        )
        self._impl = EOTPGDAttack(
            epsilon=self.epsilon,
            alpha=self.alpha,
            steps=self.steps,
            random_start=self.random_start,
            restarts=self.restarts,
            objective=self._objective,
            eot_samples=self.eot_samples,
            scale_jitter=self.scale_jitter,
            translate_frac=self.translate_frac,
            brightness_jitter=self.brightness_jitter,
            contrast_jitter=self.contrast_jitter,
            blur_prob=self.blur_prob,
        )

    @staticmethod
    def _resolve_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError("EOT-PGD framework plugin requires a model.")
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
        seed = kwargs.get("seed")
        tensor = self._image_to_tensor(image)
        adv_tensor = self._impl._apply_to_tensor(tensor, resolved_model, target=target, seed=seed)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "eot_pgd",
            "epsilon": self._impl.epsilon,
            "alpha": self._impl.alpha,
            "steps": self._impl.steps,
            "random_start": self._impl.random_start,
            "restarts": self._impl.restarts,
            "eot_samples": self._impl.eot_samples,
            "scale_jitter": self._impl.scale_jitter,
            "translate_frac": self._impl.translate_frac,
            "brightness_jitter": self._impl.brightness_jitter,
            "contrast_jitter": self._impl.contrast_jitter,
            "blur_prob": self._impl.blur_prob,
            **self._objective.to_dict(),
        }
