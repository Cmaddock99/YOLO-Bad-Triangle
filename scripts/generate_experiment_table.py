#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.eval import generate_experiment_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a markdown experiment summary table from metrics CSV."
    )
    parser.add_argument(
        "--input_csv",
        default="outputs/metrics_summary.csv",
        help="Path to metrics_summary.csv file.",
    )
    parser.add_argument(
        "--output_md",
        default="outputs/experiment_table.md",
        help="Path for generated markdown table.",
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_md = Path(args.output_md)
    row_count, output_path = generate_experiment_table(
        csv_path=input_csv, markdown_path=output_md
    )
    print(f"Generated {output_path} with {row_count} experiment row(s).")


if __name__ == "__main__":
    main()
