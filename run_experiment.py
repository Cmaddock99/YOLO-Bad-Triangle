#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.experiment_registry import ExperimentRegistry, parse_key_value_overrides


USAGE = """\
One-command experiment lab

Usage:
  python run_experiment.py attack=blur model=yolo11 dataset=coco_subset
  python run_experiment.py attack=deepfool defense=denoise

Optional overrides:
  config=configs/experiment_lab.yaml
  conf=0.5               # single threshold
  conf=0.25,0.5,0.75     # multiple thresholds
  iou=0.7 imgsz=640 seed=42
  run_name=my_run run_id=20260311
  attack.kernel_size=11 defense.h=12
  output_root=outputs/experiments
  validate=true dry_run=true
"""


def main() -> None:
    overrides = parse_key_value_overrides(sys.argv[1:])
    if overrides.pop("help", False):
        print(USAGE)
        return

    config_path = Path(str(overrides.pop("config", "configs/experiment_lab.yaml")))
    dry_run = bool(overrides.pop("dry_run", False))

    registry = ExperimentRegistry.from_yaml(ROOT / config_path)
    resolved = registry.resolve(overrides)

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
    print(f"Output root: {resolved.summary['output_root']}")


if __name__ == "__main__":
    main()
