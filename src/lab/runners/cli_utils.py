from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import yaml


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        if re.fullmatch(r"[+-]?\d+", value):
            return int(value)
        if re.fullmatch(r"[+-]?\d+\.\d*", value):
            return float(value)
    except ValueError:
        pass
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def sanitize_segment(value: object, fallback: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").strip().lower()).strip("-")
    return cleaned or fallback


def parse_key_value_tokens(tokens: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"Invalid parameter '{token}'. Expected key=value.")
        key, value = token.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid parameter '{token}'. Key cannot be empty.")
        parsed[key] = parse_scalar(value.strip())
    return parsed


def resolve_python_bin(project_root: Path) -> str:
    candidate = project_root / ".venv/bin/python"
    if candidate.is_file():
        return str(candidate)
    return sys.executable


def build_repo_python_command(
    project_root: Path,
    script_relative_path: str,
    args: list[str],
    *,
    python_bin: str | None = None,
) -> list[str]:
    interpreter = python_bin or resolve_python_bin(project_root)
    return [interpreter, str(project_root / script_relative_path), *args]


def build_run_experiment_command(
    project_root: Path,
    config: Path | str,
    overrides: list[str],
    *,
    python_bin: str | None = None,
) -> list[str]:
    command = build_repo_python_command(
        project_root,
        "src/lab/runners/run_experiment.py",
        ["--config", str(config)],
        python_bin=python_bin,
    )
    for override in overrides:
        command.extend(["--set", override])
    return command


def with_src_pythonpath(project_root: Path, env: dict[str, str] | None = None) -> dict[str, str]:
    runtime_env = dict(env or os.environ)
    existing = runtime_env.get("PYTHONPATH", "")
    src_path = str(project_root / "src")
    runtime_env["PYTHONPATH"] = f"{src_path}:{existing}" if existing else src_path
    return runtime_env


def run_repo_python_script(
    project_root: Path,
    script_relative_path: str,
    args: list[str],
    *,
    include_src_pythonpath: bool = True,
) -> int:
    command = build_repo_python_command(project_root, script_relative_path, args)
    env = with_src_pythonpath(project_root) if include_src_pythonpath else None
    return subprocess.call(command, env=env)


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping config in {path}")
    return cast(dict[str, Any], loaded)


def as_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping at '{key}'.")
    return cast(dict[str, Any], value)


def apply_override(config: dict[str, Any], assignment: str) -> None:
    if "=" not in assignment:
        raise ValueError(f"Override must use key=value format, got: {assignment}")
    key_path, raw_value = assignment.split("=", 1)
    if not key_path.strip():
        raise ValueError(f"Override key cannot be empty: {assignment}")

    keys = [part for part in key_path.split(".") if part]
    if not keys:
        raise ValueError(f"Invalid override key path: {assignment}")

    node: dict[str, Any] = config
    for key in keys[:-1]:
        existing = node.get(key)
        if existing is None:
            node[key] = {}
            existing = node[key]
        if not isinstance(existing, dict):
            raise ValueError(f"Cannot set nested key under non-mapping path '{key_path}'.")
        node = cast(dict[str, Any], existing)
    node[keys[-1]] = parse_scalar(raw_value)
