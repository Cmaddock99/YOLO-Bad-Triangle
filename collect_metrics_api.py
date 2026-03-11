#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.eval import append_run_metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_name", required=True)
    parser.add_argument("--attack", required=True)
    parser.add_argument("--conf", required=True)
    parser.add_argument("--iou", required=True)
    parser.add_argument("--imgsz", required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output_root", default="results")
    parser.add_argument("--date", default=None)
    parser.add_argument("--commit", default=None)
    parser.add_argument("--branch", default=None)
    parser.add_argument("--cmd", default=None)
    args = parser.parse_args()

    row = append_run_metrics(
        run_dir=Path(args.output_root) / args.run_name,
        csv_path=Path(args.output_root) / "metrics_summary.csv",
        run_name=args.run_name,
        attack=args.attack,
        defense="none",
        conf=float(args.conf),
        iou=float(args.iou),
        imgsz=int(args.imgsz),
        seed=int(args.seed),
    )
    print(f"Logged metrics for {args.run_name}: {row}")


if __name__ == "__main__":
    main()
