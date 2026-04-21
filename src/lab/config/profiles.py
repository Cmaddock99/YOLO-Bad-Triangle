from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_PROFILES_PATH = _REPO_ROOT / "configs" / "pipeline_profiles.yaml"
_NONE_LIKE = {"", "none", "identity"}
_STATUS_ORDER = {"canonical": 0, "manual_only": 1, "incompatible": 2}


def default_profiles_path() -> Path:
    return _DEFAULT_PROFILES_PATH


def _normalize_name(value: object) -> str:
    return str(value or "").strip().lower()


def _as_mapping(value: Any, *, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping for {label}.")
    return cast(dict[str, Any], value)


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping config in {path}")
    return cast(dict[str, Any], loaded)


def _normalize_catalog(section: dict[str, Any], *, label: str) -> dict[str, list[str]]:
    canonical = section.get("canonical") or []
    manual_only = section.get("manual_only") or []
    if not isinstance(canonical, list) or not isinstance(manual_only, list):
        raise ValueError(f"{label}.canonical and {label}.manual_only must be lists.")
    normalized_canonical = [_normalize_name(item) for item in canonical if _normalize_name(item)]
    normalized_manual = [_normalize_name(item) for item in manual_only if _normalize_name(item)]
    return {
        "canonical": list(dict.fromkeys(normalized_canonical)),
        "manual_only": list(dict.fromkeys(normalized_manual)),
    }


def load_pipeline_profiles(*, profiles_path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = (profiles_path or default_profiles_path()).expanduser().resolve()
    payload = _load_yaml_mapping(path)
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"Expected top-level 'profiles' mapping in {path}")
    return {
        str(name): _as_mapping(value, label=f"profile {name}")
        for name, value in profiles.items()
    }


def load_pipeline_profile(name: str, *, profiles_path: Path | None = None) -> dict[str, Any]:
    profiles = load_pipeline_profiles(profiles_path=profiles_path)
    profile_name = str(name or "").strip()
    if not profile_name:
        raise ValueError("Profile name is required.")
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown pipeline profile '{profile_name}'. Available: {available}")
    profile = deepcopy(profiles[profile_name])
    for required_key in ("model", "data", "predict", "validation", "attacks", "defenses", "authoritative_metric", "fortify_mode", "learned_defense"):
        if required_key not in profile:
            raise ValueError(f"Profile '{profile_name}' missing required key '{required_key}'.")
    profile["attacks"] = _normalize_catalog(_as_mapping(profile.get("attacks"), label=f"{profile_name}.attacks"), label=f"{profile_name}.attacks")
    profile["defenses"] = _normalize_catalog(_as_mapping(profile.get("defenses"), label=f"{profile_name}.defenses"), label=f"{profile_name}.defenses")
    return profile


def build_profile_config(name: str, *, profiles_path: Path | None = None) -> dict[str, Any]:
    profile = load_pipeline_profile(name, profiles_path=profiles_path)
    config = {
        "model": deepcopy(_as_mapping(profile.get("model"), label=f"{name}.model")),
        "data": deepcopy(_as_mapping(profile.get("data"), label=f"{name}.data")),
        "attack": {"name": "none", "params": {}},
        "defense": {"name": "none", "params": {}},
        "predict": deepcopy(_as_mapping(profile.get("predict"), label=f"{name}.predict")),
        "validation": {
            "enabled": False,
            **deepcopy(_as_mapping(profile.get("validation"), label=f"{name}.validation")),
        },
        "summary": {
            "enabled": False,
            **deepcopy(_as_mapping(profile.get("summary"), label=f"{name}.summary")),
        },
        "runner": {
            "seed": 42,
            "max_images": 8,
            "output_root": "outputs/framework_runs",
            **deepcopy(_as_mapping(profile.get("runner"), label=f"{name}.runner")),
        },
        "pipeline_profile": {
            "name": name,
            "authoritative_metric": str(profile.get("authoritative_metric")),
            "fortify_mode": deepcopy(_as_mapping(profile.get("fortify_mode"), label=f"{name}.fortify_mode")),
            "learned_defense": deepcopy(_as_mapping(profile.get("learned_defense"), label=f"{name}.learned_defense")),
            "attacks": deepcopy(_as_mapping(profile.get("attacks"), label=f"{name}.attacks")),
            "defenses": deepcopy(_as_mapping(profile.get("defenses"), label=f"{name}.defenses")),
            "model": deepcopy(_as_mapping(profile.get("model"), label=f"{name}.model")),
        },
    }
    return config


def resolve_framework_config(
    *,
    config_path: Path | None = None,
    profile_name: str | None = None,
    profiles_path: Path | None = None,
) -> tuple[dict[str, Any], Path | None]:
    if profile_name and config_path is not None:
        raise ValueError("Choose either config_path or profile_name, not both.")
    if profile_name:
        return build_profile_config(profile_name, profiles_path=profiles_path), None
    if config_path is None:
        raise ValueError("config_path or profile_name is required.")
    return _load_yaml_mapping(config_path), config_path


def pipeline_profile_metadata(config: dict[str, Any]) -> dict[str, Any] | None:
    payload = config.get("pipeline_profile")
    if not isinstance(payload, dict):
        return None
    name = str(payload.get("name") or "").strip()
    if not name:
        return None
    return cast(dict[str, Any], payload)


def pipeline_profile_name(config: dict[str, Any]) -> str | None:
    payload = pipeline_profile_metadata(config)
    if payload is None:
        return None
    name = str(payload.get("name") or "").strip()
    return name or None


def authoritative_metric(config: dict[str, Any]) -> str | None:
    payload = pipeline_profile_metadata(config)
    if payload is None:
        return None
    metric = str(payload.get("authoritative_metric") or "").strip()
    return metric or None


def _membership_status(
    selected_name: str,
    *,
    canonical: list[str],
    manual_only: list[str],
    allow_none_like: bool,
    label: str,
    profile_name: str,
) -> tuple[str, str]:
    normalized = _normalize_name(selected_name)
    if allow_none_like and normalized in _NONE_LIKE:
        return "canonical", f"{label} uses the baseline sentinel."
    if normalized in canonical:
        return "canonical", f"{label} '{normalized}' is canonical for {profile_name}."
    if normalized in manual_only:
        return "manual_only", f"{label} '{normalized}' is manual-only for {profile_name}."
    return "incompatible", f"{label} '{normalized or 'none'}' is not declared in {profile_name}."


def resolve_profile_compatibility(config: dict[str, Any]) -> dict[str, Any] | None:
    metadata = pipeline_profile_metadata(config)
    if metadata is None:
        return None
    profile_name = str(metadata["name"])
    attack_cfg = _as_mapping(config.get("attack"), label="attack")
    defense_cfg = _as_mapping(config.get("defense"), label="defense")
    model_cfg = _as_mapping(config.get("model"), label="model")
    attack_catalog = _normalize_catalog(_as_mapping(metadata.get("attacks"), label=f"{profile_name}.attacks"), label=f"{profile_name}.attacks")
    defense_catalog = _normalize_catalog(_as_mapping(metadata.get("defenses"), label=f"{profile_name}.defenses"), label=f"{profile_name}.defenses")

    attack_status, attack_reason = _membership_status(
        str(attack_cfg.get("name") or "none"),
        canonical=attack_catalog["canonical"],
        manual_only=attack_catalog["manual_only"],
        allow_none_like=True,
        label="attack",
        profile_name=profile_name,
    )
    defense_status, defense_reason = _membership_status(
        str(defense_cfg.get("name") or "none"),
        canonical=defense_catalog["canonical"],
        manual_only=defense_catalog["manual_only"],
        allow_none_like=True,
        label="defense",
        profile_name=profile_name,
    )

    expected_model = _normalize_name(
        _as_mapping(_as_mapping(metadata.get("model"), label=f"{profile_name}.model").get("params"), label=f"{profile_name}.model.params").get("model")
    )
    selected_model = _normalize_name(
        _as_mapping(model_cfg.get("params"), label="model.params").get("model")
    )
    if expected_model and selected_model and expected_model == selected_model:
        model_status = "canonical"
        model_reason = f"model '{selected_model}' matches {profile_name}."
    else:
        model_status = "incompatible"
        model_reason = (
            f"model '{selected_model or 'unspecified'}' does not match "
            f"{profile_name} expected '{expected_model or 'unspecified'}'."
        )

    reasons = [model_reason, attack_reason, defense_reason]
    status = "canonical"
    for candidate in (model_status, attack_status, defense_status):
        if _STATUS_ORDER[candidate] > _STATUS_ORDER[status]:
            status = candidate
    return {
        "status": status,
        "model_status": model_status,
        "attack_status": attack_status,
        "defense_status": defense_status,
        "reasons": reasons,
    }


def should_include_extra_plugins(config: dict[str, Any]) -> bool:
    if pipeline_profile_name(config) is None:
        return True
    compatibility = resolve_profile_compatibility(config)
    if compatibility is None:
        return True
    return str(compatibility.get("status") or "").strip().lower() != "canonical"


def learned_defense_compatibility(profile_name: str, *, profiles_path: Path | None = None) -> dict[str, Any]:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    learned_defense = _as_mapping(profile.get("learned_defense"), label=f"{profile_name}.learned_defense")
    trainable = bool(learned_defense.get("trainable", False))
    return {
        "status": "compatible" if trainable else "incompatible",
        "trainable": trainable,
        "default_defense": str(learned_defense.get("default_defense") or "").strip() or None,
        "reason": str(
            learned_defense.get("reason")
            or (
                f"{profile_name} supports a trainable learned-defense path."
                if trainable
                else f"{profile_name} does not support a trainable learned-defense path."
            )
        ),
    }


def profile_canonical_attacks(profile_name: str, *, profiles_path: Path | None = None) -> list[str]:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    return list(_as_mapping(profile.get("attacks"), label=f"{profile_name}.attacks").get("canonical") or [])


def profile_canonical_defenses(profile_name: str, *, profiles_path: Path | None = None) -> list[str]:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    return list(_as_mapping(profile.get("defenses"), label=f"{profile_name}.defenses").get("canonical") or [])


def profile_manual_only_attacks(profile_name: str, *, profiles_path: Path | None = None) -> list[str]:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    return list(_as_mapping(profile.get("attacks"), label=f"{profile_name}.attacks").get("manual_only") or [])


def profile_manual_only_defenses(profile_name: str, *, profiles_path: Path | None = None) -> list[str]:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    return list(_as_mapping(profile.get("defenses"), label=f"{profile_name}.defenses").get("manual_only") or [])


def profile_model_name(profile_name: str, *, profiles_path: Path | None = None) -> str:
    profile = load_pipeline_profile(profile_name, profiles_path=profiles_path)
    return str(_as_mapping(profile.get("model"), label=f"{profile_name}.model").get("name") or "").strip()
