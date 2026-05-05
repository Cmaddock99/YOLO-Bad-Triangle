from __future__ import annotations

from importlib import import_module
from typing import Any

from .base_model import BaseModel
from .framework_registry import get_model_class, list_registered_models, register_model
from .model_utils import model_label_from_path, normalize_model_path

__all__ = [
    "BaseModel",
    "YOLOModel",
    "YOLOModelAdapter",
    "get_model_class",
    "list_registered_models",
    "model_label_from_path",
    "normalize_model_path",
    "register_model",
]


def __getattr__(name: str) -> Any:
    if name == "YOLOModel":
        module = import_module(".yolo_adapter", __name__)
        return module.YOLOModelAdapter
    if name == "YOLOModelAdapter":
        module = import_module(".yolo_adapter", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

