#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.runners import ExperimentRunner
from lab.runners.experiment_registry import parse_key_value_overrides


USAGE = """\
One-command experiment lab with YAML experiment configs

Usage:
  python run_experiment.py --config experiments/blur_attack.yaml
  python run_experiment.py --config experiments/deepfool_defense.yaml --dry-run
  python run_experiment.py attack=blur conf=0.5

Config file fields:
  model, attack, defense, imgsz, conf, dataset_path, output_dir

Optional key=value overrides:
  model=<weights-path> attack=none|blur|gaussian_noise|deepfool
  defense=none|median|median_blur|denoise conf=0.25,0.5 imgsz=640
  dataset_path=<image-dir> output_dir=<output-root> iou=0.7 seed=42
"""


DEFAULT_EXPERIMENT = {
    "model": "yolov8n.pt",
    "attack": "none",
    "defense": "none",
    "imgsz": 640,
    "conf": 0.25,
    "dataset_path": "datasets/coco/val2017_subset500/images",
    "output_dir": "outputs/",
}

ATTACK_ALIASES = {
    "none": "none",
    "blur": "blur",
    "gaussian": "gaussian_noise",
    "gaussian_noise": "gaussian_noise",
    "deepfool": "deepfool",
}

DEFENSE_ALIASES = {
    "none": "none",
    "median": "median_blur",
    "median_blur": "median_blur",
    "denoise": "denoise",
}


def _print_readable_summary(summary: dict[str, Any], resolved_runner: dict[str, Any]) -> None:
    confs = resolved_runner.get("runner", {}).get("confs", [])
    conf_text = ",".join(str(conf) for conf in confs) if confs else "default"
    imgsz = resolved_runner.get("runner", {}).get("imgsz")
    print("Running experiment")
    print(f"Model: {summary.get('model_label', summary.get('model', 'unknown'))}")
    print(f"Attack: {summary.get('attack', 'none')}")
    print(f"Defense: {summary.get('defense', 'none')}")
    print(f"Conf: {conf_text}")
    print(f"Image size: {imgsz}")
    print()


def _coerce_confs(value: Any) -> list[float]:
    if isinstance(value, list):
        return [float(v) for v in value]
    if isinstance(value, str) and "," in value:
        return [float(v.strip()) for v in value.split(",") if v.strip()]
    return [float(value)]


def _load_experiment_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    loaded = yaml.safe_load(config_path.read_text())
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a mapping YAML config in {config_path}")
    merged = dict(DEFAULT_EXPERIMENT)
    merged.update(loaded)
    return merged


def _build_runner_config(
    *,
    experiment_cfg: dict[str, Any],
    config_path: Path,
    overrides: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    merged = dict(experiment_cfg)
    merged.update(overrides)

    attack_raw = str(merged.get("attack", "none")).strip()
    defense_raw = str(merged.get("defense", "none")).strip()
    attack_module = ATTACK_ALIASES.get(attack_raw)
    defense_module = DEFENSE_ALIASES.get(defense_raw)
    if attack_module is None:
        raise ValueError(f"Unsupported attack '{attack_raw}'.")
    if defense_module is None:
        raise ValueError(f"Unsupported defense '{defense_raw}'.")

    confs = _coerce_confs(merged.get("conf", 0.25))
    run_name = config_path.stem
    run_name_template = run_name if len(confs) == 1 else f"{run_name}_conf{{conf_token}}"

    iou = float(merged.get("iou", 0.7))
    seed = int(merged.get("seed", 42))
    imgsz = int(merged.get("imgsz", 640))
    model = str(merged.get("model", "yolov8n.pt"))
    dataset_path = str(merged.get("dataset_path", DEFAULT_EXPERIMENT["dataset_path"]))
    output_dir = str(merged.get("output_dir", DEFAULT_EXPERIMENT["output_dir"]))

    runner_config = {
        "model": model,
        "data": {
            "data_yaml": "configs/coco_subset500.yaml",
            "image_dir": dataset_path,
        },
        "runner": {
            "confs": confs,
            "iou": iou,
            "imgsz": imgsz,
            "seed": seed,
            "output_root": output_dir,
            "metrics_csv": "metrics_summary.csv",
        },
        "experiments": [
            {
                "name": run_name,
                "run_name_template": run_name_template,
                "attack": attack_module,
                "attack_label": attack_raw,
                "defense": defense_module,
                "defense_label": defense_raw,
                "run_validation": False,
            }
        ],
    }
    summary = {
        "model_label": Path(model).stem,
        "attack": attack_raw,
        "defense": defense_raw,
        "confs": confs,
        "output_root": output_dir,
        "dataset_path": dataset_path,
        "config": str(config_path),
    }
    return runner_config, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run YOLO robustness experiments from YAML config files.",
        add_help=True,
    )
    parser.add_argument(
        "--config",
        default="experiments/baseline.yaml",
        help="Path to experiment config YAML (default: experiments/baseline.yaml).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved config and exit without running inference.",
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional key=value overrides (attack=..., conf=..., imgsz=..., etc).",
    )
    args = parser.parse_args()

    try:
        overrides = parse_key_value_overrides(args.overrides)
    except ValueError as exc:
        print(f"Error: {exc}")
        print()
        print(USAGE)
        raise SystemExit(2) from exc

    if overrides.pop("help", False) or args.config in {"-h", "--help", "help"}:
        print(USAGE)
        return

    config_path = Path(str(args.config))
    full_config_path = config_path if config_path.is_absolute() else ROOT / config_path
    dry_run = bool(args.dry_run or overrides.pop("dry_run", False))

    try:
        experiment_cfg = _load_experiment_config(full_config_path)
        runner_config, summary = _build_runner_config(
            experiment_cfg=experiment_cfg,
            config_path=config_path,
            overrides=overrides,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        print()
        print(USAGE)
        raise SystemExit(2) from exc

    _print_readable_summary(summary, runner_config)

    if dry_run:
        print("Resolved experiment summary:")
        print(json.dumps(summary, indent=2))
        print("\nResolved runner config:")
        print(json.dumps(runner_config, indent=2))
        return

    runner = ExperimentRunner.from_dict(runner_config)
    rows = runner.run()
    print(f"\nCompleted {len(rows)} run(s).")
    output_root = Path(str(summary["output_root"])).resolve()
    if len(rows) == 1 and rows[0].get("run_name"):
        run_dir = output_root / str(rows[0]["run_name"])
        print(f"Output folder: {run_dir}")
    else:
        print(f"Output folder: {output_root}")
        for row in rows:
            run_name = row.get("run_name")
            if run_name:
                print(f"  - {output_root / str(run_name)}")


if __name__ == "__main__":
    main()
