from __future__ import annotations

from ..catalog import build_plugin_inventory


def list_extra_attack_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["attacks"]["extra"])


def list_extra_defense_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["defenses"]["extra"])


def list_extra_model_plugins(profile_name: str = "yolo11n_lab_v1") -> list[str]:
    inventory = build_plugin_inventory(profile_name)
    return list(inventory["models"]["extra"])


__all__ = [
    "list_extra_attack_plugins",
    "list_extra_defense_plugins",
    "list_extra_model_plugins",
]
