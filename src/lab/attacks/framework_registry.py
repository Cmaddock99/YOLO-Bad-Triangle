from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules

from .base_attack import BaseAttack
from .plugin_registry import get_attack_plugin, list_attack_plugins

_PLUGINS_LOADED = False


def _load_builtin_attack_plugins() -> None:
    global _PLUGINS_LOADED
    if _PLUGINS_LOADED:
        return
    package = import_module("lab.attacks")
    for module in iter_modules(package.__path__):
        if not module.name.endswith("_adapter"):
            continue
        import_module(f"{package.__name__}.{module.name}")
    _PLUGINS_LOADED = True


def build_attack_plugin(name: str, **kwargs: object) -> BaseAttack:
    _load_builtin_attack_plugins()
    attack_cls = get_attack_plugin(name)
    if attack_cls is None:
        supported = ", ".join(list_attack_plugins())
        raise ValueError(f"Unsupported attack plugin '{name}'. Supported: {supported}")
    return attack_cls(**kwargs)


def list_available_attack_plugins() -> list[str]:
    _load_builtin_attack_plugins()
    return list_attack_plugins()
