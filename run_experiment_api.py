#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.runners import ExperimentRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YOLO experiment via modular runner")
    parser.add_argument("--run_name", required=True, help="Name of this run (used as output folder)")
    parser.add_argument(
        "--attack",
        required=True,
        choices=["none", "blur", "gaussian_noise"],
        help='Attack type or "none"',
    )
    parser.add_argument("--conf", type=float, required=True, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.7, help="IoU threshold")
    parser.add_argument("--imgsz", type=int, required=True, help="Image size (pixels)")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "--attacks_dir",
        default=None,
        help="Optional path to pre-generated attacked images",
    )
    parser.add_argument(
        "--blur_kernel",
        type=int,
        default=9,
        help="Kernel size for blur attack generation",
    )
    args = parser.parse_args()

    if args.attack == "none":
        attack_name = "none"
        attack_label = "none"
        source_override = None
        run_validation = True
        attack_params: dict[str, float | int] = {}
    elif args.attacks_dir:
        attack_name = "none"
        attack_label = args.attack
        source_override = args.attacks_dir
        run_validation = False
        attack_params = {}
    elif args.attack == "blur":
        attack_name = "blur"
        attack_label = "blur"
        source_override = None
        run_validation = False
        attack_params = {"kernel_size": args.blur_kernel}
    else:
        attack_name = "gaussian_noise"
        attack_label = "gaussian_noise"
        source_override = None
        run_validation = False
        attack_params = {"stddev": 12.0}

    runner = ExperimentRunner.from_dict(
        {
            "model": {"path": "yolo11n.pt"},
            "data": {
                "data_yaml": "configs/coco_subset500.yaml",
                "image_dir": "coco/val2017_subset500/images",
            },
            "runner": {
                "confs": [args.conf],
                "iou": args.iou,
                "imgsz": args.imgsz,
                "seed": args.seed,
                "output_root": "results",
                "metrics_csv": "metrics_summary.csv",
            },
            "experiments": [
                {
                    "name": args.run_name,
                    "run_name_template": args.run_name,
                    "attack": attack_name,
                    "attack_label": attack_label,
                    "attack_params": attack_params,
                    "source_override": source_override,
                    "defense": "none",
                    "run_validation": run_validation,
                }
            ],
        }
    )
    runner.run()
    print(f"\nExperiment {args.run_name} completed successfully.")
    print(f"Outputs saved to: results/{args.run_name}\n")


if __name__ == "__main__":
    main()