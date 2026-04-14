from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.config.contracts import PIXEL_MAX

# Below-production-default threshold used to score detections inside the attack loop.
# Intentionally low so weak detections are still counted against the adversary.
_DETECTION_CONF_THRESHOLD = 0.1

from .base_attack import BaseAttack  # noqa: E402
from .fgsm_adapter import FGSMAttack  # noqa: E402
from .framework_registry import register_attack_plugin  # noqa: E402


LOGGER = logging.getLogger(__name__)


class SquareAttack:
    """Query-based L∞ Square Attack (black-box — no gradients required).

    Algorithm:
      1. Start from the clean image. Score = sum of detection confidences.
      2. For each query: pick a random square, apply ±eps perturbation,
         query the model, keep if score drops (adversarial = lower confidence).
      3. Return the best (most adversarial) image found.

    The square size shrinks on a geometric schedule:
      p(step) = p_init * 0.5^(step / n_queries)
    """

    def __init__(
        self,
        eps: float = 0.05,
        n_queries: int = 1000,
        p_init: float = 0.05,
    ) -> None:
        self.eps = float(eps)
        self.n_queries = int(n_queries)
        self.p_init = float(p_init)
        LOGGER.info(
            "SquareAttack initialized (eps=%s n_queries=%s p_init=%s)",
            self.eps, self.n_queries, self.p_init,
        )

    def _score(self, outputs: Any) -> float:
        """Sum of detection confidences above threshold. Lower = more attacked."""
        total = 0.0
        for t in FGSMAttack._iter_output_tensors(outputs):
            if t.ndim >= 2 and t.shape[-1] >= 5:
                conf = t[..., 4]
                total += float(conf[conf > _DETECTION_CONF_THRESHOLD].sum().item())
        return total

    def _apply_to_tensor(
        self,
        x_orig: torch.Tensor,
        torch_model: torch.nn.Module,
        *,
        generator: torch.Generator,
    ) -> tuple[torch.Tensor, dict[str, Any]]:
        _, _, orig_h, orig_w = x_orig.shape

        # Stride-pad for YOLO compatibility (same pattern as PGD)
        stride_val = getattr(torch_model, "stride", torch.tensor([32]))
        stride = int(stride_val.max().item()) if isinstance(stride_val, torch.Tensor) else int(stride_val)
        pad_h = (stride - (orig_h % stride)) % stride
        pad_w = (stride - (orig_w % stride)) % stride
        if pad_h or pad_w:
            x_padded = F.pad(x_orig, (0, pad_w, 0, pad_h), mode="replicate")
        else:
            x_padded = x_orig

        _, _, h, w = x_padded.shape
        device = x_padded.device

        with torch.no_grad():
            best = x_padded.clone()
            best_score = self._score(torch_model(best))

            queries_used = 0
            for step in range(self.n_queries):
                # Shrinking square size schedule
                p = self.p_init * (0.5 ** (step / max(self.n_queries, 1)))
                sq_h = max(1, int(math.ceil(p * h)))
                sq_w = max(1, int(math.ceil(p * w)))

                # Random square location
                top = int(torch.randint(0, max(1, h - sq_h + 1), (1,), generator=generator).item())
                left = int(torch.randint(0, max(1, w - sq_w + 1), (1,), generator=generator).item())

                # ±eps perturbation sign chosen per-channel.
                # Generate on CPU to avoid device/generator mismatch, then move to target device.
                sign = (
                    torch.randint(0, 2, (1, x_padded.shape[1], sq_h, sq_w), generator=generator)
                    .float() * 2.0 - 1.0
                ).to(device)

                candidate = best.clone()
                candidate[:, :, top:top + sq_h, left:left + sq_w] = torch.clamp(
                    candidate[:, :, top:top + sq_h, left:left + sq_w] + self.eps * sign,
                    0.0, 1.0,
                )

                score = self._score(torch_model(candidate))
                queries_used += 1
                if score < best_score:
                    best = candidate
                    best_score = score

        # Crop padding
        if pad_h or pad_w:
            best = best[:, :, :orig_h, :orig_w]

        return best, {
            "attack": "square",
            "eps": self.eps,
            "n_queries": self.n_queries,
            "queries_used": queries_used,
            "final_score": best_score,
        }


@dataclass
@register_attack_plugin("square", "square_attack")
class SquareAttackAdapter(BaseAttack):
    """Framework Square Attack plugin — query-based, black-box."""

    eps: float = 0.05
    n_queries: int = 1000
    p_init: float = 0.05
    device: str = "cpu"
    name: str = "square"
    _impl: SquareAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._impl = SquareAttack(
            eps=self.eps,
            n_queries=self.n_queries,
            p_init=self.p_init,
        )

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
        if model is None:
            raise ValueError("SquareAttackAdapter requires a model for forward queries.")

        torch_model = FGSMAttack._resolve_torch_model(model)

        seed = kwargs.get("seed")
        generator = torch.Generator(device="cpu")
        if seed is not None:
            generator.manual_seed(int(seed))

        tensor = self._image_to_tensor(image)
        adv_tensor, meta = self._impl._apply_to_tensor(tensor, torch_model, generator=generator)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, meta
