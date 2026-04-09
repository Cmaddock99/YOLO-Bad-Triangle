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


REQUIRED_RUN_ARTIFACTS = ("metrics.json", "run_summary.json", "predictions.jsonl")


def required_run_artifacts_status(run_dir: Path) -> tuple[bool, list[str]]:
    missing = [name for name in REQUIRED_RUN_ARTIFACTS if not (run_dir / name).is_file()]
    return not missing, missing


def load_run_resume_fingerprint(run_dir: Path) -> dict[str, object] | None:
    summary_path = run_dir / "run_summary.json"
    if not summary_path.is_file():
        return None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    validation = payload.get("validation")
    if not isinstance(validation, dict):
        validation = {}
    reporting_context = payload.get("reporting_context")
    if not isinstance(reporting_context, dict):
        reporting_context = {}
    defense_checkpoints = provenance.get("defense_checkpoints")
    if not isinstance(defense_checkpoints, list):
        defense_checkpoints = []
    defense_shas = sorted(
        str(item.get("sha256", "")).strip()
        for item in defense_checkpoints
        if isinstance(item, dict) and str(item.get("sha256", "")).strip()
    )
    return {
        "config_fingerprint_sha256": provenance.get("config_fingerprint_sha256"),
        "attack_signature": (
            (payload.get("attack") or {}).get("signature")
            if isinstance(payload.get("attack"), dict)
            else None
        ),
        "defense_signature": (
            (payload.get("defense") or {}).get("signature")
            if isinstance(payload.get("defense"), dict)
            else None
        ),
        "checkpoint_fingerprint_sha256": provenance.get("checkpoint_fingerprint_sha256"),
        "defense_checkpoint_shas": defense_shas,
        "seed": payload.get("seed"),
        "validation_enabled": validation.get("enabled"),
        "reporting_context": dict(reporting_context),
    }


def normalize_intended_fingerprint(intent: dict[str, object]) -> dict[str, object]:
    defense_checkpoints = intent.get("defense_checkpoints")
    if not isinstance(defense_checkpoints, list):
        defense_checkpoints = []
    defense_shas = sorted(
        str(item.get("sha256", "")).strip()
        for item in defense_checkpoints
        if isinstance(item, dict) and str(item.get("sha256", "")).strip()
    )
    reporting_context = intent.get("reporting_context")
    if not isinstance(reporting_context, dict):
        reporting_context = {}
    return {
        "config_fingerprint_sha256": intent.get("config_fingerprint_sha256"),
        "attack_signature": intent.get("attack_signature"),
        "defense_signature": intent.get("defense_signature"),
        "checkpoint_fingerprint_sha256": intent.get("checkpoint_fingerprint_sha256"),
        "defense_checkpoint_shas": defense_shas,
        "seed": intent.get("seed"),
        "validation_enabled": intent.get("validation_enabled"),
        "reporting_context": dict(reporting_context),
    }


def check_run_resume(run_dir: Path, intended_intent: dict[str, object]) -> tuple[str, str]:
    artifacts_complete, missing = required_run_artifacts_status(run_dir)
    if not run_dir.exists() or (
        not (run_dir / "metrics.json").exists()
        and not (run_dir / "run_summary.json").exists()
        and not (run_dir / "predictions.jsonl").exists()
    ):
        return "run", ""
    if not artifacts_complete:
        return "reran_partial", f"missing required artifacts: {', '.join(missing)}"
    existing = load_run_resume_fingerprint(run_dir)
    if existing is None:
        return "reran_partial", "run_summary.json missing or malformed"
    intended = normalize_intended_fingerprint(intended_intent)
    mismatches = [
        key for key in sorted(intended)
        if intended.get(key) is not None and existing.get(key) != intended.get(key)
    ]
    if mismatches:
        return "reran_mismatch", f"run intent changed: {', '.join(mismatches)}"
    return "skipped_exact", "exact run-intent match"


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
