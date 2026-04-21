#!/usr/bin/env python3
"""Generate a static HTML dashboard from explicit or discovered report directories.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py
    PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py \
        --reports-root outputs/framework_reports \
        --output outputs/dashboard.html
    PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py \
        --report-dir outputs/framework_reports/custom_report_dir \
        --output outputs/framework_reports/custom_report_dir/dashboard.html

Output:
    A single self-contained HTML file, open in any browser.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lab.reporting.aggregate import generate_dashboard

generate = generate_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate static HTML dashboard from sweep reports.")
    parser.add_argument(
        "--reports-root",
        default="outputs/framework_reports",
        help=(
            "Root directory for backward-compatible child discovery. "
            "Immediate child directories are included when they contain framework_run_summary.csv."
        ),
    )
    parser.add_argument(
        "--report-dir",
        action="append",
        default=[],
        help="Explicit report directory to load. Can be repeated.",
    )
    parser.add_argument(
        "--output",
        default="outputs/dashboard.html",
        help="Output HTML file path.",
    )
    parser.add_argument(
        "--compat-output",
        help="Optional compatibility mirror path that receives the same HTML as --output.",
    )
    parser.add_argument(
        "--no-pages",
        action="store_true",
        default=False,
        help="Skip writing docs/index.html for GitHub Pages.",
    )
    args = parser.parse_args()
    generate_dashboard(
        reports_root=Path(args.reports_root).expanduser().resolve(),
        output=Path(args.output).expanduser().resolve(),
        report_dirs=[Path(path) for path in args.report_dir],
        compat_output=Path(args.compat_output).expanduser().resolve() if args.compat_output else None,
        no_pages=args.no_pages,
    )


if __name__ == "__main__":
    main()
