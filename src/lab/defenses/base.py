from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TypeVar


class Defense(ABC):
    name: str = "defense"

    @abstractmethod
    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        """Applies defense preprocessing and returns output directory."""


DefenseType = TypeVar("DefenseType", bound=type[Defense])
_DEFENSE_REGISTRY: dict[str, type[Defense]] = {}


def register_defense(*names: str) -> Callable[[DefenseType], DefenseType]:
    if not names:
        raise ValueError("register_defense requires at least one name.")

    def decorator(defense_cls: DefenseType) -> DefenseType:
        for name in names:
            key = name.strip().lower()
            if not key:
                continue
            _DEFENSE_REGISTRY[key] = defense_cls
        return defense_cls

    return decorator


def get_defense_class(name: str) -> type[Defense] | None:
    return _DEFENSE_REGISTRY.get(name.strip().lower())


def list_registered_defenses() -> list[str]:
    return sorted(_DEFENSE_REGISTRY)

