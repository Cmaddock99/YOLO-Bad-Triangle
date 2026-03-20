from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules

from .base_defense import BaseDefense
from .plugin_registry import get_defense_plugin, list_defense_plugins

_PLUGINS_LOADED = False


def _load_builtin_defense_plugins() -> None:
    global _PLUGINS_LOADED
    if _PLUGINS_LOADED:
        return
    package = import_module("lab.defenses")
    loaded = []
    for module in iter_modules(package.__path__):
        if not module.name.endswith("_adapter"):
            continue
        import_module(f"{package.__name__}.{module.name}")
        loaded.append(module.name)
    if not loaded:
        raise RuntimeError(
            "No defense adapter plugins were loaded. "
            "Check that plugin files follow the *_adapter.py naming convention."
        )
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
