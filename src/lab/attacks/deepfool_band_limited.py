from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("deepfool_band_limited", "deepfool_banded")
class DeepFoolBandLimitedAttack(Attack):
    """DeepFool-style perturbation constrained to horizontal stripe bands."""

    epsilon: float = 0.9
    steps: int = 3
    stripe_period: int = 32
    stripe_width: int = 12
    blur_kernel: int = 7
    name: str = "deepfool_band_limited"

    def __post_init__(self) -> None:
        if self.epsilon <= 0.0:
            raise ValueError("epsilon must be > 0.")
        if self.steps < 1:
            raise ValueError("steps must be >= 1.")
        if self.stripe_period < 4:
            raise ValueError("stripe_period must be >= 4.")
        if self.stripe_width < 1 or self.stripe_width > self.stripe_period:
            raise ValueError("stripe_width must be in [1, stripe_period].")
        if self.blur_kernel < 1 or self.blur_kernel % 2 == 0:
            raise ValueError("blur_kernel must be odd and >= 1.")

    def _stripe_mask(self, height: int, width: int) -> np.ndarray:
        mask = np.zeros((height, width), dtype=np.float32)
        for start in range(0, height, self.stripe_period):
            end = min(height, start + self.stripe_width)
            mask[start:end, :] = 1.0
        return np.repeat(mask[:, :, None], 3, axis=2)

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            adv = image.astype(np.float32)
            h, w, _ = adv.shape
            stripe_mask = self._stripe_mask(h, w)
            for _ in range(self.steps):
                gray = cv2.cvtColor(np.clip(adv, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
                grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
                grad_norm = np.sqrt((grad_x**2) + (grad_y**2)) + 1e-6
                grad_dir = np.stack([grad_x / grad_norm, grad_y / grad_norm], axis=-1)
                perturb = np.zeros_like(adv, dtype=np.float32)
                perturb[..., 0] = grad_dir[..., 0]
                perturb[..., 1] = grad_dir[..., 1]
                perturb[..., 2] = -grad_dir[..., 0]
                perturb = cv2.GaussianBlur(perturb, (self.blur_kernel, self.blur_kernel), 0)
                jitter = rng.normal(0.0, 0.1, size=adv.shape).astype(np.float32)
                adv = adv + ((self.epsilon * perturb + jitter) * stripe_mask)

            adv = np.clip(adv, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), adv)

        return output_dir
