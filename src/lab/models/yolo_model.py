from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ultralytics import YOLO


@dataclass
class YOLOModel:
    model_path: str
    _model: YOLO = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._model = YOLO(self.model_path)

    def predict(self, **kwargs: Any) -> Any:
        return self._model.predict(**kwargs)

    def validate(self, **kwargs: Any) -> Any:
        return self._model.val(**kwargs)

