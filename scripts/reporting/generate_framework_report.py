#!/usr/bin/env python3
"""Generate CSV and markdown comparison report from a framework runs directory.

Reads all completed run directories under --runs-root, extracts metrics, and
produces a framework_run_report.md and framework_run_summary.csv showing attack
effectiveness and defense recovery across all combinations.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/generate_framework_report.py \\
        --runs-root outputs/framework_runs/sweep_20260320T220057Z
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lab.reporting.framework import generate_framework_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate comparison summaries from framework run artifacts."
    )
    parser.add_argument(
        "--runs-root",
        default="outputs/framework_runs",
        help="Directory containing framework run folders.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/framework_reports",
        help="Directory for generated report artifacts.",
    )
    args = parser.parse_args()

    csv_path, md_path, record_count = generate_framework_report(
        runs_root=Path(args.runs_root),
        output_dir=Path(args.output_dir),
    )
    print(f"Discovered runs: {record_count}")
    print(f"Summary CSV: {csv_path}")
    print(f"Markdown report: {md_path}")


if __name__ == "__main__":
    main()
