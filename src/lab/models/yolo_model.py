from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ultralytics import YOLO
from .model_utils import model_label_from_path, normalize_model_path


@dataclass
class YOLOModel:
    model: str | None = None
    model_path: str = field(init=False)
    model_label: str = field(init=False)
    _model: YOLO = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.model_path = normalize_model_path(self.model)
        self.model_label = model_label_from_path(self.model_path)
        self._model = YOLO(self.model_path)

    def predict(self, **kwargs: Any) -> Any:
        return self._model.predict(**kwargs)

    def validate(self, **kwargs: Any) -> Any:
        return self._model.val(**kwargs)

