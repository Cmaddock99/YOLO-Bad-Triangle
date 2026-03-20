#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.reporting.legacy_compat import write_legacy_compat_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate strict legacy-compatible artifacts from framework run folders."
    )
    parser.add_argument(
        "--runs-root",
        default="outputs/framework_runs",
        help="Directory containing framework run folders.",
    )
    parser.add_argument(
        "--output-root",
        default="outputs",
        help="Directory where legacy-compatible artifacts are written.",
    )
    parser.add_argument("--conf-default", type=float, default=0.25)
    parser.add_argument("--iou-default", type=float, default=0.7)
    parser.add_argument("--imgsz-default", type=int, default=640)
    args = parser.parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    if not runs_root.is_dir():
        raise FileNotFoundError(f"Framework runs root not found: {runs_root}")
    output_root = Path(args.output_root).expanduser().resolve()

    result = write_legacy_compat_artifacts(
        runs_root=runs_root,
        output_root=output_root,
        conf_default=args.conf_default,
        iou_default=args.iou_default,
        imgsz_default=args.imgsz_default,
    )
    print(f"Framework runs discovered: {result.row_count}")
    print(f"Legacy CSV: {result.metrics_csv}")
    print(f"Legacy table: {result.experiment_table_md}")


if __name__ == "__main__":
    main()
