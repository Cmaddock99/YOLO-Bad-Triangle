from __future__ import annotations

from lab.attacks.framework_registry import list_available_attack_plugins
from lab.config.profiles import (
    profile_canonical_attacks,
    profile_canonical_defenses,
    profile_manual_only_attacks,
    profile_manual_only_defenses,
    profile_model_name,
)
from lab.defenses.framework_registry import list_available_defense_plugins
from lab.models.framework_registry import list_available_models

_DEFAULT_PROFILE = "yolo11n_lab_v1"
_BASELINE_SENTINELS = {
    "attack": ["none"],
    "defense": ["none", "identity"],
}
_EXTRA_MODEL_PREFERRED_NAMES = ["faster_rcnn"]


def _intersect_preferred(preferred: list[str], available: list[str]) -> list[str]:
    available_names = {str(name).strip() for name in available}
    return [name for name in preferred if name in available_names]


def build_plugin_inventory(profile_name: str = _DEFAULT_PROFILE) -> dict[str, object]:
    attack_aliases = list_available_attack_plugins()
    defense_aliases = list_available_defense_plugins()
    model_aliases = list_available_models()

    model_name = profile_model_name(profile_name)
    attack_core = _intersect_preferred(
        profile_canonical_attacks(profile_name),
        attack_aliases,
    )
    attack_extra = _intersect_preferred(
        profile_manual_only_attacks(profile_name),
        attack_aliases,
    )
    defense_core = [
        name
        for name in _intersect_preferred(
            profile_canonical_defenses(profile_name),
            defense_aliases,
        )
        if name not in {"none", "identity"}
    ]
    defense_extra = _intersect_preferred(
        profile_manual_only_defenses(profile_name),
        defense_aliases,
    )
    model_core = _intersect_preferred([model_name] if model_name else [], model_aliases)
    model_extra = _intersect_preferred(_EXTRA_MODEL_PREFERRED_NAMES, model_aliases)

    return {
        "profile": profile_name,
        "baseline_sentinels": {
            "attack": list(_BASELINE_SENTINELS["attack"]),
            "defense": list(_BASELINE_SENTINELS["defense"]),
        },
        "models": {
            "core": model_core,
            "extra": model_extra,
            "all_aliases": model_aliases,
        },
        "attacks": {
            "core": attack_core,
            "extra": attack_extra,
            "all_aliases": attack_aliases,
        },
        "defenses": {
            "core": defense_core,
            "extra": defense_extra,
            "all_aliases": defense_aliases,
        },
    }


__all__ = ["build_plugin_inventory"]
