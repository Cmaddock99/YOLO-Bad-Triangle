from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from .base import register_attack
from .fgsm import FGSMAttack


@register_attack("fgsm_center_mask", "fgsm_center")
class FGSMCenterMaskAttack(FGSMAttack):
    """FGSM variant that perturbs only a central elliptical region."""

    def __init__(self, epsilon: float = 0.008, radius_fraction: float = 0.35) -> None:
        super().__init__(epsilon=epsilon)
        self.radius_fraction = float(radius_fraction)
        if not 0.05 <= self.radius_fraction <= 0.95:
            raise ValueError("radius_fraction must be between 0.05 and 0.95.")

    @staticmethod
    def _center_mask(height: int, width: int, radius_fraction: float, device: torch.device) -> torch.Tensor:
        yy, xx = torch.meshgrid(
            torch.arange(height, device=device),
            torch.arange(width, device=device),
            indexing="ij",
        )
        cy = (height - 1) / 2.0
        cx = (width - 1) / 2.0
        ry = max(1.0, height * radius_fraction)
        rx = max(1.0, width * radius_fraction)
        ellipse = (((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2) <= 1.0
        return ellipse.float().unsqueeze(0).unsqueeze(0)

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
    ) -> torch.Tensor:
        base = image.detach().clone()
        adv = super()._apply_to_tensor(image=image, model=model, target=target)
        _, _, h, w = adv.shape
        mask = self._center_mask(h, w, self.radius_fraction, adv.device)
        return torch.clamp(mask * adv + (1.0 - mask) * base.to(adv.device), 0.0, 1.0)

    def apply(
        self,
        source_dir: Path | torch.Tensor,
        output_dir: Path | Any | None = None,
        *,
        seed: int | None = None,
        model: Any | None = None,
        target: torch.Tensor | None = None,
    ) -> Path | torch.Tensor:
        return super().apply(
            source_dir=source_dir,
            output_dir=output_dir,
            seed=seed,
            model=model,
            target=target,
        )
