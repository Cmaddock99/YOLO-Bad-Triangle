from __future__ import annotations

from typing import Callable, TypeVar

from .base_model import BaseModel

ModelType = TypeVar("ModelType", bound=type[BaseModel])
_MODEL_REGISTRY: dict[str, type[BaseModel]] = {}


def register_model(*names: str) -> Callable[[ModelType], ModelType]:
    """Register one model class under one or more aliases."""
    if not names:
        raise ValueError("register_model requires at least one alias.")

    def decorator(model_cls: ModelType) -> ModelType:
        for name in names:
            key = name.strip().lower()
            if key:
                _MODEL_REGISTRY[key] = model_cls
        return model_cls

    return decorator


def get_model_class(name: str) -> type[BaseModel] | None:
    return _MODEL_REGISTRY.get(name.strip().lower())


def list_registered_models() -> list[str]:
    return sorted(_MODEL_REGISTRY)
