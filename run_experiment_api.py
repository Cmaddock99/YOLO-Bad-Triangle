#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.cli_utils import parse_key_value_tokens, run_repo_python_script


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "[DEPRECATED COMPAT ENTRYPOINT] Run one experiment via explicit CLI arguments. "
            "Prefer framework runner: src/lab/runners/run_experiment.py"
        )
    )
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
    print(
        "DEPRECATION NOTICE: 'run_experiment_api.py' is a legacy compatibility entrypoint. "
        "Use 'run_experiment.py' or 'scripts/run_unified.py run-one --config configs/lab_framework_phase5.yaml --set ...' "
        "for framework-first operation."
    )

    if args.list_attacks or args.list_defenses or args.list_models or args.list_datasets:
        delegated_args: list[str] = []
        if args.list_attacks:
            delegated_args.append("--list-attacks")
        if args.list_defenses:
            delegated_args.append("--list-defenses")
        if args.list_models:
            delegated_args.append("--list-models")
        if args.list_datasets:
            delegated_args.append("--list-datasets")
        raise SystemExit(run_repo_python_script(ROOT, "run_experiment.py", delegated_args))

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
        attack_params = parse_key_value_tokens(list(args.attack_param))
        defense_params = parse_key_value_tokens(list(args.defense_param))
    except ValueError as exc:
        parser.error(str(exc))

    attack_name = str(args.attack)
    if args.attacks_dir:
        attack_name = "none"
        source_dir_override = args.attacks_dir
    elif args.source_override:
        source_dir_override = args.source_override
    else:
        source_dir_override = args.image_dir

    if args.attack == "blur" and "kernel_size" not in attack_params:
        attack_params["kernel_size"] = args.blur_kernel
    if args.attack == "gaussian_noise" and "stddev" not in attack_params:
        attack_params["stddev"] = 12.0

    delegated_args = [
        f"run_name={args.run_name}",
        f"attack={attack_name}",
        f"defense={args.defense}",
        f"model={args.model}",
        f"conf={args.conf}",
        f"iou={args.iou}",
        f"imgsz={args.imgsz}",
        f"seed={args.seed}",
        f"output_root={output_root}",
        f"validate={str(bool(args.validate)).lower()}",
        f"data.source_dir={source_dir_override}",
        f"validation.dataset={args.data_yaml}",
    ]
    for key, value in attack_params.items():
        delegated_args.extend(["--set", f"attack.params.{key}={value}"])
    for key, value in defense_params.items():
        delegated_args.extend(["--set", f"defense.params.{key}={value}"])

    raise SystemExit(run_repo_python_script(ROOT, "run_experiment.py", delegated_args))


if __name__ == "__main__":
    main()