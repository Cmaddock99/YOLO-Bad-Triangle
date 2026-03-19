from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch

from .base import register_attack
from .fgsm import FGSMAttack


@register_attack("fgsm_edge_mask", "fgsm_edges")
class FGSMSobelEdgeMaskAttack(FGSMAttack):
    """FGSM variant that applies perturbation mainly on high-gradient edges."""

    def __init__(
        self,
        epsilon: float = 0.008,
        edge_threshold: int = 40,
        edge_dilate: int = 1,
    ) -> None:
        super().__init__(epsilon=epsilon)
        self.edge_threshold = int(edge_threshold)
        self.edge_dilate = int(edge_dilate)
        if self.edge_threshold < 0 or self.edge_threshold > 255:
            raise ValueError("edge_threshold must be in [0, 255].")
        if self.edge_dilate < 0:
            raise ValueError("edge_dilate must be >= 0.")

    def _edge_mask(self, image: torch.Tensor) -> torch.Tensor:
        rgb_uint8 = self._tensor_to_uint8_rgb(image.detach().cpu())
        gray = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2GRAY)
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        edges = (magnitude >= float(self.edge_threshold)).astype(np.uint8)
        if self.edge_dilate > 0:
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=self.edge_dilate)
        return torch.from_numpy(edges).float().unsqueeze(0).unsqueeze(0).to(image.device)

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
    ) -> torch.Tensor:
        base = image.detach().clone()
        adv = super()._apply_to_tensor(image=image, model=model, target=target)
        mask = self._edge_mask(base.to(adv.device))
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
