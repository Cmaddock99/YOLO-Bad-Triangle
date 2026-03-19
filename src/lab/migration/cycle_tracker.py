from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .runtime_policy import load_runtime_policy


@dataclass
class MigrationCycleState:
    cycle_count: int
    consecutive_full_passes: int
    legacy_status: str
    legacy_default_enabled: bool
    last_cycle_passed: bool
    last_updated_utc: str


def _default_state() -> dict[str, Any]:
    return {
        "cycle_count": 0,
        "consecutive_full_passes": 0,
        "legacy_status": "active",
        "legacy_default_enabled": False,
        "last_cycle_passed": False,
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "history": [],
    }


def _read_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return _default_state()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _default_state()
    if not isinstance(payload, dict):
        return _default_state()
    merged = _default_state()
    merged.update(payload)
    return merged


def update_migration_cycle_tracker(
    *,
    cycle_name: str,
    gate_results: dict[str, bool],
    state_path: str | Path | None = None,
) -> MigrationCycleState:
    policy = load_runtime_policy()
    resolved_state_path = Path(
        state_path or str(policy.get("tracker_state_path", "outputs/migration_state/migration_cycle_tracker.json"))
    ).expanduser().resolve()
    resolved_state_path.parent.mkdir(parents=True, exist_ok=True)
    state = _read_state(resolved_state_path)

    full_pass = all(bool(value) for value in gate_results.values())
    state["cycle_count"] = int(state.get("cycle_count", 0)) + 1
    if full_pass:
        state["consecutive_full_passes"] = int(state.get("consecutive_full_passes", 0)) + 1
    else:
        state["consecutive_full_passes"] = 0
    required = int(policy.get("required_consecutive_passes", 2) or 2)
    deprecate = bool(policy.get("deprecate_legacy_after_passes", True))
    if deprecate and int(state["consecutive_full_passes"]) >= required:
        state["legacy_status"] = "deprecated"
        state["legacy_default_enabled"] = False
    else:
        state["legacy_status"] = "active"
        state["legacy_default_enabled"] = bool(policy.get("use_legacy_runtime", False))
    state["last_cycle_passed"] = full_pass
    state["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    history = state.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append(
        {
            "cycle_name": cycle_name,
            "passed": full_pass,
            "gate_results": gate_results,
            "updated_at_utc": state["last_updated_utc"],
        }
    )
    state["history"] = history[-50:]
    resolved_state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return MigrationCycleState(
        cycle_count=int(state["cycle_count"]),
        consecutive_full_passes=int(state["consecutive_full_passes"]),
        legacy_status=str(state["legacy_status"]),
        legacy_default_enabled=bool(state["legacy_default_enabled"]),
        last_cycle_passed=bool(state["last_cycle_passed"]),
        last_updated_utc=str(state["last_updated_utc"]),
    )
