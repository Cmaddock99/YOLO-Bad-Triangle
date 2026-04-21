from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from lab.eval.prediction_adapter import normalize_ultralytics_result
from lab.eval.prediction_schema import PredictionRecord
from lab.models.base_model import BaseModel
from lab.models.framework_registry import register_model
from lab.models.model_utils import model_label_from_path, normalize_model_path


@dataclass
@register_model("yolo", "ultralytics_yolo")
class YOLOModelAdapter(BaseModel):
    """Framework YOLO model plugin."""

    model: str | None = None
    name: str = "yolo_adapter"
    _model: YOLO = field(init=False, repr=False)
    _model_label: str = field(init=False, repr=False)

    def load(self) -> None:
        model_path = normalize_model_path(self.model)
        self._model_label = model_label_from_path(model_path)
        self._model = YOLO(model_path)

    def _ensure_loaded(self) -> None:
        if not hasattr(self, "_model"):
            self.load()

    def predict(self, images: list[Path], **kwargs: Any) -> list[PredictionRecord]:
        self._ensure_loaded()
        sources = [str(path) for path in images]
        results = self._model.predict(source=sources, save=False, **kwargs)
        return [
            normalize_ultralytics_result(result, model_name=self._model_label)
            for result in results
        ]

    def validate(self, dataset: Path | str, **kwargs: Any) -> dict[str, Any]:
        self._ensure_loaded()
        results = self._model.val(data=str(dataset), **kwargs)
        box = getattr(results, "box", None)
        if box is None:
            return {"precision": None, "recall": None, "mAP50": None, "mAP50-95": None}

        def _to_float_or_none(val: object) -> float | None:
            return float(val) if val is not None else None

        return {
            "precision": _to_float_or_none(getattr(box, "mp", None)),
            "recall": _to_float_or_none(getattr(box, "mr", None)),
            "mAP50": _to_float_or_none(getattr(box, "map50", None)),
            "mAP50-95": _to_float_or_none(getattr(box, "map", None)),
        }
