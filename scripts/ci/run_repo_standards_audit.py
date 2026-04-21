#!/usr/bin/env python3
"""Run the repository standards audit."""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_COMPAT_TESTS = [
    "tests/test_repo_structure_compat.py",
    "tests/test_plugin_loader_routing.py",
    "tests/test_training_script_compat.py",
    "tests/test_reporting_and_demo_script_compat.py",
    "tests/test_automation_script_compat.py",
    "tests/test_framework_output_contract.py",
]


def _build_lane_commands(python_bin: str, lane: str) -> list[list[str]]:
    commands: list[list[str]] = []
    if lane == "full":
        commands.append([python_bin, "scripts/ci/run_repo_quality_gate.py", "--lane", "fast"])
    commands.append([python_bin, "-m", "pytest", "-q", *_COMPAT_TESTS])
    return commands


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the repository standards audit.",
    )
    parser.add_argument(
        "--lane",
        choices=("compat", "full"),
        default="compat",
        help="compat: structure/compat audit only; full: quality gate fast lane plus compat audit.",
    )
    parser.add_argument(
        "--python-bin",
        default=sys.executable,
        help="Python interpreter to use for subprocesses.",
    )
    args = parser.parse_args(argv)

    env = _build_env()
    for command in _build_lane_commands(args.python_bin, args.lane):
        print(f"$ PYTHONPATH=src {shlex.join(command)}", flush=True)
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
