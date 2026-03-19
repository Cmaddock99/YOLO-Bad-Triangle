#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def _assert_range(name: str, value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric, got {value!r}") from exc
    if numeric < 0.0 or numeric > 100.0:
        raise ValueError(f"{name} must be in [0, 100], got {numeric}")
    return numeric


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate migration contract ownership and SLO definitions.")
    parser.add_argument(
        "--contracts",
        default="contracts/migration_contracts.yaml",
        help="Path to migration contract ownership file.",
    )
    args = parser.parse_args()

    path = Path(args.contracts).expanduser().resolve()
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("Expected mapping in contracts file.")
    contracts = payload.get("contracts", {})
    if not isinstance(contracts, dict):
        raise ValueError("Expected mapping at top-level 'contracts'.")

    required = ("runtime", "reporting", "demo")
    for name in required:
        if name not in contracts:
            raise ValueError(f"Missing required contract: {name}")
        entry = contracts[name]
        if not isinstance(entry, dict):
            raise ValueError(f"Contract '{name}' must be a mapping.")
        owner = str(entry.get("owner", "")).strip()
        if not owner:
            raise ValueError(f"Contract '{name}' missing owner.")
        slo = entry.get("slo", {})
        if not isinstance(slo, dict):
            raise ValueError(f"Contract '{name}' slo must be a mapping.")
        pass_target = _assert_range(f"{name}.slo.pass_rate_target_pct", slo.get("pass_rate_target_pct"))
        fail_threshold = _assert_range(
            f"{name}.slo.acceptable_failure_threshold_pct",
            slo.get("acceptable_failure_threshold_pct"),
        )
        if pass_target + fail_threshold < 99.0:
            raise ValueError(
                f"Contract '{name}' has weak SLO envelope: pass_rate_target_pct + acceptable_failure_threshold_pct < 99."
            )
    print("Contract ownership and SLO validation PASS")


if __name__ == "__main__":
    main()
