from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from lab.defenses.base_defense import BaseDefense
from lab.defenses.framework_registry import register_defense_plugin
from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import adapter_stage_metadata

_INPAINT_METHODS = {
    "telea": cv2.INPAINT_TELEA,
    "ns": cv2.INPAINT_NS,
}


@dataclass
@register_defense_plugin("oracle_patch_recover")
class OraclePatchRecoverDefenseAdapter(BaseDefense):
    """Oracle upper-bound defense that inpaints the exact known patch region."""

    dilate_px: int = 8
    inpaint_radius: float = 7.0
    inpaint_method: str = "telea"
    name: str = "oracle_patch_recover"
    _stage_name: str = field(default="oracle_patch_recover", init=False, repr=False)

    def __post_init__(self) -> None:
        self.dilate_px = int(self.dilate_px)
        self.inpaint_radius = float(self.inpaint_radius)
        self.inpaint_method = str(self.inpaint_method or "telea").strip().lower()
        if self.dilate_px < 0:
            raise ValueError("dilate_px must be >= 0.")
        if self.inpaint_radius <= 0:
            raise ValueError("inpaint_radius must be > 0.")
        if self.inpaint_method not in _INPAINT_METHODS:
            raise ValueError(
                f"inpaint_method must be one of {sorted(_INPAINT_METHODS)}, got {self.inpaint_method}"
            )

    def _mask_from_attack_metadata(
        self,
        image: np.ndarray,
        attack_metadata: dict[str, Any] | None,
    ) -> np.ndarray | None:
        if not isinstance(attack_metadata, dict):
            return None
        top = attack_metadata.get("top")
        left = attack_metadata.get("left")
        applied_patch_size = attack_metadata.get("applied_patch_size")
        if top is None or left is None or not isinstance(applied_patch_size, list) or len(applied_patch_size) != 2:
            return None
        patch_h = int(applied_patch_size[0])
        patch_w = int(applied_patch_size[1])
        top_i = int(top)
        left_i = int(left)
        if patch_h <= 0 or patch_w <= 0:
            return None
        bottom = min(image.shape[0], top_i + patch_h)
        right = min(image.shape[1], left_i + patch_w)
        top_i = max(0, top_i)
        left_i = max(0, left_i)
        if top_i >= bottom or left_i >= right:
            return None
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        mask[top_i:bottom, left_i:right] = 255
        if self.dilate_px > 0:
            kernel_size = self.dilate_px * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            mask = cv2.dilate(mask, kernel, iterations=1)
        return mask

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        attack_metadata = kwargs.get("attack_metadata")
        mask = self._mask_from_attack_metadata(image, attack_metadata if isinstance(attack_metadata, dict) else None)
        if mask is None:
            return image.copy(), adapter_stage_metadata(
                self._stage_name,
                "preprocess",
                oracle_upper_bound=True,
                applied=False,
                note="no_attack_metadata_available",
            )
        output = cv2.inpaint(
            image,
            mask,
            self.inpaint_radius,
            _INPAINT_METHODS[self.inpaint_method],
        )
        return output, adapter_stage_metadata(
            self._stage_name,
            "preprocess",
            oracle_upper_bound=True,
            applied=True,
            dilate_px=self.dilate_px,
            inpaint_radius=self.inpaint_radius,
            inpaint_method=self.inpaint_method,
            note="oracle_upper_bound_exact_patch_region",
        )

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            self._stage_name,
            "postprocess",
            oracle_upper_bound=True,
            note="identity_postprocess",
        )
