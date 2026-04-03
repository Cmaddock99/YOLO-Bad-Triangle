#!/usr/bin/env python3
"""Enforce tracked-output policy for versioned repository artifacts.

This repository intentionally versions selected summary artifacts under
``outputs/`` for longitudinal analysis and capstone reporting. Raw run data,
locks, state files, transfer bundles, and other purely local artifacts must
remain untracked.
"""
from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

DISALLOWED_PATTERNS = (
    "outputs/framework_runs/**",
    "outputs/report_tables/**",
    "outputs/training_data/**",
    "outputs/training_exports/**",
    "outputs/demo/**",
    "outputs/audit_exports/**",
    "outputs/ci_demo/**",
    "outputs/.cycle.lock",
    "outputs/.cw_tune.lock",
    "outputs/cycle_state.json",
    "outputs/cw_tune_state.json",
    "outputs/*.zip",
    "outputs/*.pdf",
)


def _tracked_outputs() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "outputs"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in completed.stdout.splitlines() if line.strip()]


def _matches_any(path: Path, patterns: tuple[str, ...]) -> bool:
    normalized = path.as_posix()
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def find_disallowed_tracked_outputs(paths: Iterable[Path]) -> list[Path]:
    return [
        path
        for path in paths
        if _matches_any(path, DISALLOWED_PATTERNS)
    ]


def main(tracked_paths: list[Path] | None = None) -> int:
    tracked = tracked_paths if tracked_paths is not None else _tracked_outputs()
    disallowed = find_disallowed_tracked_outputs(tracked)
    if disallowed:
        print("Tracked output policy failed. These paths must not be versioned:")
        for path in disallowed:
            print(path.as_posix())
        return 1

    print(
        "Tracked output policy OK. Historical summaries may be versioned; raw runs and local-only "
        "artifacts are not."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
