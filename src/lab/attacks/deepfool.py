from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("deepfool")
class DeepFoolAttack(Attack):
    """Lightweight DeepFool-style iterative perturbation approximation."""

    epsilon: float = 0.8
    steps: int = 3
    name: str = "deepfool"

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("DeepFool steps must be >= 1.")
        if self.epsilon <= 0:
            raise ValueError("DeepFool epsilon must be > 0.")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            adv = image.astype(np.float32)
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
                jitter = rng.normal(0.0, 0.15, size=adv.shape).astype(np.float32)
                adv = adv + (self.epsilon * perturb) + jitter

            adv = np.clip(adv, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), adv)

        return output_dir
