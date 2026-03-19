#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_KEYS = ["status", "stage", "issues", "commands", "timestamp_utc"]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _assert_contract(path: Path, payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in payload:
            issues.append(f"{path}: missing required key '{key}'")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify standardized observability output contract keys.")
    parser.add_argument("--gate-summary", default="outputs/migration_state/gate_summary.json")
    parser.add_argument("--health-summary", default="outputs/system_health/system_health_summary.json")
    parser.add_argument("--status-snapshot", default="outputs/migration_state/migration_status_snapshot.json")
    args = parser.parse_args()

    files = [
        Path(args.gate_summary).expanduser().resolve(),
        Path(args.health_summary).expanduser().resolve(),
        Path(args.status_snapshot).expanduser().resolve(),
    ]
    violations: list[str] = []
    for path in files:
        if not path.is_file():
            violations.append(f"{path}: missing required output file")
            continue
        try:
            payload = _read_json(path)
        except Exception as exc:  # pragma: no cover
            violations.append(f"{path}: failed to parse JSON: {exc}")
            continue
        violations.extend(_assert_contract(path, payload))
    if violations:
        raise RuntimeError("Observability contract failed:\n" + "\n".join(f"- {item}" for item in violations))
    print("Observability contract PASS")


if __name__ == "__main__":
    main()
