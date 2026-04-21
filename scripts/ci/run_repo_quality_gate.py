#!/usr/bin/env python3
"""Run the repository quality gate with local and CI-parity lanes."""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _build_lane_commands(python_bin: str, lane: str) -> list[list[str]]:
    commands: list[list[str]] = [
        [python_bin, "-m", "ruff", "check", "src", "tests", "scripts"],
        [python_bin, "-m", "mypy"],
        [python_bin, "-m", "pytest", "-q"],
    ]
    if lane == "fast":
        return commands

    commands.extend(
        [
            [
                python_bin,
                "scripts/run_unified.py",
                "run-one",
                "--config",
                "configs/ci_demo.yaml",
                "--set",
                "runner.output_root=outputs/framework_runs/ci",
                "--set",
                "runner.run_name=ci_demo",
            ],
            [
                python_bin,
                "scripts/ci/validate_outputs.py",
                "--output-root",
                "outputs/framework_runs/ci/ci_demo",
                "--contract-name",
                "framework_run",
                "--framework-run-dir",
                "outputs/framework_runs/ci/ci_demo",
                "--legacy-compat-csv",
                "tests/fixtures/schema/valid/legacy_compat.csv",
                "--require-schema",
            ],
            [
                python_bin,
                "scripts/generate_framework_report.py",
                "--runs-root",
                "outputs/framework_runs/ci",
                "--output-dir",
                "outputs/framework_reports/ci",
            ],
            [python_bin, "scripts/ci/check_tracked_outputs.py"],
        ]
    )
    return commands


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the repository quality gate with a fast lane or CI-parity lane."
    )
    parser.add_argument(
        "--lane",
        choices=("fast", "ci"),
        default="ci",
        help="Select the quality gate lane to run (default: ci).",
    )
    parser.add_argument(
        "--python-bin",
        default=sys.executable,
        help="Python interpreter to use for Python-script subprocesses.",
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
