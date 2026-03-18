#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks.registry import list_available_attacks
from lab.defenses.registry import list_available_defenses
from lab.runners.experiment_registry import ExperimentRegistry, parse_key_value_overrides


USAGE = """\
One-command experiment lab

Usage:
  python run_experiment.py attack=blur model=yolo11 defense=median
  python run_experiment.py attack=blur model=yolo11 defense=none conf=0.5 imgsz=640

Key arguments:
  attack=none|blur|gaussian_noise|fgsm|deepfool
  defense=none|median|median_blur|denoise
  model=yolo26|yolo26n|yolo26s|yolo11|yolo11n|yolo11s|yolo8|<weights-path>
  conf=0.5               # single threshold
  conf=0.25,0.5,0.75     # multiple thresholds
  imgsz=640

Discovery flags:
  --list-attacks
  --list-defenses
  --list-models
  --list-datasets

Additional optional overrides:
  config=configs/experiment_lab.yaml
  iou=0.7 imgsz=640 seed=42
  run_name=my_run run_id=20260311
  attack.kernel_size=11 defense.h=12
  output_root=outputs
  validate=true dry_run=true
"""


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


def _print_list(title: str, values: list[str]) -> None:
    print(f"{title}:")
    if not values:
        print("  (none)")
        return
    for value in values:
        print(f"  - {value}")


def main() -> None:
    try:
        overrides = parse_key_value_overrides(sys.argv[1:])
    except ValueError as exc:
        print(f"Error: {exc}")
        print()
        print(USAGE)
        raise SystemExit(2) from exc

    if overrides.pop("help", False):
        print(USAGE)
        return

    config_path = Path(str(overrides.pop("config", "configs/experiment_lab.yaml")))
    dry_run = bool(overrides.pop("dry_run", False))

    registry = ExperimentRegistry.from_yaml(ROOT / config_path)
    requested_lists = {
        "attacks": bool(overrides.pop("list_attacks", False)),
        "defenses": bool(overrides.pop("list_defenses", False)),
        "models": bool(overrides.pop("list_models", False)),
        "datasets": bool(overrides.pop("list_datasets", False)),
    }
    wants_list_output = any(requested_lists.values())
    if wants_list_output:
        if requested_lists["attacks"]:
            config_attacks = registry.available_attack_aliases()
            registered_attacks = list_available_attacks()
            _print_list("Configured attack aliases", config_attacks)
            _print_list("Registered attack plugins", registered_attacks)
        if requested_lists["defenses"]:
            config_defenses = registry.available_defense_aliases()
            registered_defenses = list_available_defenses()
            _print_list("Configured defense aliases", config_defenses)
            _print_list("Registered defense plugins", registered_defenses)
        if requested_lists["models"]:
            _print_list("Configured models", registry.available_models())
        if requested_lists["datasets"]:
            _print_list("Configured datasets", registry.available_datasets())
        return

    resolved = registry.resolve(overrides)
    _print_readable_summary(resolved.summary, resolved.runner_config)

    if dry_run:
        print("Resolved experiment summary:")
        print(json.dumps(resolved.summary, indent=2))
        print("\nResolved runner config:")
        print(json.dumps(resolved.runner_config, indent=2))
        return

    from lab.runners import ExperimentRunner

    runner = ExperimentRunner.from_dict(resolved.runner_config)
    rows = runner.run()
    print(f"\nCompleted {len(rows)} run(s).")
    output_root = Path(str(resolved.summary["output_root"])).resolve()
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
