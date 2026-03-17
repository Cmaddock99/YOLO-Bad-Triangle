from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("brightness_contrast_noise", "photometric_noise")
class BrightnessContrastNoiseAttack(Attack):
    """Shift photometric statistics and SNR to stress YOLO robustness under illumination drift."""

    brightness_delta: float = 18.0
    contrast_gain: float = 1.15
    noise_stddev: float = 7.5
    channel_jitter: float = 0.04
    name: str = "brightness_contrast_noise"

    def __post_init__(self) -> None:
        if self.contrast_gain <= 0.0:
            raise ValueError("contrast_gain must be > 0.")
        if self.noise_stddev < 0.0:
            raise ValueError("noise_stddev must be >= 0.")
        if self.channel_jitter < 0.0:
            raise ValueError("channel_jitter must be >= 0.")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            work = image.astype(np.float32)
            work = (work * self.contrast_gain) + self.brightness_delta
            if self.channel_jitter > 0.0:
                jitter = rng.uniform(
                    low=1.0 - self.channel_jitter,
                    high=1.0 + self.channel_jitter,
                    size=(1, 1, 3),
                ).astype(np.float32)
                work *= jitter
            if self.noise_stddev > 0.0:
                noise = rng.normal(0.0, self.noise_stddev, size=work.shape).astype(np.float32)
                work += noise

            attacked = np.clip(work, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), attacked)
        return output_dir
