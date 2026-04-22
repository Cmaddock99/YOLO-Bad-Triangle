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
)

GRANDFATHERED_LOCAL_ONLY_OUTPUTS = frozenset(
    {
        "outputs/delegated_phase4.log",
        "outputs/sweep_deepfool_strong.log",
        "outputs/sweep_eot_pgd_mac.log",
        "outputs/training_log.txt",
        "outputs/training_log_round2.txt",
        "outputs/training_log_round2b.txt",
    }
)

TOP_LEVEL_LOCAL_ONLY_SUFFIXES = frozenset({".zip", ".pdf", ".log", ".txt"})

# Binary artifact suffixes that must never be tracked anywhere, including inside
# outputs/framework_reports/ where summary files are otherwise allowed.
FRAMEWORK_REPORTS_BINARY_SUFFIXES = frozenset({".pt", ".onnx", ".zip", ".bin"})


def _is_framework_reports_binary(path: Path) -> bool:
    """Return True for binary artifacts nested under outputs/framework_reports/."""
    parts = path.parts
    return (
        len(parts) >= 3
        and parts[0] == "outputs"
        and parts[1] == "framework_reports"
        and path.suffix in FRAMEWORK_REPORTS_BINARY_SUFFIXES
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


def _is_grandfathered_local_output(path: Path) -> bool:
    return path.as_posix() in GRANDFATHERED_LOCAL_ONLY_OUTPUTS


def _is_top_level_local_only_output(path: Path) -> bool:
    return len(path.parts) == 2 and path.parts[0] == "outputs" and path.suffix in TOP_LEVEL_LOCAL_ONLY_SUFFIXES


def find_disallowed_tracked_outputs(paths: Iterable[Path]) -> list[Path]:
    return [
        path
        for path in paths
        if (
            _matches_any(path, DISALLOWED_PATTERNS)
            or _is_top_level_local_only_output(path)
            or _is_framework_reports_binary(path)
        )
        and not _is_grandfathered_local_output(path)
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
