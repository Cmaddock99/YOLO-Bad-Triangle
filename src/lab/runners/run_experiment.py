#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import yaml

from lab.attacks.framework_registry import build_attack_plugin, list_available_attack_plugins
from lab.attacks.utils import iter_images
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins
from lab.eval.prediction_io import write_predictions_jsonl
from lab.models.registry import build_model, list_available_models


def _load_yaml_mapping(config_path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(config_path.read_text()) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping config in {config_path}")
    return cast(dict[str, Any], loaded)


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        if re.fullmatch(r"[+-]?\d+", value):
            return int(value)
        if re.fullmatch(r"[+-]?\d+\.\d*", value):
            return float(value)
    except ValueError:
        pass
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _apply_override(config: dict[str, Any], assignment: str) -> None:
    if "=" not in assignment:
        raise ValueError(f"Override must use key=value format, got: {assignment}")
    key_path, raw_value = assignment.split("=", 1)
    if not key_path.strip():
        raise ValueError(f"Override key cannot be empty: {assignment}")

    keys = [part for part in key_path.split(".") if part]
    if not keys:
        raise ValueError(f"Invalid override key path: {assignment}")

    node: dict[str, Any] = config
    for key in keys[:-1]:
        existing = node.get(key)
        if existing is None:
            node[key] = {}
            existing = node[key]
        if not isinstance(existing, dict):
            raise ValueError(f"Cannot set nested key under non-mapping path '{key_path}'.")
        node = cast(dict[str, Any], existing)
    node[keys[-1]] = _parse_scalar(raw_value)


def _sanitize_segment(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return cleaned or fallback


def _collect_images(source_dir: Path, max_images: int) -> list[Path]:
    images = sorted(iter_images(source_dir))
    if max_images > 0:
        images = images[:max_images]
    return images


def _as_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping at '{key}'.")
    return cast(dict[str, Any], value)


@dataclass
class UnifiedExperimentRunner:
    """Phase 5 unified runner for baseline/blur/no-defense framework runs."""

    config: dict[str, Any]
    config_path: Path | None = None

    @classmethod
    def from_yaml(cls, config_path: Path) -> "UnifiedExperimentRunner":
        return cls(config=_load_yaml_mapping(config_path), config_path=config_path)

    def _resolve_run_dir(self) -> Path:
        runner_cfg = _as_mapping(self.config, "runner")
        output_root = Path(str(runner_cfg.get("output_root", "outputs/framework_runs")))
        output_root = output_root.expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)

        model_name = str(_as_mapping(self.config, "model").get("name", "model"))
        attack_name = str(_as_mapping(self.config, "attack").get("name", "none"))
        defense_name = str(_as_mapping(self.config, "defense").get("name", "none"))

        run_name = runner_cfg.get("run_name")
        if run_name is None or not str(run_name).strip():
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            run_name = (
                f"{ts}__{_sanitize_segment(model_name, 'model')}"
                f"__{_sanitize_segment(attack_name, 'attack')}"
                f"__{_sanitize_segment(defense_name, 'defense')}"
            )
        run_dir = output_root / str(run_name)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def run(self) -> dict[str, Any]:
        model_cfg = _as_mapping(self.config, "model")
        data_cfg = _as_mapping(self.config, "data")
        attack_cfg = _as_mapping(self.config, "attack")
        defense_cfg = _as_mapping(self.config, "defense")
        runner_cfg = _as_mapping(self.config, "runner")
        predict_cfg = _as_mapping(self.config, "predict")

        model_name = str(model_cfg.get("name", ""))
        if not model_name:
            raise ValueError("config.model.name is required")
        source_dir_raw = data_cfg.get("source_dir")
        if not source_dir_raw:
            raise ValueError("config.data.source_dir is required")

        seed = int(runner_cfg.get("seed", 42))
        random.seed(seed)
        np.random.seed(seed)

        source_dir = Path(str(source_dir_raw)).expanduser().resolve()
        if not source_dir.exists():
            raise FileNotFoundError(f"source_dir not found: {source_dir}")

        run_dir = self._resolve_run_dir()
        prepared_dir = run_dir / "prepared_images"
        prepared_dir.mkdir(parents=True, exist_ok=True)

        max_images = int(runner_cfg.get("max_images", 0))
        images = _collect_images(source_dir, max_images=max_images)
        if not images:
            raise ValueError(f"No images discovered under: {source_dir}")

        model_params = dict(_as_mapping(model_cfg, "params"))
        model = build_model(model_name, **model_params)
        model.load()

        attack_name = str(attack_cfg.get("name", "none")).strip().lower()
        attack_params = dict(_as_mapping(attack_cfg, "params"))
        attack = None
        if attack_name not in {"", "none", "identity"}:
            attack = build_attack_plugin(attack_name, **attack_params)

        defense_name = str(defense_cfg.get("name", "none")).strip().lower()
        defense_params = dict(_as_mapping(defense_cfg, "params"))
        defense = build_defense_plugin(defense_name or "none", **defense_params)

        prepared_paths: list[Path] = []
        for image_path in images:
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            defended_image, _ = defense.preprocess(image)
            transformed = defended_image
            if attack is not None:
                transformed, _ = attack.apply(defended_image, model=model)

            target = prepared_dir / image_path.name
            cv2.imwrite(str(target), transformed)
            prepared_paths.append(target)

        if not prepared_paths:
            raise ValueError("No readable images were processed.")

        predictions = model.predict(prepared_paths, **predict_cfg)
        postprocessed: list[dict[str, Any]] = []
        for record in predictions:
            records, _ = defense.postprocess([record])
            postprocessed.extend(records)

        predictions_file = run_dir / "predictions.jsonl"
        write_predictions_jsonl(postprocessed, predictions_file)

        resolved_config_file = run_dir / "resolved_config.yaml"
        resolved_config_file.write_text(yaml.safe_dump(self.config, sort_keys=False), encoding="utf-8")

        run_summary = {
            "runner": "lab.runners.run_experiment.UnifiedExperimentRunner",
            "run_dir": str(run_dir),
            "source_dir": str(source_dir),
            "input_image_count": len(images),
            "processed_image_count": len(prepared_paths),
            "prediction_record_count": len(postprocessed),
            "model": {"name": model_name, "params": model_params},
            "attack": {"name": attack_name or "none", "params": attack_params},
            "defense": {"name": defense_name or "none", "params": defense_params},
            "predict": predict_cfg,
            "seed": seed,
        }
        summary_file = run_dir / "run_summary.json"
        summary_file.write_text(json.dumps(run_summary, indent=2, sort_keys=True), encoding="utf-8")
        return run_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 5 unified framework runner.")
    parser.add_argument(
        "--config",
        default="configs/lab_framework_phase5.yaml",
        help="Path to framework config YAML.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve and print config without executing a run.",
    )
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override config values using dot keys. Repeatable.",
    )
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List registered framework model/attack/defense plugins and exit.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args, unknown = parser.parse_known_args()

    if args.list_plugins:
        payload = {
            "models": list_available_models(),
            "attacks": ["none", *list_available_attack_plugins()],
            "defenses": list_available_defense_plugins(),
        }
        print(json.dumps(payload, indent=2))
        return

    config_path = Path(args.config).expanduser().resolve()
    runner = UnifiedExperimentRunner.from_yaml(config_path)

    overrides = list(args.set)
    overrides.extend(item for item in unknown if "=" in item)
    if unknown and len(overrides) != len(unknown):
        bad = [item for item in unknown if "=" not in item]
        raise ValueError(f"Unknown arguments: {bad}. Use --set key=value for overrides.")
    if overrides:
        merged = deepcopy(runner.config)
        for assignment in overrides:
            _apply_override(merged, assignment)
        runner.config = merged

    if args.dry_run:
        print("Phase 5 unified framework runner (dry-run)")
        print(json.dumps(runner.config, indent=2, sort_keys=True))
        return
    summary = runner.run()
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
