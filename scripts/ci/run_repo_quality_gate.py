#!/usr/bin/env python3
"""Run the repository quality gate with local and CI-parity lanes.

When ``--python-bin`` is omitted, subprocesses prefer the repository virtualenv
interpreter and fall back to the current interpreter only when no repo venv
exists.
"""
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


def _ensure_ci_demo_input(repo_root: Path) -> Path:
    import cv2
    import numpy as np

    source_dir = repo_root / "outputs" / "ci_demo" / "images"
    source_dir.mkdir(parents=True, exist_ok=True)
    image_path = source_dir / "ci.jpg"
    image = np.full((128, 128, 3), 127, dtype=np.uint8)
    wrote = cv2.imwrite(str(image_path), image)
    if not wrote:
        raise RuntimeError(f"Failed to write CI demo image: {image_path}")
    return image_path


def _resolve_python_bin(explicit_python_bin: str | None) -> str:
    if explicit_python_bin is not None:
        return explicit_python_bin
    repo_python = REPO_ROOT / ".venv" / "bin" / "python"
    if repo_python.is_file():
        return str(repo_python)
    return sys.executable


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
        default=None,
        help=(
            "Python interpreter override for subprocesses. Defaults to "
            "REPO_ROOT/.venv/bin/python when present, otherwise the current interpreter."
        ),
    )
    args = parser.parse_args(argv)
    python_bin = _resolve_python_bin(args.python_bin)

    if args.lane == "ci":
        _ensure_ci_demo_input(REPO_ROOT)

    env = _build_env()
    for command in _build_lane_commands(python_bin, args.lane):
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
