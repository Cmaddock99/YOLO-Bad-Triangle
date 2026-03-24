from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lab.eval.prediction_schema import PredictionRecord
from .base_model import BaseModel
from .framework_registry import register_model


@dataclass
@register_model("faster_rcnn", "torchvision_frcnn")
class FasterRCNNAdapter(BaseModel):
    """Framework Faster R-CNN adapter using torchvision pretrained weights.

    Output class IDs are remapped from torchvision's 1-indexed COCO category
    IDs to the framework's 0-indexed convention (torchvision_id - 1).

    Gradient-based attacks (FGSM/PGD/CW) are out of scope: eval-mode Faster
    R-CNN returns list[dict], not a confidence tensor, so _compute_loss cannot
    extract a differentiable signal. Square Attack works since it is black-box.
    """

    model: str = "fasterrcnn_resnet50_fpn"
    pretrained: bool = True
    score_threshold: float = 0.5
    name: str = "faster_rcnn"
    _model: Any = field(init=False, repr=False, default=None)

    def load(self) -> None:
        try:
            from torchvision.models.detection import fasterrcnn_resnet50_fpn
        except ImportError as exc:
            raise ImportError(
                "torchvision is required for FasterRCNNAdapter. "
                "Install it with: pip install torchvision"
            ) from exc

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            if self.pretrained:
                self._model = fasterrcnn_resnet50_fpn(pretrained=True).eval()
            else:
                # weights=None, weights_backbone=None avoids any network downloads
                try:
                    self._model = fasterrcnn_resnet50_fpn(
                        weights=None, weights_backbone=None
                    ).eval()
                except TypeError:
                    # Older torchvision that doesn't accept weights kwarg
                    self._model = fasterrcnn_resnet50_fpn(pretrained=False).eval()

    def _ensure_loaded(self) -> None:
        if self._model is None:
            self.load()

    def predict(self, images: Iterable[Path], **kwargs: Any) -> Sequence[PredictionRecord]:
        import torch
        import torchvision.transforms.functional as TF
        import cv2

        self._ensure_loaded()
        records: list[PredictionRecord] = []
        with torch.no_grad():
            for image_path in images:
                img_bgr = cv2.imread(str(image_path))
                if img_bgr is None:
                    records.append({
                        "image_id": Path(image_path).name,
                        "boxes": [],
                        "scores": [],
                        "class_ids": [],
                        "metadata": {"model": self.name, "error": "unreadable"},
                    })
                    continue

                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                tensor = TF.to_tensor(img_rgb)

                output = self._model([tensor])[0]

                boxes_raw = output["boxes"].cpu().tolist()
                scores_raw = output["scores"].cpu().tolist()
                labels_raw = output["labels"].cpu().tolist()

                # Filter by score threshold and remap 1-indexed → 0-indexed
                boxes: list[list[float]] = []
                scores: list[float] = []
                class_ids: list[int] = []
                for box, score, label in zip(boxes_raw, scores_raw, labels_raw):
                    if score >= self.score_threshold:
                        boxes.append([float(v) for v in box])
                        scores.append(float(score))
                        class_ids.append(int(label) - 1)  # torchvision is 1-indexed

                records.append({
                    "image_id": Path(image_path).name,
                    "boxes": boxes,
                    "scores": scores,
                    "class_ids": class_ids,
                    "metadata": {
                        "model": self.name,
                        "source_path": str(image_path),
                    },
                })
        return records

    def validate(self, dataset: Path | str, **kwargs: Any) -> dict[str, Any]:
        # Full COCO mAP evaluation via pycocotools is optional.
        # Return a not_supported stub so the runner still writes valid metrics.json.
        return {
            "mAP50": None,
            "mAP50-95": None,
            "precision": None,
            "recall": None,
            "_status": "not_supported",
        }
