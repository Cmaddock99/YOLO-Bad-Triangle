#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks.registry import list_available_attacks
from lab.defenses.registry import list_available_defenses
from lab.runners import ExperimentRunner
from lab.runners.experiment_registry import ExperimentRegistry


def _print_list(title: str, values: list[str]) -> None:
    print(f"{title}:")
    if not values:
        print("  (none)")
        return
    for value in values:
        print(f"  - {value}")


def _parse_scalar(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"none", "null"}:
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def _parse_param_tokens(tokens: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"Invalid parameter '{token}'. Expected key=value.")
        key, value = token.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid parameter '{token}'. Key cannot be empty.")
        parsed[key] = _parse_scalar(value.strip())
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one experiment via explicit CLI arguments.")
    parser.add_argument(
        "--config",
        default="configs/experiment_lab.yaml",
        help="Registry config used for --list-* discovery output.",
    )
    parser.add_argument(
        "--list-attacks",
        action="store_true",
        help="List configured attack aliases and registered attack plugins, then exit.",
    )
    parser.add_argument(
        "--list-defenses",
        action="store_true",
        help="List configured defense aliases and registered defense plugins, then exit.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List configured model aliases, then exit.",
    )
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="List configured dataset aliases, then exit.",
    )
    parser.add_argument("--run_name", help="Name of this run (used as output folder)")
    parser.add_argument(
        "--model",
        default="yolov8n",
        help="YOLO model name/path (for example: yolov8n, yolo11n, yolo11s.pt)",
    )
    parser.add_argument(
        "--attack",
        default=None,
        help='Attack type (for example: none, blur, gaussian_noise, fgsm, deepfool)',
    )
    parser.add_argument(
        "--defense",
        default="none",
        help='Defense type (for example: none, median_blur, denoise)',
    )
    parser.add_argument("--conf", type=float, default=None, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.7, help="IoU threshold")
    parser.add_argument("--imgsz", type=int, default=None, help="Image size (pixels)")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "--output_root",
        default="outputs",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--output-root",
        dest="output_root_dash",
        default=None,
        help="Output root folder (default: outputs).",
    )
    parser.add_argument(
        "--attacks_dir",
        default=None,
        help="Optional path to pre-generated attacked images",
    )
    parser.add_argument(
        "--source-override",
        default=None,
        help="Optional explicit source image directory override for this run.",
    )
    parser.add_argument(
        "--blur_kernel",
        type=int,
        default=9,
        help="Backward-compatible blur kernel override when attack=blur and no --attack-param is set.",
    )
    parser.add_argument(
        "--attack-param",
        action="append",
        default=[],
        help="Attack parameter override as key=value. Repeatable.",
    )
    parser.add_argument(
        "--defense-param",
        action="append",
        default=[],
        help="Defense parameter override as key=value. Repeatable.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Enable validation metrics for this run.",
    )
    parser.add_argument(
        "--data-yaml",
        default="configs/coco_subset500.yaml",
        help="Dataset data.yaml path (default: configs/coco_subset500.yaml).",
    )
    parser.add_argument(
        "--image-dir",
        default="coco/val2017_subset500/images",
        help="Dataset image directory (default: coco/val2017_subset500/images).",
    )
    args = parser.parse_args()

    if args.list_attacks or args.list_defenses or args.list_models or args.list_datasets:
        registry = ExperimentRegistry.from_yaml(ROOT / args.config)
        if args.list_attacks:
            _print_list("Configured attack aliases", registry.available_attack_aliases())
            _print_list("Registered attack plugins", list_available_attacks())
        if args.list_defenses:
            _print_list("Configured defense aliases", registry.available_defense_aliases())
            _print_list("Registered defense plugins", list_available_defenses())
        if args.list_models:
            _print_list("Configured models", registry.available_models())
        if args.list_datasets:
            _print_list("Configured datasets", registry.available_datasets())
        return

    required_missing: list[str] = []
    if not args.run_name:
        required_missing.append("--run_name")
    if not args.attack:
        required_missing.append("--attack")
    if args.conf is None:
        required_missing.append("--conf")
    if args.imgsz is None:
        required_missing.append("--imgsz")
    if required_missing:
        parser.error(f"Missing required arguments for execution: {', '.join(required_missing)}")

    output_root = args.output_root_dash or args.output_root

    try:
        attack_params = _parse_param_tokens(list(args.attack_param))
        defense_params = _parse_param_tokens(list(args.defense_param))
    except ValueError as exc:
        parser.error(str(exc))

    attack_name = str(args.attack)
    attack_label = str(args.attack)
    if args.attacks_dir:
        attack_name = "none"
        source_override = args.attacks_dir
    elif args.source_override:
        source_override = args.source_override
    else:
        source_override = None

    if args.attack == "blur" and "kernel_size" not in attack_params:
        attack_params["kernel_size"] = args.blur_kernel
    if args.attack == "gaussian_noise" and "stddev" not in attack_params:
        attack_params["stddev"] = 12.0

    run_validation = bool(args.validate)

    runner = ExperimentRunner.from_dict(
        {
            "model": {"path": args.model},
            "data": {
                "data_yaml": args.data_yaml,
                "image_dir": args.image_dir,
            },
            "runner": {
                "confs": [args.conf],
                "iou": args.iou,
                "imgsz": args.imgsz,
                "seed": args.seed,
                "output_root": output_root,
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
                    "defense": args.defense,
                    "defense_label": args.defense,
                    "defense_params": defense_params,
                    "run_validation": run_validation,
                }
            ],
        }
    )
    rows = runner.run()
    run_names = ", ".join(str(row.get("run_name")) for row in rows)
    print(f"\nExperiment(s) {run_names} completed successfully.")
    print(f"Outputs saved under: {output_root}/\n")


if __name__ == "__main__":
    main()