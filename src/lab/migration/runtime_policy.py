from __future__ import annotations

from contextlib import contextmanager
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _operator_id() -> str:
    return (
        os.environ.get("OPERATOR_CONTEXT")
        or os.environ.get("GITHUB_ACTOR")
        or os.environ.get("USER")
        or "unknown-operator"
    )


def _log_runtime_policy_decision(*, context: str, allowed: bool, source: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    operator = _operator_id()
    status = "ALLOW" if allowed else "DENY"
    print(
        "RUNTIME_POLICY "
        f"timestamp_utc={stamp} operator={operator} context={context} source={source} decision={status}"
    )


def load_runtime_policy(path: str | Path = "configs/migration_runtime.yaml") -> dict[str, Any]:
    policy_path = Path(path).expanduser().resolve()
    if not policy_path.is_file():
        return {
            "use_legacy_runtime": False,
            "required_consecutive_passes": 2,
            "deprecate_legacy_after_passes": True,
            "tracker_state_path": "outputs/migration_state/migration_cycle_tracker.json",
        }
    loaded = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return {
            "use_legacy_runtime": False,
            "required_consecutive_passes": 2,
            "deprecate_legacy_after_passes": True,
            "tracker_state_path": "outputs/migration_state/migration_cycle_tracker.json",
        }
    migration = loaded.get("migration", {})
    if not isinstance(migration, dict):
        migration = {}
    return {
        "use_legacy_runtime": _to_bool(migration.get("use_legacy_runtime", False), default=False),
        "required_consecutive_passes": int(migration.get("required_consecutive_passes", 2) or 2),
        "deprecate_legacy_after_passes": _to_bool(
            migration.get("deprecate_legacy_after_passes", True), default=True
        ),
        "tracker_state_path": str(
            migration.get("tracker_state_path", "outputs/migration_state/migration_cycle_tracker.json")
        ),
    }


def allow_legacy_runtime(
    *,
    context: str,
    path: str | Path = "configs/migration_runtime.yaml",
) -> bool:
    # Environment override for emergency rollbacks only.
    env_override = os.environ.get("USE_LEGACY_RUNTIME")
    if env_override is not None:
        allowed = _to_bool(env_override, default=False)
        _log_runtime_policy_decision(context=context, allowed=allowed, source="env:USE_LEGACY_RUNTIME")
        return allowed
    allowed = bool(load_runtime_policy(path).get("use_legacy_runtime", False))
    _log_runtime_policy_decision(context=context, allowed=allowed, source="config:migration.use_legacy_runtime")
    return allowed


def legacy_runtime_warning(*, operator_context: str) -> str:
    operator = _operator_id()
    timestamp = datetime.now(timezone.utc).isoformat()
    return (
        "LEGACY MODE ENABLED - EMERGENCY USE ONLY. "
        f"timestamp_utc={timestamp} operator={operator} context={operator_context}"
    )


@contextmanager
def temporary_legacy_runtime_override(enabled: bool) -> Any:
    prior = os.environ.get("USE_LEGACY_RUNTIME")
    os.environ["USE_LEGACY_RUNTIME"] = "true" if enabled else "false"
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop("USE_LEGACY_RUNTIME", None)
        else:
            os.environ["USE_LEGACY_RUNTIME"] = prior
