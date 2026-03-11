from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from lab.attacks.utils import iter_images

from .base import Defense, register_defense


@dataclass
@register_defense("denoise", "nlm_denoise")
class DenoiseDefense(Defense):
    h: float = 10.0
    h_color: float = 10.0
    template_window_size: int = 7
    search_window_size: int = 21
    name: str = "denoise"

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        del seed
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            denoised = cv2.fastNlMeansDenoisingColored(
                image,
                None,
                self.h,
                self.h_color,
                self.template_window_size,
                self.search_window_size,
            )
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), denoised)

        return output_dir
