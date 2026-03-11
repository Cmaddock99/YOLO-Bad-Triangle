from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
from typing import Any

from .base import Defense, get_defense_class, list_registered_defenses

_BUILTINS_LOADED = False


def _load_builtin_defenses() -> None:
    global _BUILTINS_LOADED
    if _BUILTINS_LOADED:
        return

    package = import_module("lab.defenses")
    for module in iter_modules(package.__path__):
        if module.name in {"__init__", "base", "registry"}:
            continue
        import_module(f"{package.__name__}.{module.name}")
    _BUILTINS_LOADED = True


def build_defense(name: str, params: dict[str, Any] | None = None) -> Defense:
    _load_builtin_defenses()
    params = params or {}
    defense_cls = get_defense_class(name)
    if defense_cls is None:
        supported = ", ".join(list_registered_defenses())
        raise ValueError(f"Unsupported defense '{name}'. Supported defenses: {supported}")
    return defense_cls(**params)

