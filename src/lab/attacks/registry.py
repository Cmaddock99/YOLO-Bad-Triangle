from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
from typing import Any

from .base import Attack, get_attack_class, list_registered_attacks

_BUILTINS_LOADED = False


def _load_builtin_attacks() -> None:
    global _BUILTINS_LOADED
    if _BUILTINS_LOADED:
        return

    package = import_module("lab.attacks")
    for module in iter_modules(package.__path__):
        if module.name in {"__init__", "base", "registry", "utils"}:
            continue
        import_module(f"{package.__name__}.{module.name}")
    _BUILTINS_LOADED = True


def build_attack(name: str, params: dict[str, Any] | None = None) -> Attack:
    _load_builtin_attacks()
    params = params or {}
    attack_cls = get_attack_class(name)
    if attack_cls is None:
        supported = ", ".join(list_registered_attacks())
        raise ValueError(f"Unsupported attack '{name}'. Supported attacks: {supported}")
    return attack_cls(**params)

