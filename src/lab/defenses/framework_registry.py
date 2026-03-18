from __future__ import annotations

from importlib import import_module

from .base_defense import BaseDefense
from .plugin_registry import get_defense_plugin, list_defense_plugins

_PLUGINS_LOADED = False


def _load_builtin_defense_plugins() -> None:
    global _PLUGINS_LOADED
    if _PLUGINS_LOADED:
        return
    import_module("lab.defenses.none_adapter")
    _PLUGINS_LOADED = True


def build_defense_plugin(name: str, **kwargs: object) -> BaseDefense:
    _load_builtin_defense_plugins()
    defense_cls = get_defense_plugin(name)
    if defense_cls is None:
        supported = ", ".join(list_defense_plugins())
        raise ValueError(f"Unsupported defense plugin '{name}'. Supported: {supported}")
    return defense_cls(**kwargs)


def list_available_defense_plugins() -> list[str]:
    _load_builtin_defense_plugins()
    return list_defense_plugins()
