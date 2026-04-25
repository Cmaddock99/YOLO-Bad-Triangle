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


def _normalize_map(values: np.ndarray, *, percentile: float = 95.0) -> np.ndarray:
    upper = float(np.percentile(values, percentile))
    if upper <= 1e-8:
        return np.zeros_like(values, dtype=np.float32)
    return np.clip(values / upper, 0.0, 1.0).astype(np.float32)


@dataclass
@register_defense_plugin("blind_patch_recover")
class BlindPatchRecoverDefenseAdapter(BaseDefense):
    """Heuristic blind patch localize-and-inpaint defense."""

    score_percentile: float = 99.0
    min_area_frac: float = 0.01
    max_area_frac: float = 0.20
    dilate_px: int = 8
    inpaint_radius: float = 7.0
    inpaint_method: str = "telea"
    name: str = "blind_patch_recover"
    _stage_name: str = field(default="blind_patch_recover", init=False, repr=False)

    def __post_init__(self) -> None:
        self.score_percentile = float(self.score_percentile)
        self.min_area_frac = float(self.min_area_frac)
        self.max_area_frac = float(self.max_area_frac)
        self.dilate_px = int(self.dilate_px)
        self.inpaint_radius = float(self.inpaint_radius)
        self.inpaint_method = str(self.inpaint_method or "telea").strip().lower()

        if not (0.0 < self.score_percentile <= 100.0):
            raise ValueError("score_percentile must be in (0, 100].")
        if not (0.0 <= self.min_area_frac <= 1.0):
            raise ValueError("min_area_frac must be in [0, 1].")
        if not (0.0 <= self.max_area_frac <= 1.0):
            raise ValueError("max_area_frac must be in [0, 1].")
        if self.min_area_frac > self.max_area_frac:
            raise ValueError("min_area_frac must be <= max_area_frac.")
        if self.dilate_px < 0:
            raise ValueError("dilate_px must be >= 0.")
        if self.inpaint_radius <= 0:
            raise ValueError("inpaint_radius must be > 0.")
        if self.inpaint_method not in _INPAINT_METHODS:
            raise ValueError(
                f"inpaint_method must be one of {sorted(_INPAINT_METHODS)}, got {self.inpaint_method}"
            )

    def _build_anomaly_map(self, image: np.ndarray) -> np.ndarray:
        image_float = image.astype(np.float32) / 255.0
        color_smooth = cv2.GaussianBlur(image_float, (0, 0), sigmaX=3.0, sigmaY=3.0)
        color_deviation = np.linalg.norm(image_float - color_smooth, axis=2)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        laplacian = np.abs(cv2.Laplacian(gray, cv2.CV_32F, ksize=3))
        texture_deviation = cv2.GaussianBlur(laplacian, (0, 0), sigmaX=1.5, sigmaY=1.5)

        anomaly = 0.6 * _normalize_map(color_deviation) + 0.4 * _normalize_map(texture_deviation)
        return _normalize_map(anomaly)

    def _clean_mask(self, mask: np.ndarray) -> np.ndarray:
        open_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
        return cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, close_kernel, iterations=1)

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        anomaly = self._build_anomaly_map(image)
        score_threshold = float(np.percentile(anomaly, self.score_percentile))
        if score_threshold <= 0.0 or float(anomaly.max()) <= 0.0:
            return image.copy(), adapter_stage_metadata(
                self._stage_name,
                "preprocess",
                applied=False,
                score_percentile=self.score_percentile,
                min_area_frac=self.min_area_frac,
                max_area_frac=self.max_area_frac,
                dilate_px=self.dilate_px,
                inpaint_radius=self.inpaint_radius,
                inpaint_method=self.inpaint_method,
                note="low_anomaly_signal",
            )

        threshold_mask = np.where(anomaly >= score_threshold, 255, 0).astype(np.uint8)
        cleaned_mask = self._clean_mask(threshold_mask)
        if not np.any(cleaned_mask):
            return image.copy(), adapter_stage_metadata(
                self._stage_name,
                "preprocess",
                applied=False,
                score_percentile=self.score_percentile,
                score_threshold=score_threshold,
                min_area_frac=self.min_area_frac,
                max_area_frac=self.max_area_frac,
                dilate_px=self.dilate_px,
                inpaint_radius=self.inpaint_radius,
                inpaint_method=self.inpaint_method,
                note="no_mask_after_morphology",
            )

        total_pixels = int(image.shape[0] * image.shape[1])
        min_area_px = max(1, int(round(total_pixels * self.min_area_frac)))
        max_area_px = max(min_area_px, int(round(total_pixels * self.max_area_frac)))
        component_count, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned_mask, connectivity=8)

        best_label = 0
        best_score = -1.0
        best_area = 0
        best_bbox = [0, 0, 0, 0]
        for label in range(1, component_count):
            area_px = int(stats[label, cv2.CC_STAT_AREA])
            if area_px < min_area_px or area_px > max_area_px:
                continue
            component_mask = labels == label
            component_score = float(anomaly[component_mask].sum())
            if component_score > best_score:
                left = int(stats[label, cv2.CC_STAT_LEFT])
                top = int(stats[label, cv2.CC_STAT_TOP])
                width = int(stats[label, cv2.CC_STAT_WIDTH])
                height = int(stats[label, cv2.CC_STAT_HEIGHT])
                best_label = label
                best_score = component_score
                best_area = area_px
                best_bbox = [left, top, width, height]

        if best_label == 0:
            return image.copy(), adapter_stage_metadata(
                self._stage_name,
                "preprocess",
                applied=False,
                score_percentile=self.score_percentile,
                score_threshold=score_threshold,
                min_area_frac=self.min_area_frac,
                max_area_frac=self.max_area_frac,
                min_area_px=min_area_px,
                max_area_px=max_area_px,
                dilate_px=self.dilate_px,
                inpaint_radius=self.inpaint_radius,
                inpaint_method=self.inpaint_method,
                note="no_component_within_area_bounds",
            )

        selected_mask = np.where(labels == best_label, 255, 0).astype(np.uint8)
        if self.dilate_px > 0:
            kernel_size = self.dilate_px * 2 + 1
            dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            selected_mask = cv2.dilate(selected_mask, dilate_kernel, iterations=1)

        output = cv2.inpaint(
            image,
            selected_mask,
            self.inpaint_radius,
            _INPAINT_METHODS[self.inpaint_method],
        )
        return output, adapter_stage_metadata(
            self._stage_name,
            "preprocess",
            applied=True,
            score_percentile=self.score_percentile,
            score_threshold=score_threshold,
            min_area_frac=self.min_area_frac,
            max_area_frac=self.max_area_frac,
            min_area_px=min_area_px,
            max_area_px=max_area_px,
            component_area_px=best_area,
            component_area_frac=best_area / float(total_pixels),
            component_bbox_xywh=best_bbox,
            dilate_px=self.dilate_px,
            mask_area_px=int(np.count_nonzero(selected_mask)),
            inpaint_radius=self.inpaint_radius,
            inpaint_method=self.inpaint_method,
            note="blind_localize_and_inpaint",
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
            note="identity_postprocess",
        )
