from __future__ import annotations

from importlib import import_module
from typing import Any

from .model_utils import model_label_from_path, normalize_model_path

__all__ = ["YOLOModel", "model_label_from_path", "normalize_model_path"]


def __getattr__(name: str) -> Any:
    if name == "YOLOModel":
        module = import_module(".yolo_model", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

