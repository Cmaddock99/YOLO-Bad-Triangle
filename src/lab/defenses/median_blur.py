from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from lab.attacks.utils import iter_images

from .base import Defense


@dataclass
class MedianBlurDefense(Defense):
    kernel_size: int = 3
    name: str = "median_blur"

    def __post_init__(self) -> None:
        if self.kernel_size < 3 or self.kernel_size % 2 == 0:
            raise ValueError("Median blur kernel_size must be odd and >= 3.")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        del seed
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            defended = cv2.medianBlur(image, self.kernel_size)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), defended)
        return output_dir

