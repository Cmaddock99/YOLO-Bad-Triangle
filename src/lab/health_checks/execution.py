from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Callable


class CheckFailure(RuntimeError):
    """Structured error for check/gate failures."""


@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def format_command(command: list[str]) -> str:
    return shlex.join(command)


def log_event(*, component: str, severity: str, message: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    stream = sys.stderr if severity.upper() in {"ERROR", "WARN"} else sys.stdout
    print(f"{ts} [{component}] {severity.upper()}: {message}", file=stream)


def run_command(
    *,
    name: str,
    command: list[str],
    cwd: Path,
    with_src_pythonpath: bool = True,
    component: str = "health-check",
    extra_env: dict[str, str] | None = None,
) -> CommandResult:
    rendered = format_command(command)
    log_event(component=component, severity="INFO", message=f"$ {rendered}")
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    if with_src_pythonpath:
        src_path = str((cwd / "src").resolve())
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path}:{existing_pythonpath}" if existing_pythonpath else src_path
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise CheckFailure(
            f"{name} failed to launch. command={rendered} cwd={cwd} error={exc}"
        ) from exc
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return CommandResult(
        name=name,
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def require_success(result: CommandResult, *, component: str = "health-check") -> None:
    if result.returncode != 0:
        raise CheckFailure(
            f"{result.name} failed with exit code {result.returncode}. "
            f"command={format_command(result.command)} "
            f"stdout_len={len(result.stdout)} stderr_len={len(result.stderr)}"
        )
    log_event(component=component, severity="INFO", message=f"{result.name} PASS")


def run_and_require_success(
    *,
    name: str,
    command: list[str],
    cwd: Path,
    with_src_pythonpath: bool = True,
    component: str = "health-check",
    extra_env: dict[str, str] | None = None,
) -> CommandResult:
    result = run_command(
        name=name,
        command=command,
        cwd=cwd,
        with_src_pythonpath=with_src_pythonpath,
        component=component,
        extra_env=extra_env,
    )
    require_success(result, component=component)
    return result


def resolve_latest_dir(
    parent: Path,
    *,
    predicate: Callable[[Path], bool] | None = None,
    description: str = "run directories",
) -> Path:
    if not parent.is_dir():
        raise FileNotFoundError(f"Directory not found: {parent}")
    keep = predicate or (lambda _: True)
    candidates = sorted((path for path in parent.iterdir() if path.is_dir() and keep(path)), key=lambda p: p.name)
    if not candidates:
        raise FileNotFoundError(f"No {description} found under {parent}")
    return candidates[-1]


def resolve_latest_shadow_run_dir(shadow_root: Path) -> Path:
    return resolve_latest_dir(
        shadow_root,
        predicate=lambda path: (path / "parity_report.json").is_file(),
        description="shadow run directories with parity_report.json",
    )


def resolve_latest_framework_run(runs_root: Path) -> Path:
    return resolve_latest_dir(runs_root, description="framework run directories")


def read_json_file(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Expected top-level JSON object at {path}")
    return payload
