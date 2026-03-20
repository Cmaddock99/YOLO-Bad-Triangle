#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.cli_utils import run_repo_python_script


USAGE = """\
[FRAMEWORK-FIRST ENTRYPOINT] one-command experiment lab

Usage:
  python run_experiment.py --config configs/default.yaml --set attack.name=fgsm
  python run_experiment.py attack=fgsm defense=none model=yolo26n conf=0.25

Shorthand arguments:
  attack=none|blur|gaussian_noise|fgsm|deepfool
  defense=none|median|median_blur|denoise
  model=yolo26|yolo26n|yolo26s|yolo11|yolo11n|yolo11s|yolo8|<weights-path>
  conf=0.5
  imgsz=640
"""


def _legacy_to_framework_args(argv: list[str]) -> list[str]:
    mapped: list[str] = []
    key_map = {
        "attack": "attack.name",
        "defense": "defense.name",
        "model": "model.params.model",
        "conf": "predict.conf",
        "iou": "predict.iou",
        "imgsz": "predict.imgsz",
        "seed": "runner.seed",
        "output_root": "runner.output_root",
        "run_name": "runner.run_name",
        "validate": "validation.enabled",
        "dry_run": "--dry-run",
        "config": "--config",
    }
    for item in argv:
        if item in {"--framework"}:
            continue
        if item in {"--help", "-h", "help"}:
            mapped.append(item)
            continue
        if item == "--list-attacks" or item == "--list-defenses" or item == "--list-models":
            mapped.append("--list-plugins")
            continue
        if item == "--list-datasets":
            mapped.append("--list-plugins")
            continue
        if "=" not in item:
            mapped.append(item)
            continue
        key, value = item.split("=", 1)
        mapped_key = key_map.get(key, key)
        if mapped_key == "--dry-run":
            truthy = value.strip().lower() in {"1", "true", "yes", "on"}
            if truthy:
                mapped.append("--dry-run")
            continue
        if mapped_key == "--config":
            mapped.extend(["--config", value])
            continue
        mapped.extend(["--set", f"{mapped_key}={value}"])
    if "--config" not in mapped:
        mapped.extend(["--config", "configs/default.yaml"])
    return mapped


def main() -> None:
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(USAGE)
        return
    framework_args = _legacy_to_framework_args(argv)
    code = run_repo_python_script(ROOT, "scripts/run_unified.py", ["run-one", *framework_args])
    raise SystemExit(code)


if __name__ == "__main__":
    main()
