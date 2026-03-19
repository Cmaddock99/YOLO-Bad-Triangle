#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.migration import allow_legacy_runtime, legacy_runtime_warning
from lab.runners.cli_utils import run_repo_python_script
from lab.runners.experiment_registry import ExperimentRegistry, parse_key_value_overrides


USAGE = """\
[FRAMEWORK-FIRST ENTRYPOINT] one-command experiment lab

Framework-first usage:
  python run_experiment.py --config configs/lab_framework_phase5.yaml --set attack.name=fgsm
  python run_experiment.py attack=fgsm defense=none model=yolo26n conf=0.25

Legacy rollback mode:
  python run_experiment.py --legacy attack=blur model=yolo11 defense=median

Shorthand arguments (framework mode):
  attack=none|blur|gaussian_noise|fgsm|deepfool
  defense=none|median|median_blur|denoise
  model=yolo26|yolo26n|yolo26s|yolo11|yolo11n|yolo11s|yolo8|<weights-path>
  conf=0.5
  imgsz=640
"""

ENTRY_NOTICE = (
    "FRAMEWORK-FIRST: 'run_experiment.py' now dispatches to "
    "'scripts/run_unified.py run-one' by default. "
    "Use '--legacy' for rollback compatibility mode."
)


def _dispatch_framework_passthrough(argv: list[str]) -> None:
    code = run_repo_python_script(ROOT, "scripts/run_unified.py", ["run-one", *argv])
    raise SystemExit(code)


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
            # Framework runner does not maintain legacy dataset catalog.
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
        mapped.extend(["--config", "configs/lab_framework_phase5.yaml"])
    return mapped


def _run_legacy_mode(argv: list[str]) -> None:
    if not allow_legacy_runtime(context="run_experiment.py --legacy"):
        raise RuntimeError(
            "Legacy runtime is disabled by policy (USE_LEGACY_RUNTIME=false). "
            "Set USE_LEGACY_RUNTIME=true for emergency rollback only."
        )
    legacy_args = [part for part in argv if part != "--legacy"]
    try:
        overrides = parse_key_value_overrides(legacy_args)
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
    resolved = registry.resolve(overrides)
    if dry_run:
        print("Legacy compatibility mode (dry-run).")
        print(resolved.summary)
        return
    from lab.runners import ExperimentRunner
    runner = ExperimentRunner.from_dict(resolved.runner_config)
    rows = runner.run()
    print(f"Legacy rollback run complete: {len(rows)} run(s).")


def main() -> None:
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(USAGE)
        return
    print(ENTRY_NOTICE)
    if "--legacy" in argv:
        print(legacy_runtime_warning(operator_context="run_experiment.py"))
        try:
            _run_legacy_mode(argv)
        except (ValueError, RuntimeError, FileNotFoundError, PermissionError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        return
    framework_args = _legacy_to_framework_args(argv)
    _dispatch_framework_passthrough(framework_args)


if __name__ == "__main__":
    main()
