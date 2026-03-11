#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

from lab.eval import append_run_metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_name", required=True, help="Run folder name")
    parser.add_argument("--attack", required=True, help='Attack name (or "none")')
    parser.add_argument("--conf", required=True, help="Confidence threshold")
    parser.add_argument("--iou", required=True, help="IoU threshold")
    parser.add_argument("--imgsz", required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--defense", default="none")
    parser.add_argument("--output_root", default="results")
    args = parser.parse_args()

    csv_path = Path(args.output_root) / "metrics_summary.csv"
    row = append_run_metrics(
        run_dir=Path(args.output_root) / args.run_name,
        csv_path=csv_path,
        run_name=args.run_name,
        attack=args.attack,
        defense=args.defense,
        conf=float(args.conf),
        iou=float(args.iou),
        imgsz=int(args.imgsz),
        seed=int(args.seed),
    )
    print(f"Metrics for run '{args.run_name}' appended to {csv_path}: {row}")


if __name__ == "__main__":
    main()
