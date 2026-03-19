from __future__ import annotations

from importlib import import_module
from typing import Any

from .base_model import BaseModel
from .model_utils import model_label_from_path, normalize_model_path
from .plugin_registry import get_model_class, list_registered_models, register_model

__all__ = [
    "BaseModel",
    "YOLOModel",
    "register_model",
    "get_model_class",
    "list_registered_models",
    "model_label_from_path",
    "normalize_model_path",
]


def __getattr__(name: str) -> Any:
    if name == "YOLOModel":
        module = import_module(".yolo_model", __name__)
        return getattr(module, name)
    if name == "YOLOModelAdapter":
        module = import_module(".yolo_adapter", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

