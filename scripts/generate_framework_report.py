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

from lab.reporting import discover_framework_runs, render_markdown_report, write_summary_csv


def _assert_consistent_profile(records: list[object]) -> None:
    profile_pairs = {
        (
            getattr(record, "pipeline_profile", None),
            getattr(record, "authoritative_metric", None),
        )
        for record in records
    }
    if len(profile_pairs) > 1:
        raise ValueError(
            "Mixed pipeline profiles or authoritative metrics detected under one runs-root. "
            "Generate reports from a single profile-consistent run set."
        )


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

    runs_root = Path(args.runs_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = discover_framework_runs(runs_root)
    _assert_consistent_profile(records)
    csv_path = output_dir / "framework_run_summary.csv"
    md_path = output_dir / "framework_run_report.md"

    write_summary_csv(records, csv_path)
    md_path.write_text(render_markdown_report(records), encoding="utf-8")

    print(f"Discovered runs: {len(records)}")
    print(f"Summary CSV: {csv_path}")
    print(f"Markdown report: {md_path}")


if __name__ == "__main__":
    main()
