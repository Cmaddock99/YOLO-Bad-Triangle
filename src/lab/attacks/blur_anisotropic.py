from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("blur_anisotropic", "anisotropic_blur")
class AnisotropicBlurAttack(Attack):
    """Directional Gaussian blur with independent horizontal/vertical kernels."""

    kernel_x: int = 17
    kernel_y: int = 3
    sigma_x: float = 0.0
    sigma_y: float = 0.0
    name: str = "blur_anisotropic"

    def __post_init__(self) -> None:
        if self.kernel_x < 1 or self.kernel_y < 1:
            raise ValueError("kernel_x and kernel_y must be >= 1.")
        if self.kernel_x % 2 == 0 or self.kernel_y % 2 == 0:
            raise ValueError("kernel_x and kernel_y must be odd.")
        if self.sigma_x < 0.0 or self.sigma_y < 0.0:
            raise ValueError("sigma_x and sigma_y must be >= 0.")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        del seed
        output_dir.mkdir(parents=True, exist_ok=True)
        kernel = (self.kernel_x, self.kernel_y)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            blurred = cv2.GaussianBlur(
                image,
                kernel,
                sigmaX=self.sigma_x,
                sigmaY=self.sigma_y,
            )
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), blurred)
        return output_dir
