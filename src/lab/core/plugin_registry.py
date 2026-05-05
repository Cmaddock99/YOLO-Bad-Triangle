from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class PluginRegistry(Generic[T]):
    """Generic decorator-based registry mapping string aliases to classes.

    Usage::

        _registry: PluginRegistry[BaseAttack] = PluginRegistry("attack")
        register_attack_plugin = _registry.register

        @register_attack_plugin("fgsm")
        class FGSMAdapter(BaseAttack): ...
    """

    def __init__(self, label: str) -> None:
        self._label = label
        self._store: dict[str, type[T]] = {}

    def register(self, *names: str) -> Callable[[type[T]], type[T]]:
        """Decorator: register a class under one or more aliases."""
        if not names:
            raise ValueError(
                f"register requires at least one alias for {self._label} plugin."
            )

        def decorator(cls: type[T]) -> type[T]:
            for name in names:
                key = name.strip().lower()
                if key:
                    existing = self._store.get(key)
                    if existing is not None and existing is not cls:
                        raise ValueError(
                            f"Duplicate {self._label} plugin alias '{key}': "
                            f"{cls} conflicts with existing registration {existing}."
                        )
                    self._store[key] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[T] | None:
        return self._store.get(name.strip().lower())

    def list(self) -> list[str]:
        return sorted(self._store)
