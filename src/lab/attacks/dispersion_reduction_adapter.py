from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.config.contracts import PIXEL_MAX

from .base_attack import BaseAttack
from .framework_registry import register_attack_plugin


class _DispersionReductionCore:
    """Core DR attack: PGD that minimises intermediate feature variance."""

    def __init__(self, epsilon: float, steps: int, alpha: float, layer_indices: list[int]):
        self.epsilon = epsilon
        self.steps = steps
        self.alpha = alpha
        self.layer_indices = layer_indices

    def apply_to_tensor(self, x0: torch.Tensor, torch_model: torch.nn.Module) -> torch.Tensor:
        device = x0.device
        torch_model = torch_model.to(device)
        torch_model.eval()
        for p in torch_model.parameters():
            p.requires_grad_(False)

        # Stride-align spatial dims (YOLO requirement)
        stride = int(getattr(torch_model, "stride", torch.tensor([32])).max().item())
        _, _, h, w = x0.shape
        ph = (stride - h % stride) % stride
        pw = (stride - w % stride) % stride
        if ph or pw:
            x0 = F.pad(x0, (0, pw, 0, ph), mode="replicate")

        captured: list[torch.Tensor] = []

        def hook_fn(module, inp, out):
            feat = out[0] if isinstance(out, (tuple, list)) else out
            captured.append(feat)

        handles = []
        try:
            for idx in self.layer_indices:
                if idx < len(torch_model.model):
                    handles.append(torch_model.model[idx].register_forward_hook(hook_fn))

            if not handles:
                raise ValueError(
                    f"DispersionReduction: no hooks registered — all layer_indices "
                    f"{self.layer_indices} exceed model depth {len(torch_model.model)}. "
                    f"Valid range: 0–{len(torch_model.model) - 1}."
                )

            # Random start within epsilon ball
            x_adv = (x0 + torch.empty_like(x0).uniform_(-self.epsilon, self.epsilon)).clamp(0, 1)

            for _ in range(self.steps):
                x_adv = x_adv.detach()
                x_req = x_adv.requires_grad_(True)
                captured.clear()

                with torch.inference_mode(False):
                    with torch.enable_grad():
                        torch_model(x_req)
                        valid = [f for f in captured if f.numel() > 1]
                        if not valid:
                            break
                        # Minimise feature variance → features collapse toward mean
                        var_loss = torch.stack([f.var() for f in valid]).sum()
                        var_loss.backward()

                if x_req.grad is None:
                    break

                # Gradient DESCENT: push toward lower variance (minus sign)
                x_adv = x_adv - self.alpha * x_req.grad.sign()
                delta = (x_adv - x0).clamp(-self.epsilon, self.epsilon)
                x_adv = (x0 + delta).clamp(0.0, 1.0)

        finally:
            for handle in handles:
                handle.remove()

        if ph or pw:
            x_adv = x_adv[:, :, :h, :w]
        return x_adv.detach()


@dataclass
@register_attack_plugin("dispersion_reduction", "dr")
class DispersionReductionAdapter(BaseAttack):
    """
    Dispersion Reduction (DR): black-box transfer attack via feature collapse.

    Minimises variance of intermediate YOLO backbone activations using PGD,
    forcing feature maps toward their channel mean. Requires no class labels
    or task-specific loss — operates purely on feature statistics. Because
    feature collapse transfers across architectures and tasks, this is a
    realistic black-box threat to object detectors.

    Params:
      epsilon  L-inf budget (default 0.05 ≈ 13/255)
      steps    PGD iterations (default 50)
      alpha    Per-step size (default 2*epsilon/steps, auto if 0)
      layers   Backbone layer indices to hook, or "auto" for all C2f blocks
    """

    epsilon: float = 0.05
    steps: int = 50
    alpha: float = field(default=0.0)   # 0 → auto = 2*epsilon/steps
    layers: str = "auto"                # "auto" or comma-separated indices e.g. "2,4,6"
    name: str = "dispersion_reduction_adapter"

    _impl_cache: Any = field(init=False, repr=False, default=None)

    def __post_init__(self) -> None:
        if self.alpha == 0.0:
            self.alpha = 2.0 * self.epsilon / max(self.steps, 1)

    @staticmethod
    def _resolve_torch_model(model: Any) -> torch.nn.Module:
        ensure = getattr(model, "_ensure_loaded", None)
        if callable(ensure):
            ensure()
        model_obj = getattr(model, "_model", model)
        torch_model = getattr(model_obj, "model", model_obj)
        if not isinstance(torch_model, torch.nn.Module):
            raise TypeError("DR attack requires a torch.nn.Module-compatible model.")
        return torch_model

    def _resolve_layer_indices(self, torch_model: torch.nn.Module) -> list[int]:
        if self.layers == "auto":
            indices = [
                i for i, m in enumerate(torch_model.model)
                if type(m).__name__ in ("C2f", "C2fAttn", "C2fPSA", "C2fCIB")
            ]
            return indices if indices else [2, 4, 6]
        if isinstance(self.layers, list):
            return [int(x) for x in self.layers]
        return [int(x.strip()) for x in str(self.layers).split(",") if x.strip()]

    @staticmethod
    def _to_tensor(image: np.ndarray) -> torch.Tensor:
        return (
            torch.from_numpy(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            .float().permute(2, 0, 1).unsqueeze(0) / PIXEL_MAX
        )

    @staticmethod
    def _to_image(tensor: torch.Tensor) -> np.ndarray:
        rgb = (
            tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * PIXEL_MAX
        ).clip(0, 255).round().astype(np.uint8)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        if model is None:
            raise ValueError("DispersionReduction requires a model.")
        torch_model = self._resolve_torch_model(model)
        layer_indices = self._resolve_layer_indices(torch_model)
        impl = _DispersionReductionCore(
            epsilon=self.epsilon,
            steps=self.steps,
            alpha=self.alpha,
            layer_indices=layer_indices,
        )
        x_adv = impl.apply_to_tensor(self._to_tensor(image), torch_model)
        return self._to_image(x_adv), {
            "attack": "dispersion_reduction",
            "epsilon": self.epsilon,
            "steps": self.steps,
            "alpha": self.alpha,
            "layers_hooked": layer_indices,
        }
