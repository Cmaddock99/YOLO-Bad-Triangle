from __future__ import annotations

from typing import Callable, TypeVar

from .base_attack import BaseAttack

AttackType = TypeVar("AttackType", bound=type[BaseAttack])
_ATTACK_PLUGIN_REGISTRY: dict[str, type[BaseAttack]] = {}


def register_attack_plugin(*names: str) -> Callable[[AttackType], AttackType]:
    """Register one attack class under one or more aliases."""
    if not names:
        raise ValueError("register_attack_plugin requires at least one alias.")

    def decorator(attack_cls: AttackType) -> AttackType:
        for name in names:
            key = name.strip().lower()
            if key:
                _ATTACK_PLUGIN_REGISTRY[key] = attack_cls
        return attack_cls

    return decorator


def get_attack_plugin(name: str) -> type[BaseAttack] | None:
    return _ATTACK_PLUGIN_REGISTRY.get(name.strip().lower())


def list_attack_plugins() -> list[str]:
    return sorted(_ATTACK_PLUGIN_REGISTRY)
