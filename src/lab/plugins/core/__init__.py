from __future__ import annotations

from lab.attacks.framework_registry import build_attack_plugin, list_available_attack_plugins
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins
from lab.models.framework_registry import build_model, list_available_models

from ..catalog import build_plugin_inventory


def list_core_attack_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["attacks"]["core"])


def list_core_defense_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["defenses"]["core"])


def list_core_model_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["models"]["core"])


def build_core_attack_plugin(name: str, **kwargs: object):
    return build_attack_plugin(name, include_extra=False, **kwargs)


def build_core_defense_plugin(name: str, **kwargs: object):
    return build_defense_plugin(name, include_extra=False, **kwargs)


def build_core_model(name: str, **kwargs: object):
    return build_model(name, include_extra=False, **kwargs)


def list_core_attack_aliases() -> list[str]:
    return list_available_attack_plugins(include_extra=False)


def list_core_defense_aliases() -> list[str]:
    return list_available_defense_plugins(include_extra=False)


def list_core_model_aliases() -> list[str]:
    return list_available_models(include_extra=False)


__all__ = [
    "build_core_attack_plugin",
    "build_core_defense_plugin",
    "build_core_model",
    "list_core_attack_aliases",
    "list_core_attack_plugins",
    "list_core_defense_aliases",
    "list_core_defense_plugins",
    "list_core_model_aliases",
    "list_core_model_plugins",
]
