#!/usr/bin/env python3
"""Generate team-facing summary JSON and markdown from framework report artifacts.

Reads the output of generate_framework_report.py and produces a condensed
team_summary.json and team_summary.md showing only the current report-root's
local results. Optional external provenance must be passed explicitly.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/generate_team_summary.py \\
        --report-root outputs/framework_reports/sweep_20260320T220057Z
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lab.reporting.local import write_team_summary


def generate_team_summary(
    *,
    report_root: Path,
    external_clean_gate_path: Path | None = None,
) -> tuple[Path, Path]:
    report_root = report_root.expanduser().resolve()
    resolved_external_clean_gate_path = (
        external_clean_gate_path.expanduser().resolve()
        if external_clean_gate_path is not None
        else None
    )
    return write_team_summary(
        report_root,
        external_clean_gate_path=resolved_external_clean_gate_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate team-facing markdown + JSON summary from framework report artifacts."
    )
    parser.add_argument(
        "--report-root",
        required=True,
        help="Directory containing framework_run_summary.csv and per-attack summary_*.txt files.",
    )
    parser.add_argument(
        "--external-clean-gate",
        help="Optional explicit path to an external clean-gate JSON artifact to cite under External Provenance.",
    )
    args = parser.parse_args()

    json_path, md_path = generate_team_summary(
        report_root=Path(args.report_root),
        external_clean_gate_path=(
            Path(args.external_clean_gate)
            if args.external_clean_gate
            else None
        ),
    )
    print(f"Team summary JSON: {json_path}")
    print(f"Team summary MD:   {md_path}")


if __name__ == "__main__":
    main()
