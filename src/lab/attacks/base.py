from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TypeVar


class Attack(ABC):
    name: str = "attack"

    @abstractmethod
    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        """Transforms source images and returns the output directory."""


AttackType = TypeVar("AttackType", bound=type[Attack])
_ATTACK_REGISTRY: dict[str, type[Attack]] = {}


def register_attack(*names: str) -> Callable[[AttackType], AttackType]:
    if not names:
        raise ValueError("register_attack requires at least one name.")

    def decorator(attack_cls: AttackType) -> AttackType:
        for name in names:
            key = name.strip().lower()
            if not key:
                continue
            _ATTACK_REGISTRY[key] = attack_cls
        return attack_cls

    return decorator


def get_attack_class(name: str) -> type[Attack] | None:
    return _ATTACK_REGISTRY.get(name.strip().lower())


def list_registered_attacks() -> list[str]:
    return sorted(_ATTACK_REGISTRY)

