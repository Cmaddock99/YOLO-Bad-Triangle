#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _current_branch() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"failed to resolve git branch: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _read_policy(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("migration runtime config must be a mapping")
    migration = payload.get("migration", {})
    if not isinstance(migration, dict):
        raise ValueError("migration runtime config must include mapping key 'migration'")
    return migration


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "on"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail if legacy runtime default is enabled on protected branches.")
    parser.add_argument("--config", default="configs/migration_runtime.yaml")
    parser.add_argument("--protected-branches", default="main,master,release,production")
    parser.add_argument("--branch", default="")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"runtime config not found: {config_path}")
    branch = args.branch.strip() or _current_branch()
    protected = {name.strip() for name in args.protected_branches.split(",") if name.strip()}

    migration = _read_policy(config_path)
    legacy_enabled = _to_bool(migration.get("use_legacy_runtime", False))
    if branch in protected and legacy_enabled:
        raise RuntimeError(
            f"Protected branch '{branch}' forbids migration.use_legacy_runtime=true in {config_path}."
        )
    print(
        f"Legacy policy branch guard PASS (branch={branch}, protected={branch in protected}, "
        f"use_legacy_runtime={legacy_enabled})"
    )


if __name__ == "__main__":
    main()
