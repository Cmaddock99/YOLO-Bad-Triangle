#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lab.reporting.team_summary import write_team_summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate team-facing markdown + JSON summary from framework report artifacts."
    )
    parser.add_argument(
        "--report-root",
        required=True,
        help="Directory containing framework_run_summary.csv and per-attack summary_*.txt files.",
    )
    args = parser.parse_args()

    report_root = Path(args.report_root).expanduser().resolve()
    json_path, md_path = write_team_summary(report_root)
    print(f"Team summary JSON: {json_path}")
    print(f"Team summary MD:   {md_path}")


if __name__ == "__main__":
    main()
