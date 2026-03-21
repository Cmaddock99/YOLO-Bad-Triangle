from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.config.contracts import PIXEL_MAX

from .base_attack import BaseAttack
from .fgsm_adapter import FGSMAttack
from .framework_registry import register_attack_plugin


LOGGER = logging.getLogger(__name__)


class DeepFoolAttack(FGSMAttack):
    """DeepFool for object detection.

    At each step, computes the minimal L2 perturbation that linearises the
    detection confidence to zero, then projects the accumulated delta onto an
    L∞ ball of radius epsilon.  This matches the spirit of Moosavi-Dezfooli
    et al. (2016) adapted to an untargeted, confidence-suppression objective.

    Key difference from FGSM: the per-step size is derived from the ratio
    f(x)/||∇f(x)||², not a fixed epsilon.  The attack terminates early if
    confidence already reaches zero (no detections above threshold).
    """

    def __init__(
        self,
        epsilon: float = 0.05,
        steps: int = 50,
        overshoot: float = 0.02,
    ) -> None:
        super().__init__(epsilon=epsilon)
        if steps < 1:
            raise ValueError("steps must be >= 1.")
        if overshoot < 0.0:
            raise ValueError("overshoot must be >= 0.")
        self.steps = int(steps)
        self.overshoot = float(overshoot)
        LOGGER.info(
            "DeepFool attack initialized (epsilon=%s steps=%s overshoot=%s)",
            self.epsilon, self.steps, self.overshoot,
        )

    def _detection_confidence(self, outputs: Any) -> torch.Tensor | None:
        """Return a differentiable scalar in (0, 1] representing aggregate detection confidence.

        YOLO outputs tensors of shape (batch, channels, anchors) where channels=4 are
        box coordinates and channels=num_classes are raw class logits.  Applying sigmoid
        to class logit tensors gives a proxy that is always positive (never causes the
        DeepFool loop to terminate early) and has meaningful gradients.
        """
        tensors = self._iter_output_tensors(outputs)
        conf_terms: list[torch.Tensor] = []
        for t in tensors:
            if t.ndim == 3:
                _, c, n = t.shape
                if c > 4 and n > 100:
                    # Class score tensor (batch, num_classes, num_anchors) — apply sigmoid
                    # so values are in (0, 1) and gradients flow cleanly.
                    conf_terms.append(t.float().sigmoid().mean())
                elif n == 6:
                    # Post-NMS output (batch, detections, 6=[x,y,x,y,conf,cls])
                    conf_terms.append(t[..., 4].float().mean())
        if conf_terms:
            return torch.stack(conf_terms).mean()
        # Fallback: sigmoid of all tensor values keeps the proxy in (0, 1).
        all_t = [t.float().sigmoid().mean() for t in tensors if t.numel() > 0]
        return torch.stack(all_t).mean() if all_t else None

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
    ) -> torch.Tensor:
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
            # Minimal L2 step: r = -(1 + overshoot) * f(x) / ||w||² * w
            # Negative because we are minimising confidence (driving f → 0).
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
    name: str = "deepfool_adapter"
    _impl: DeepFoolAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._impl = DeepFoolAttack(
            epsilon=self.epsilon,
            steps=self.steps,
            overshoot=self.overshoot,
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
        resolved_model = self._resolve_model(model)
        tensor = self._image_to_tensor(image)
        adv_tensor = self._impl._apply_to_tensor(tensor, resolved_model)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "deepfool",
            "epsilon": self._impl.epsilon,
            "steps": self._impl.steps,
            "overshoot": self._impl.overshoot,
        }
