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
        self,
        package_name: str | tuple[str, ...],
        label: str,
        registry: PluginRegistry[T],
        *,
        core_package_names: tuple[str, ...] | None = None,
        extra_package_names: tuple[str, ...] | None = None,
    ) -> None:
        if isinstance(package_name, str):
            self._package_names: tuple[str, ...] = (package_name,)
        else:
            self._package_names = tuple(package_name)
        self._label = label
        self._registry = registry
        self._core_package_names: tuple[str, ...] = (
            self._package_names
            if core_package_names is None
            else tuple(core_package_names)
        )
        self._extra_package_names: tuple[str, ...] = (
            ()
            if extra_package_names is None
            else tuple(extra_package_names)
        )
        self._core_loaded = False
        self._extra_loaded = False
        self._scoped_aliases: dict[str, set[str]] = {"core": set(), "extra": set()}

    @property
    def package_names(self) -> tuple[str, ...]:
        return self._package_names

    @property
    def core_package_names(self) -> tuple[str, ...]:
        return self._core_package_names

    @property
    def extra_package_names(self) -> tuple[str, ...]:
        return self._extra_package_names

    def _load(self) -> None:
        self._load_core()
        self._load_extra()

    def _load_core(self) -> None:
        self._load_scope("core")

    def _load_extra(self) -> None:
        self._load_scope("extra")

    def _load_scope(self, scope: str) -> None:
        if scope == "core":
            if self._core_loaded:
                return
            package_names = self._core_package_names
        else:
            if self._extra_loaded:
                return
            package_names = self._extra_package_names

        if not package_names:
            if scope == "core":
                self._core_loaded = True
            else:
                self._extra_loaded = True
            return

        loaded = []
        adapter_module_names: set[str] = set()
        for package_name in package_names:
            package = import_module(package_name)
            for module in iter_modules(package.__path__):
                if not module.name.endswith("_adapter"):
                    continue
                module_name = f"{package.__name__}.{module.name}"
                imported = import_module(module_name)
                loaded.append(module_name)
                adapter_module_names.add(imported.__name__)
                adapter_module_names.update(
                    module_name
                    for module_name in getattr(imported, "ADAPTER_MODULES", ())
                    if isinstance(module_name, str)
                )
        if not loaded:
            searched_packages = ", ".join(package_names)
            raise RuntimeError(
                f"No {self._label} adapter plugins were loaded. "
                f"Searched packages: {searched_packages}. "
                "Check that plugin files follow the *_adapter.py naming convention."
            )

        self._scoped_aliases[scope].update(
            alias
            for alias in self._registry.list()
            if (cls := self._registry.get(alias)) is not None
            and cls.__module__ in adapter_module_names
        )
        if scope == "core":
            self._core_loaded = True
        else:
            self._extra_loaded = True

    def _supported_aliases(self, *, include_extra: bool) -> list[str]:
        if include_extra:
            self._load()
            return self._registry.list()

        self._load_core()
        return sorted(self._scoped_aliases["core"])

    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    def build(self, name: str, *, include_extra: bool = True, **kwargs: object) -> T:
        supported_aliases = self._supported_aliases(include_extra=include_extra)
        normalized_name = self._normalize_name(name)
        if not include_extra and normalized_name not in self._scoped_aliases["core"]:
            supported = ", ".join(supported_aliases)
            raise ValueError(
                f"Unsupported {self._label} plugin '{name}'. Supported: {supported}"
            )

        cls = self._registry.get(name)
        if cls is None:
            supported = ", ".join(supported_aliases)
            raise ValueError(
                f"Unsupported {self._label} plugin '{name}'. Supported: {supported}"
            )
        return cls(**kwargs)  # type: ignore[call-arg]

    def list_available(self, *, include_extra: bool = True) -> list[str]:
        return self._supported_aliases(include_extra=include_extra)
