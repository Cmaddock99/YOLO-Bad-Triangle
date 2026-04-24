from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

from lab.attacks.base_attack import BaseAttack
from lab.attacks.framework_registry import register_attack_plugin

_ARTIFACT_PROVENANCE_KEYS = (
    "artifact_sha256",
    "run_name",
    "model",
    "joint_models",
    "joint_weights",
    "patch_size",
    "training_images",
    "detection_suppression_pct",
    "manifest_path",
    "loss_source",
    "placement_regime",
    "block_erase_prob",
    "cutout_prob",
    "cutout_size",
    "self_ensemble_mode",
    "self_ensemble_prob",
    "rot_max",
    "cloth_eot",
    "nps_weight",
    "repo_commit",
    "created_at",
)
PLACEMENT_LARGEST_PERSON_TORSO = "largest_person_torso"
PLACEMENT_OFF_OBJECT_FIXED = "off_object_fixed"
PLACEMENT_MODES = {PLACEMENT_LARGEST_PERSON_TORSO, PLACEMENT_OFF_OBJECT_FIXED}


@dataclass
@register_attack_plugin("pretrained_patch", "adv_patch")
class PretrainedPatchAttackAdapter(BaseAttack):
    artifact_path: str = ""
    resize_to: tuple[int, int] | list[int] | None = None
    clean_detect_conf: float = 0.5
    clean_detect_iou: float = 0.7
    placement_mode: str = PLACEMENT_LARGEST_PERSON_TORSO
    fallback_mode: str = field(default="center", init=False)
    person_class_id: int = field(default=0, init=False)
    name: str = "pretrained_patch"
    _artifact_path: Path = field(init=False, repr=False)
    _artifact_sha256: str = field(init=False, repr=False)
    _artifact_size: tuple[int, int] = field(init=False, repr=False)
    _base_patch_bgr: np.ndarray = field(init=False, repr=False)
    _artifact_provenance: dict[str, Any] | None = field(init=False, repr=False)

    def __post_init__(self) -> None:
        artifact_raw = str(self.artifact_path or "").strip()
        if not artifact_raw:
            raise ValueError("artifact_path is required for pretrained_patch.")
        self._artifact_path = Path(artifact_raw).expanduser().resolve()
        if not self._artifact_path.is_file():
            raise FileNotFoundError(f"Patch artifact not found: {self._artifact_path}")

        patch_bytes = self._artifact_path.read_bytes()
        self._artifact_sha256 = hashlib.sha256(patch_bytes).hexdigest()
        with Image.open(self._artifact_path) as handle:
            rgb = np.asarray(handle.convert("RGB"), dtype=np.uint8)
        self._artifact_size = (int(rgb.shape[0]), int(rgb.shape[1]))
        self._base_patch_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        resize_to = self._normalize_resize_to(self.resize_to)
        if resize_to is not None:
            self._base_patch_bgr = self._resize_patch(self._base_patch_bgr, resize_to)
            self.resize_to = resize_to
        else:
            self.resize_to = None
        self.artifact_path = str(self._artifact_path)
        self.clean_detect_conf = float(self.clean_detect_conf)
        self.clean_detect_iou = float(self.clean_detect_iou)
        self.placement_mode = str(self.placement_mode or PLACEMENT_LARGEST_PERSON_TORSO).strip().lower()
        if self.placement_mode not in PLACEMENT_MODES:
            raise ValueError(
                f"placement_mode must be one of {sorted(PLACEMENT_MODES)}, "
                f"got: {self.placement_mode}"
            )
        self._artifact_provenance = self._load_artifact_provenance(self._artifact_path)

    @staticmethod
    def _artifact_sidecar_path(artifact_path: Path) -> Path:
        return artifact_path.with_name("patch_artifact.json")

    @staticmethod
    def _results_sidecar_path(artifact_path: Path) -> Path | None:
        if artifact_path.name != "patch.png":
            return None
        if artifact_path.parent.name != "patches":
            return None
        return artifact_path.parent.parent / "results.json"

    @staticmethod
    def _load_artifact_provenance(artifact_path: Path) -> dict[str, Any] | None:
        artifact_sidecar = PretrainedPatchAttackAdapter._artifact_sidecar_path(artifact_path)
        sidecar_candidates = [artifact_sidecar]
        legacy_sidecar = PretrainedPatchAttackAdapter._results_sidecar_path(artifact_path)
        if legacy_sidecar is not None:
            sidecar_candidates.append(legacy_sidecar)
        for sidecar_path in sidecar_candidates:
            if not sidecar_path.is_file():
                continue
            try:
                payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            provenance = {
                key: payload[key]
                for key in _ARTIFACT_PROVENANCE_KEYS
                if key in payload
            }
            if provenance:
                return provenance
        return None

    @staticmethod
    def _normalize_resize_to(value: tuple[int, int] | list[int] | None) -> tuple[int, int] | None:
        if value is None:
            return None
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("resize_to must be a 2-item [height, width] sequence.")
        height = int(value[0])
        width = int(value[1])
        if height <= 0 or width <= 0:
            raise ValueError("resize_to height and width must be positive integers.")
        return height, width

    @staticmethod
    def _resize_patch(patch_bgr: np.ndarray, size_hw: tuple[int, int]) -> np.ndarray:
        height, width = size_hw
        return cv2.resize(patch_bgr, (width, height), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _ensure_hwc_uint8(image: np.ndarray) -> None:
        if not isinstance(image, np.ndarray):
            raise ValueError("pretrained_patch expects a numpy.ndarray image.")
        if image.dtype != np.uint8:
            raise ValueError("pretrained_patch expects uint8 images.")
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("pretrained_patch expects HWC 3-channel images.")

    @staticmethod
    def _to_numpy_array(value: Any) -> np.ndarray:
        if value is None:
            return np.asarray([])
        current = value
        if hasattr(current, "detach"):
            current = current.detach()
        if hasattr(current, "cpu"):
            current = current.cpu()
        if hasattr(current, "numpy"):
            current = current.numpy()
        return np.asarray(current)

    def _detect_person_boxes(self, image_bgr: np.ndarray, model: Any | None) -> list[list[float]]:
        yolo = getattr(model, "_model", None)
        if yolo is None or not hasattr(yolo, "predict"):
            return []
        clean_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = yolo.predict(
            source=clean_rgb,
            save=False,
            verbose=False,
            conf=self.clean_detect_conf,
            iou=self.clean_detect_iou,
            classes=[self.person_class_id],
        )
        if not results:
            return []
        boxes = getattr(results[0], "boxes", None)
        if boxes is None or getattr(boxes, "xyxy", None) is None:
            return []
        xyxy = self._to_numpy_array(getattr(boxes, "xyxy", None)).reshape(-1, 4)
        classes = self._to_numpy_array(getattr(boxes, "cls", None)).reshape(-1)
        output: list[list[float]] = []
        for index, row in enumerate(xyxy.tolist()):
            class_id = int(classes[index]) if index < len(classes) else self.person_class_id
            if class_id == self.person_class_id:
                output.append([float(v) for v in row[:4]])
        return output

    @staticmethod
    def _fit_patch_to_image(patch_bgr: np.ndarray, image_shape: tuple[int, int, int]) -> np.ndarray:
        img_h, img_w = image_shape[:2]
        patch_h, patch_w = patch_bgr.shape[:2]
        if patch_h <= img_h and patch_w <= img_w:
            return patch_bgr
        scale = min(img_h / max(patch_h, 1), img_w / max(patch_w, 1))
        new_h = max(1, int(np.floor(patch_h * scale)))
        new_w = max(1, int(np.floor(patch_w * scale)))
        return cv2.resize(patch_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _off_object_position(
        image_shape: tuple[int, int, int],
        patch_shape: tuple[int, int],
        *,
        margin_ratio: float = 0.05,
    ) -> tuple[int, int]:
        img_h, img_w = image_shape[:2]
        patch_h, patch_w = patch_shape
        top = int(np.clip(round(img_h * margin_ratio), 0, max(img_h - patch_h, 0)))
        left = int(np.clip(round(img_w * margin_ratio), 0, max(img_w - patch_w, 0)))
        return top, left

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        self._ensure_hwc_uint8(image)
        patch_bgr = self._fit_patch_to_image(self._base_patch_bgr, image.shape)
        patch_h, patch_w = patch_bgr.shape[:2]
        boxes = self._detect_person_boxes(image, model)
        person_found = bool(boxes)
        if self.placement_mode == PLACEMENT_OFF_OBJECT_FIXED:
            top, left = self._off_object_position(image.shape, (patch_h, patch_w))
            fallback_used = False
        elif person_found:
            x1, y1, x2, y2 = max(
                boxes,
                key=lambda box: (box[2] - box[0]) * (box[3] - box[1]),
            )
            cx = int((x1 + x2) / 2)
            cy = int(y1 + 0.35 * (y2 - y1))
            top = int(np.clip(cy - patch_h // 2, 0, image.shape[0] - patch_h))
            left = int(np.clip(cx - patch_w // 2, 0, image.shape[1] - patch_w))
            fallback_used = False
        else:
            top = image.shape[0] // 2 - patch_h // 2
            left = image.shape[1] // 2 - patch_w // 2
            fallback_used = True
        attacked = image.copy()
        attacked[top : top + patch_h, left : left + patch_w] = patch_bgr
        metadata: dict[str, Any] = {
            "attack": "pretrained_patch",
            "artifact_path": str(self._artifact_path),
            "artifact_sha256": self._artifact_sha256,
            "artifact_size": [self._artifact_size[0], self._artifact_size[1]],
            "applied_patch_size": [
                int(self._base_patch_bgr.shape[0]),
                int(self._base_patch_bgr.shape[1]),
            ],
            "placement_mode": self.placement_mode,
            "fallback_mode": self.fallback_mode,
            "clean_detect_conf": self.clean_detect_conf,
            "clean_detect_iou": self.clean_detect_iou,
            "prediction_metadata": {
                "name": "pretrained_patch",
                "top": int(top),
                "left": int(left),
                "person_found": person_found,
                "applied_patch_size": [int(patch_h), int(patch_w)],
                "fallback_used": fallback_used,
                "placement_mode": self.placement_mode,
            },
        }
        if self._artifact_provenance is not None:
            metadata["artifact_provenance"] = dict(self._artifact_provenance)
        return attacked, metadata
