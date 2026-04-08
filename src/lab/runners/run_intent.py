from __future__ import annotations

from copy import deepcopy
import dataclasses
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import yaml

from lab.attacks.framework_registry import build_attack_plugin
from lab.config.contracts import REPORTING_CONTEXT_KEYS
from lab.defenses.framework_registry import build_defense_plugin
from lab.runners.cli_utils import as_mapping

_NONE_LIKE_NAMES = {"", "none", "identity"}
_OBJECTIVE_FIELDS = {"name", "objective_mode", "target_class", "preserve_weight", "attack_roi"}


def normalized_config_for_output(config: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(config)
    for section in ("attack", "defense"):
        value = normalized.get(section)
        if value is None:
            normalized[section] = {"name": "none", "params": {}}
            continue
        if not isinstance(value, dict):
            continue
        name = value.get("name")
        if name is None or not str(name).strip():
            value["name"] = "none"
    return normalized


def resolved_config_yaml_text(config: dict[str, Any]) -> str:
    return yaml.safe_dump(normalized_config_for_output(config), sort_keys=False)


def config_fingerprint_sha256(config: dict[str, Any]) -> str:
    return hashlib.sha256(resolved_config_yaml_text(config).encode("utf-8")).hexdigest()


def resolved_reporting_context(config: dict[str, Any]) -> dict[str, str]:
    section = as_mapping(config, "reporting_context")
    if not section:
        return {}
    payload: dict[str, str] = {}
    for key in REPORTING_CONTEXT_KEYS:
        value = section.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            payload[key] = text
    return payload


def without_none_values(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in mapping.items() if value is not None}


def stable_signature(payload: Any) -> str:
    try:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return "{}"


def sha256_file(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


@lru_cache(maxsize=64)
def _sha256_file_cached(path_str: str) -> str | None:
    return sha256_file(Path(path_str))


def build_attack_signature(
    *,
    attack_name: str,
    attack_params: dict[str, Any],
    resolved_objective: dict[str, Any],
) -> str:
    return stable_signature(
        {
            "attack_name": attack_name.strip().lower(),
            "objective_mode": resolved_objective.get("objective_mode") or attack_params.get("objective_mode"),
            "target_class": (
                resolved_objective.get("target_class")
                if resolved_objective.get("target_class") is not None
                else attack_params.get("target_class")
            ),
            "attack_roi": resolved_objective.get("attack_roi") or attack_params.get("attack_roi"),
            "attack_params": attack_params,
        }
    )


def build_defense_signature(*, defense_name: str, defense_params: dict[str, Any]) -> str:
    return stable_signature(
        {
            "defense_name": defense_name.strip().lower(),
            "defense_params": defense_params,
        }
    )


def resolve_attack_instance(
    attack_name: str,
    attack_params: dict[str, Any],
) -> tuple[Any | None, dict[str, Any], dict[str, Any]]:
    normalized_name = str(attack_name or "none").strip().lower()
    normalized_params = without_none_values(dict(attack_params))
    if normalized_name in _NONE_LIKE_NAMES:
        return None, {}, {
            "objective_mode": None,
            "target_class": None,
            "attack_roi": None,
            "preserve_weight": None,
        }

    attack = build_attack_plugin(normalized_name, **normalized_params)
    resolved_params = normalized_params
    if dataclasses.is_dataclass(attack):
        resolved_params = without_none_values(
            {
                field.name: getattr(attack, field.name)
                for field in dataclasses.fields(attack)
                if not field.name.startswith("_") and field.name not in _OBJECTIVE_FIELDS
            }
        )
    resolved_objective = {
        "objective_mode": getattr(attack, "objective_mode", normalized_params.get("objective_mode")),
        "target_class": getattr(attack, "target_class", normalized_params.get("target_class")),
        "attack_roi": getattr(attack, "attack_roi", normalized_params.get("attack_roi")),
        "preserve_weight": getattr(attack, "preserve_weight", normalized_params.get("preserve_weight")),
    }
    return attack, resolved_params, resolved_objective


def resolve_defense_instance(
    defense_name: str,
    defense_params: dict[str, Any],
) -> tuple[Any, dict[str, Any], list[dict[str, str]]]:
    normalized_name = str(defense_name or "none").strip().lower() or "none"
    normalized_params = without_none_values(dict(defense_params))
    defense = build_defense_plugin(normalized_name, **normalized_params)
    checkpoint_provenance: list[dict[str, str]] = []
    checkpoint_fn = getattr(defense, "checkpoint_provenance", None)
    if callable(checkpoint_fn):
        maybe_payload = checkpoint_fn()
        if isinstance(maybe_payload, list):
            checkpoint_provenance = [
                cast(dict[str, str], item)
                for item in maybe_payload
                if isinstance(item, dict)
            ]
    return defense, normalized_params, checkpoint_provenance


def resolve_model_checkpoint_fingerprint(
    model_params: dict[str, Any],
    *,
    cwd: Path | None = None,
) -> tuple[str | None, str | None]:
    model_path_candidate = str(model_params.get("model", "")).strip()
    if not model_path_candidate:
        return None, None
    model_path = Path(model_path_candidate).expanduser()
    if not model_path.is_absolute():
        model_path = ((cwd or Path.cwd()) / model_path).resolve()
    if not model_path.is_file():
        return None, None
    return _sha256_file_cached(str(model_path)), str(model_path)


def build_run_intent(
    config: dict[str, Any],
    *,
    cwd: Path | None = None,
) -> dict[str, Any]:
    normalized = normalized_config_for_output(config)
    model_cfg = as_mapping(normalized, "model")
    attack_cfg = as_mapping(normalized, "attack")
    defense_cfg = as_mapping(normalized, "defense")
    runner_cfg = as_mapping(normalized, "runner")
    validation_cfg = as_mapping(normalized, "validation")

    model_params = dict(as_mapping(model_cfg, "params"))
    attack_name = str(attack_cfg.get("name", "none")).strip().lower()
    attack_params = dict(as_mapping(attack_cfg, "params"))
    _, resolved_attack_params, resolved_objective = resolve_attack_instance(attack_name, attack_params)

    defense_name = str(defense_cfg.get("name", "none")).strip().lower()
    defense_params = dict(as_mapping(defense_cfg, "params"))
    _, resolved_defense_params, defense_checkpoint_provenance = resolve_defense_instance(
        defense_name,
        defense_params,
    )

    checkpoint_fingerprint, checkpoint_source = resolve_model_checkpoint_fingerprint(
        model_params,
        cwd=cwd,
    )

    return {
        "config_fingerprint_sha256": config_fingerprint_sha256(normalized),
        "attack_signature": build_attack_signature(
            attack_name=attack_name or "none",
            attack_params=resolved_attack_params,
            resolved_objective=resolved_objective,
        ),
        "defense_signature": build_defense_signature(
            defense_name=defense_name or "none",
            defense_params=resolved_defense_params,
        ),
        "checkpoint_fingerprint_sha256": checkpoint_fingerprint,
        "checkpoint_fingerprint_source": checkpoint_source,
        "defense_checkpoints": defense_checkpoint_provenance,
        "seed": int(runner_cfg.get("seed", 42)),
        "validation_enabled": bool(validation_cfg.get("enabled", False)),
        "reporting_context": resolved_reporting_context(normalized),
    }
