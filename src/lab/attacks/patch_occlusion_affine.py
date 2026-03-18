from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("patch_occlusion_affine", "occlusion_affine")
class PatchOcclusionAffineAttack(Attack):
    """Occlude local evidence and apply mild affine jitter to destabilize YOLO box priors."""

    occlusion_fraction: float = 0.12
    occlusion_count: int = 2
    rotation_deg: float = 6.0
    translate_frac: float = 0.04
    scale_jitter: float = 0.06
    name: str = "patch_occlusion_affine"

    def __post_init__(self) -> None:
        if not (0.0 <= self.occlusion_fraction <= 1.0):
            raise ValueError("occlusion_fraction must be in [0, 1].")
        if self.occlusion_count < 0:
            raise ValueError("occlusion_count must be >= 0.")
        if self.rotation_deg < 0.0:
            raise ValueError("rotation_deg must be >= 0.")
        if self.translate_frac < 0.0:
            raise ValueError("translate_frac must be >= 0.")
        if not (0.0 <= self.scale_jitter < 1.0):
            raise ValueError("scale_jitter must be in [0, 1).")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            work = image.astype(np.float32).copy()
            h, w = work.shape[:2]

            if self.occlusion_count > 0 and self.occlusion_fraction > 0.0:
                total_area = h * w
                per_patch_area = max(1, int((total_area * self.occlusion_fraction) / self.occlusion_count))
                patch_side = max(1, int(np.sqrt(per_patch_area)))
                patch_h = min(h, patch_side)
                patch_w = min(w, patch_side)
                for _ in range(self.occlusion_count):
                    max_y = max(0, h - patch_h)
                    max_x = max(0, w - patch_w)
                    y1 = int(rng.integers(0, max_y + 1))
                    x1 = int(rng.integers(0, max_x + 1))
                    fill_color = rng.integers(0, 256, size=(1, 1, 3), dtype=np.uint8).astype(np.float32)
                    work[y1 : y1 + patch_h, x1 : x1 + patch_w] = fill_color

            angle = float(rng.uniform(-self.rotation_deg, self.rotation_deg))
            tx = float(rng.uniform(-self.translate_frac, self.translate_frac) * w)
            ty = float(rng.uniform(-self.translate_frac, self.translate_frac) * h)
            scale = float(rng.uniform(1.0 - self.scale_jitter, 1.0 + self.scale_jitter))
            matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, scale)
            matrix[0, 2] += tx
            matrix[1, 2] += ty
            transformed = cv2.warpAffine(
                work,
                matrix,
                (w, h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )

            attacked = np.clip(transformed, 0, 255).astype(np.uint8)
            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), attacked)
        return output_dir
