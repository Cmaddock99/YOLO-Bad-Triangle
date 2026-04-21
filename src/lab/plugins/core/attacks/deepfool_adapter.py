from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.attacks.base_attack import BaseAttack
from lab.attacks.framework_registry import register_attack_plugin
from lab.attacks.objective import AttackObjective
from lab.config.contracts import (
    ATTACK_OBJECTIVE_CLASS_HIDE,
    ATTACK_OBJECTIVE_TARGET_CLASS,
    ATTACK_OBJECTIVE_UNTARGETED,
    PIXEL_MAX,
)
from lab.plugins.core.attacks.fgsm_adapter import FGSMAttack


LOGGER = logging.getLogger(__name__)


class DeepFoolAttack(FGSMAttack):
    """DeepFool for object detection."""

    def __init__(
        self,
        epsilon: float = 0.05,
        steps: int = 50,
        overshoot: float = 0.02,
        *,
        objective: AttackObjective | None = None,
    ) -> None:
        super().__init__(epsilon=epsilon, objective=objective)
        if steps < 1:
            raise ValueError("steps must be >= 1.")
        if overshoot < 0.0:
            raise ValueError("overshoot must be >= 0.")
        self.steps = int(steps)
        self.overshoot = float(overshoot)
        LOGGER.info(
            "DeepFool attack initialized (epsilon=%s steps=%s overshoot=%s)",
            self.epsilon,
            self.steps,
            self.overshoot,
        )

    def _detection_confidence(self, outputs: Any) -> torch.Tensor | None:
        tensors = self._iter_output_tensors(outputs)
        conf_terms: list[torch.Tensor] = []
        class_logits = self._extract_class_logits(tensors)
        if class_logits is not None:
            target_class = int(self.objective.target_class or 0)
            max_classes = int(class_logits.shape[-1])
            if target_class < 0 or target_class >= max_classes:
                raise ValueError(
                    f"target_class {target_class} out of range for logits size {max_classes}"
                )
            target = class_logits[..., target_class].mean()
            if self.objective.mode == ATTACK_OBJECTIVE_TARGET_CLASS:
                return -target
            if self.objective.mode == ATTACK_OBJECTIVE_CLASS_HIDE:
                if max_classes <= 1:
                    return target
                other_idx = [idx for idx in range(max_classes) if idx != target_class]
                others = class_logits[..., other_idx].mean()
                return target - (self.objective.preserve_weight * others)

        for t in tensors:
            if t.ndim == 3:
                _, c, n = t.shape
                if c > 4 and n > 100:
                    conf_terms.append(t.float().sigmoid().mean())
                elif n == 6:
                    conf_terms.append(t[..., 4].float().mean())
        if conf_terms:
            return torch.stack(conf_terms).mean()
        all_t = [t.float().sigmoid().mean() for t in tensors if t.numel() > 0]
        return torch.stack(all_t).mean() if all_t else None

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
    ) -> torch.Tensor:
        del target
        torch_model = self._resolve_torch_model(model)

        if image.device.type in {"cpu", "mps"}:
            device = image.device
        else:
            try:
                device = next(torch_model.parameters()).device
            except StopIteration:
                device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        torch_model = torch_model.to(device)
        image = image.to(device)

        _, _, orig_h, orig_w = image.shape
        stride = int(getattr(torch_model, "stride", torch.tensor([32])).max().item())
        pad_h = (stride - (orig_h % stride)) % stride
        pad_w = (stride - (orig_w % stride)) % stride
        x0 = image.clone().detach()
        if pad_h or pad_w:
            x0 = F.pad(x0, (0, pad_w, 0, pad_h), mode="replicate")

        r_total = torch.zeros_like(x0)

        for step in range(self.steps):
            x_hat = torch.clamp(x0 + r_total, 0.0, 1.0).detach().requires_grad_(True)
            torch_model.zero_grad(set_to_none=True)
            with torch.inference_mode(False):
                with torch.enable_grad():
                    outputs = torch_model(x_hat)
                    f_val = self._detection_confidence(outputs)
                    if f_val is None:
                        break
                    f_val.backward()

            if x_hat.grad is None:
                break

            f_scalar = f_val.item()
            if f_scalar < 1e-6:
                LOGGER.debug("DeepFool: confidence suppressed at step %s/%s.", step, self.steps)
                break

            w = x_hat.grad.detach()
            _, _, padded_h, padded_w = w.shape
            grad_mask = self.objective.gradient_mask(
                height=padded_h,
                width=padded_w,
                device=w.device,
            )
            if grad_mask is not None:
                w = w * grad_mask
            w_sq = w.pow(2).sum().clamp(min=1e-8)
            r_step = -(1.0 + self.overshoot) * (f_scalar / w_sq.item()) * w
            r_total = (r_total + r_step).clamp(-self.epsilon, self.epsilon)

        result = torch.clamp(x0 + r_total, 0.0, 1.0)
        if pad_h or pad_w:
            result = result[:, :, :orig_h, :orig_w]
        return result.detach()


@dataclass
@register_attack_plugin("deepfool")
class DeepFoolAttackAdapter(BaseAttack):
    """Framework DeepFool plugin."""

    epsilon: float = 0.05
    steps: int = 50
    overshoot: float = 0.02
    objective_mode: str = ATTACK_OBJECTIVE_UNTARGETED
    target_class: int | None = None
    preserve_weight: float = 0.25
    attack_roi: tuple[float, float, float, float] | list[float] | str | None = None
    name: str = "deepfool_adapter"
    _impl: DeepFoolAttack = field(init=False, repr=False)
    _objective: AttackObjective = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._objective = AttackObjective.from_kwargs(
            mode=self.objective_mode,
            target_class=self.target_class,
            preserve_weight=self.preserve_weight,
            attack_roi=self.attack_roi,
        )
        self._impl = DeepFoolAttack(
            epsilon=self.epsilon,
            steps=self.steps,
            overshoot=self.overshoot,
            objective=self._objective,
        )

    @staticmethod
    def _resolve_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError("DeepFool framework plugin requires a model.")
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
        del kwargs
        resolved_model = self._resolve_model(model)
        tensor = self._image_to_tensor(image)
        adv_tensor = self._impl._apply_to_tensor(tensor, resolved_model)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "deepfool",
            "epsilon": self._impl.epsilon,
            "steps": self._impl.steps,
            "overshoot": self._impl.overshoot,
            **self._objective.to_dict(),
        }
