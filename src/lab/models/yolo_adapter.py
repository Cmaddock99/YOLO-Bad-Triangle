from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lab.eval.prediction_adapter import normalize_ultralytics_result
from lab.eval.prediction_schema import PredictionRecord
from .base_model import BaseModel
from .plugin_registry import register_model
from .yolo_model import YOLOModel


@dataclass
@register_model("yolo", "ultralytics_yolo")
class YOLOModelAdapter(BaseModel):
    """Framework adapter that wraps the existing YOLOModel implementation."""

    model: str | None = None
    name: str = "yolo_adapter"
    _legacy: YOLOModel = field(init=False, repr=False)

    def load(self) -> None:
        self._legacy = YOLOModel(self.model)

    def _ensure_loaded(self) -> None:
        if not hasattr(self, "_legacy"):
            self.load()

    def predict(self, images: list[Path], **kwargs: Any) -> list[PredictionRecord]:
        self._ensure_loaded()
        sources = [str(path) for path in images]
        results = self._legacy.predict(source=sources, save=False, **kwargs)
        return [
            normalize_ultralytics_result(result, model_name=self._legacy.model_label)
            for result in results
        ]

    def validate(self, dataset: Path | str, **kwargs: Any) -> dict[str, Any]:
        self._ensure_loaded()
        results = self._legacy.validate(data=str(dataset), **kwargs)
        box = getattr(results, "box", None)
        if box is None:
            return {"precision": None, "recall": None, "mAP50": None, "mAP50-95": None}
        return {
            "precision": float(getattr(box, "mp", 0.0)),
            "recall": float(getattr(box, "mr", 0.0)),
            "mAP50": float(getattr(box, "map50", 0.0)),
            "mAP50-95": float(getattr(box, "map", 0.0)),
        }
