from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("noise_blockwise", "block_noise")
class BlockwiseGaussianNoiseAttack(Attack):
    """Apply Gaussian noise with per-block variance jitter for spatial diversity."""

    stddev: float = 10.0
    block_size: int = 32
    scale_jitter: float = 0.5
    name: str = "noise_blockwise"

    def __post_init__(self) -> None:
        if self.stddev <= 0.0:
            raise ValueError("stddev must be > 0.")
        if self.block_size < 4:
            raise ValueError("block_size must be >= 4.")
        if self.scale_jitter < 0.0:
            raise ValueError("scale_jitter must be >= 0.")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            h, w, _ = image.shape
            noisy = image.astype(np.float32).copy()
            for y0 in range(0, h, self.block_size):
                for x0 in range(0, w, self.block_size):
                    y1 = min(h, y0 + self.block_size)
                    x1 = min(w, x0 + self.block_size)
                    local_scale = rng.uniform(1.0 - self.scale_jitter, 1.0 + self.scale_jitter)
                    local_std = max(0.01, self.stddev * local_scale)
                    block_noise = rng.normal(0.0, local_std, size=(y1 - y0, x1 - x0, 3))
                    noisy[y0:y1, x0:x1] += block_noise.astype(np.float32)

            noisy = np.clip(noisy, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), noisy)
        return output_dir
