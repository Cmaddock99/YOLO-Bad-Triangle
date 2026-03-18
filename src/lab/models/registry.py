from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules

from .base_model import BaseModel
from .plugin_registry import get_model_class, list_registered_models

_MODELS_LOADED = False


def _load_builtin_models() -> None:
    global _MODELS_LOADED
    if _MODELS_LOADED:
        return
    package = import_module("lab.models")
    for module in iter_modules(package.__path__):
        if not module.name.endswith("_adapter"):
            continue
        import_module(f"{package.__name__}.{module.name}")
    _MODELS_LOADED = True


def build_model(name: str, **kwargs: object) -> BaseModel:
    _load_builtin_models()
    model_cls = get_model_class(name)
    if model_cls is None:
        supported = ", ".join(list_registered_models())
        raise ValueError(f"Unsupported model '{name}'. Supported models: {supported}")
    return model_cls(**kwargs)


def list_available_models() -> list[str]:
    _load_builtin_models()
    return list_registered_models()
