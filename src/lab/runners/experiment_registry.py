from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from lab.models.model_utils import model_label_from_path, normalize_model_path


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"none", "null"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_key_value_overrides(tokens: list[str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for token in tokens:
        if token in {"-h", "--help", "help"}:
            overrides["help"] = True
            continue
        if "=" not in token:
            raise ValueError(f"Invalid override '{token}'. Expected key=value format.")
        key, raw_value = token.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid override '{token}'. Key cannot be empty.")
        parts = [part.strip() for part in raw_value.split(",")]
        parsed_value: Any
        if len(parts) > 1:
            parsed_value = [_parse_scalar(part) for part in parts if part]
        else:
            parsed_value = _parse_scalar(raw_value.strip())
        overrides[key] = parsed_value
    return overrides


def _prefixed(overrides: dict[str, Any], prefix: str) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for key, value in overrides.items():
        if key.startswith(prefix):
            extracted[key[len(prefix) :]] = value
    return extracted


def _coerce_float_list(value: Any) -> list[float]:
    if isinstance(value, list):
        return [float(v) for v in value]
    return [float(value)]


def _merge_dict(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


@dataclass
class ResolvedExperiment:
    runner_config: dict[str, Any]
    summary: dict[str, Any]


@dataclass
class ExperimentRegistry:
    config: dict[str, Any]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ExperimentRegistry":
        loaded = yaml.safe_load(Path(path).read_text())
        if not isinstance(loaded, dict):
            raise ValueError(f"Expected mapping config in {path}.")
        return cls(config=loaded)

    def resolve(self, overrides: dict[str, Any]) -> ResolvedExperiment:
        cfg = deepcopy(self.config)
        defaults = cfg.get("defaults", {})
        model_alias = str(overrides.get("model", defaults.get("model", "yolo8")))
        dataset_alias = str(overrides.get("dataset", defaults.get("dataset", "coco_subset")))
        attack_alias = str(overrides.get("attack", defaults.get("attack", "none")))
        defense_alias = str(overrides.get("defense", defaults.get("defense", "none")))

        models = cfg.get("models", {})
        datasets = cfg.get("datasets", {})
        attacks = cfg.get("attacks", {})
        defenses = cfg.get("defenses", {})
        if dataset_alias not in datasets:
            raise ValueError(f"Unknown dataset '{dataset_alias}'. Available: {sorted(datasets)}")
        if attack_alias not in attacks:
            raise ValueError(f"Unknown attack '{attack_alias}'. Available: {sorted(attacks)}")
        if defense_alias not in defenses:
            raise ValueError(f"Unknown defense '{defense_alias}'. Available: {sorted(defenses)}")

        if model_alias in models:
            model_entry = models[model_alias]
            if isinstance(model_entry, dict):
                model_path = normalize_model_path(
                    str(model_entry.get("path") or model_entry.get("name") or "")
                )
                model_name = str(model_entry.get("name", model_alias))
                model_label = str(model_entry.get("label") or model_label_from_path(model_path))
            else:
                model_path = normalize_model_path(str(model_entry))
                model_name = model_alias
                model_label = model_label_from_path(model_path)
        else:
            model_path = normalize_model_path(model_alias)
            model_name = Path(model_path).stem
            model_label = model_label_from_path(model_path)

        dataset_entry = datasets[dataset_alias]
        if not isinstance(dataset_entry, dict):
            raise ValueError(f"Dataset '{dataset_alias}' must define data_yaml and image_dir.")
        attack_entry = attacks[attack_alias]
        defense_entry = defenses[defense_alias]
        if not isinstance(attack_entry, dict) or not isinstance(defense_entry, dict):
            raise ValueError("Attack/defense config entries must be maps.")

        attack_name = str(attack_entry.get("module", attack_alias))
        defense_name = str(defense_entry.get("module", defense_alias))

        attack_params = _merge_dict(
            attack_entry.get("params", {}),
            _prefixed(overrides, "attack."),
        )
        defense_params = _merge_dict(
            defense_entry.get("params", {}),
            _prefixed(overrides, "defense."),
        )

        runner_cfg = deepcopy(cfg.get("runner", {}))
        runner_cfg.update(_prefixed(overrides, "runner."))
        if "output_root" in overrides:
            runner_cfg["output_root"] = overrides["output_root"]
        if "imgsz" in overrides:
            runner_cfg["imgsz"] = int(overrides["imgsz"])
        if "iou" in overrides:
            runner_cfg["iou"] = float(overrides["iou"])
        if "seed" in overrides:
            runner_cfg["seed"] = int(overrides["seed"])

        if "confs" in overrides:
            confs = _coerce_float_list(overrides["confs"])
        elif "conf" in overrides:
            confs = _coerce_float_list(overrides["conf"])
        else:
            confs = _coerce_float_list(runner_cfg.get("confs", [0.5]))

        run_validation = bool(overrides.get("validate", runner_cfg.get("run_validation", False)))
        default_run_name = (
            "baseline"
            if attack_alias == "none" and defense_alias == "none"
            else (
                f"{attack_alias}_attack"
                if defense_alias == "none"
                else f"{attack_alias}_attack_with_{defense_alias}_defense"
            )
        )
        run_id = overrides.get("run_id")
        if "run_name" in overrides:
            run_name = str(overrides["run_name"])
        elif run_id is not None:
            run_name = f"{run_id}_{default_run_name}"
        else:
            run_name = default_run_name
        if "{conf_token}" not in run_name and len(confs) > 1:
            run_name = f"{run_name}_conf{{conf_token}}"

        output_root = Path(str(runner_cfg.get("output_root", "outputs")))
        organized_output_root = output_root

        exp_cfg = {
            "name": run_name,
            "run_name_template": run_name,
            "attack": attack_name,
            "attack_label": attack_alias,
            "attack_params": attack_params,
            "defense": defense_name,
            "defense_label": defense_alias,
            "defense_params": defense_params,
            "run_validation": run_validation,
        }
        resolved_runner = {
            "model": {"path": str(model_path), "name": model_name, "label": model_label},
            "data": {
                "data_yaml": str(dataset_entry["data_yaml"]),
                "image_dir": str(dataset_entry["image_dir"]),
            },
            "runner": {
                "confs": confs,
                "iou": float(runner_cfg.get("iou", 0.7)),
                "imgsz": int(runner_cfg.get("imgsz", 640)),
                "seed": int(runner_cfg.get("seed", 0)),
                "output_root": str(organized_output_root),
                "metrics_csv": str(runner_cfg.get("metrics_csv", "metrics_summary.csv")),
            },
            "experiments": [exp_cfg],
        }

        return ResolvedExperiment(
            runner_config=resolved_runner,
            summary={
                "model": model_name,
                "model_label": model_label,
                "dataset": dataset_alias,
                "attack": attack_alias,
                "defense": defense_alias,
                "run_name_template": run_name,
                "output_root": str(organized_output_root),
                "confs": confs,
            },
        )
