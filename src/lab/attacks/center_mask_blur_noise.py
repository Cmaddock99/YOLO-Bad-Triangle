from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("center_mask_blur_noise", "center_blur_noise")
class CenterMaskBlurNoiseAttack(Attack):
    """Mask center details, blur structure, and add Gaussian noise to stress YOLO localization."""

    center_scale: float = 0.5
    blur_kernel_size: int = 9
    noise_stddev: float = 8.0
    mask_strength: float = 0.6
    name: str = "center_mask_blur_noise"

    def __post_init__(self) -> None:
        if not (0.0 < self.center_scale <= 1.0):
            raise ValueError("center_scale must be in (0, 1].")
        if self.blur_kernel_size < 3 or self.blur_kernel_size % 2 == 0:
            raise ValueError("blur_kernel_size must be odd and >= 3.")
        if self.noise_stddev < 0.0:
            raise ValueError("noise_stddev must be >= 0.")
        if not (0.0 <= self.mask_strength <= 1.0):
            raise ValueError("mask_strength must be in [0, 1].")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            blurred = cv2.GaussianBlur(image, (self.blur_kernel_size, self.blur_kernel_size), 0)
            work = image.astype(np.float32).copy()
            h, w = image.shape[:2]
            box_h = max(1, int(h * self.center_scale))
            box_w = max(1, int(w * self.center_scale))
            y1 = max(0, (h - box_h) // 2)
            x1 = max(0, (w - box_w) // 2)
            y2 = min(h, y1 + box_h)
            x2 = min(w, x1 + box_w)

            center_orig = work[y1:y2, x1:x2]
            center_blur = blurred[y1:y2, x1:x2].astype(np.float32)
            center_suppressed = center_blur * 0.35
            center_mix = (1.0 - self.mask_strength) * center_orig + self.mask_strength * center_suppressed
            work[y1:y2, x1:x2] = center_mix

            if self.noise_stddev > 0.0:
                noise = rng.normal(0.0, self.noise_stddev, size=work.shape).astype(np.float32)
                work += noise

            attacked = np.clip(work, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), attacked)
        return output_dir
