from __future__ import annotations

from typing import Callable, TypeVar

from .base_defense import BaseDefense

DefenseType = TypeVar("DefenseType", bound=type[BaseDefense])
_DEFENSE_PLUGIN_REGISTRY: dict[str, type[BaseDefense]] = {}


def register_defense_plugin(*names: str) -> Callable[[DefenseType], DefenseType]:
    """Register one defense class under one or more aliases."""
    if not names:
        raise ValueError("register_defense_plugin requires at least one alias.")

    def decorator(defense_cls: DefenseType) -> DefenseType:
        for name in names:
            key = name.strip().lower()
            if key:
                _DEFENSE_PLUGIN_REGISTRY[key] = defense_cls
        return defense_cls

    return decorator


def get_defense_plugin(name: str) -> type[BaseDefense] | None:
    return _DEFENSE_PLUGIN_REGISTRY.get(name.strip().lower())


def list_defense_plugins() -> list[str]:
    return sorted(_DEFENSE_PLUGIN_REGISTRY)
