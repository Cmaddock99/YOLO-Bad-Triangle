from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
from typing import Generic, TypeVar

from .plugin_registry import PluginRegistry

T = TypeVar("T")


class AdapterLoader(Generic[T]):
    """Lazy loader that discovers and imports ``*_adapter`` modules from a package,
    then exposes build and list operations backed by a :class:`PluginRegistry`.

    Usage::

        _loader: AdapterLoader[BaseAttack] = AdapterLoader(
            "lab.attacks", "attack", _registry
        )
        build_attack_plugin = _loader.build
        list_available_attack_plugins = _loader.list_available
    """

    def __init__(
        self, package_name: str, label: str, registry: PluginRegistry[T]
    ) -> None:
        self._package_name = package_name
        self._label = label
        self._registry = registry
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        package = import_module(self._package_name)
        loaded = []
        for module in iter_modules(package.__path__):
            if not module.name.endswith("_adapter"):
                continue
            import_module(f"{package.__name__}.{module.name}")
            loaded.append(module.name)
        if not loaded:
            raise RuntimeError(
                f"No {self._label} adapter plugins were loaded. "
                "Check that plugin files follow the *_adapter.py naming convention."
            )
        self._loaded = True

    def build(self, name: str, **kwargs: object) -> T:
        self._load()
        cls = self._registry.get(name)
        if cls is None:
            supported = ", ".join(self._registry.list())
            raise ValueError(
                f"Unsupported {self._label} plugin '{name}'. Supported: {supported}"
            )
        return cls(**kwargs)  # type: ignore[call-arg]

    def list_available(self) -> list[str]:
        self._load()
        return self._registry.list()
