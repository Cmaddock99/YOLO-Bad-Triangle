#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform as _platform
import random
import sys
import time
import traceback
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import torch
from tqdm import tqdm
import yaml

from lab.config.contracts import (
    CURRENT_PIPELINE_TRANSFORM_ORDER,
    FRAMEWORK_METRICS_SCHEMA_VERSION,
    FRAMEWORK_RUN_SUMMARY_SCHEMA_VERSION,
    PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE,
)
from lab.config.profiles import resolve_framework_config, should_include_extra_plugins
from lab.attacks.framework_registry import list_available_attack_plugins
from lab.attacks.utils import iter_images
from lab.defenses.framework_registry import list_available_defense_plugins
from lab.eval.framework_metrics import (
    VALIDATION_STATUS_VALUES,
    sanitize_validation_metrics,
    summarize_prediction_metrics,
    validation_status,
)
from lab.eval.prediction_utils import write_predictions_jsonl
from lab.eval.prediction_schema import PredictionRecord, validate_prediction_records
from lab.models.framework_registry import build_model, list_available_models
from lab.plugins import build_plugin_inventory
from lab.runners.run_intent import (
    build_attack_signature as _build_attack_signature,
    build_run_intent,
    build_defense_signature as _build_defense_signature,
    config_fingerprint_sha256,
    normalized_config_for_output as _normalized_config_for_output,  # noqa: F401 — re-exported for tests
    resolve_attack_instance,
    resolve_defense_instance,
    resolved_config_yaml_text,
    resolved_reporting_context as _resolved_reporting_context,
)
from lab.runners.cli_utils import apply_override, as_mapping, load_yaml_mapping, sanitize_segment


def _collect_images(source_dir: Path, max_images: int) -> list[Path]:
    images = sorted(iter_images(source_dir))
    if max_images > 0:
        images = images[:max_images]
    return images


def _assert_metrics_payload_contract(metrics_payload: dict[str, Any]) -> None:
    required_top_level = ("schema_version", "predictions", "validation")
    missing = [key for key in required_top_level if key not in metrics_payload]
    if missing:
        raise ValueError(f"metrics payload missing required top-level keys: {', '.join(missing)}")
    if metrics_payload.get("schema_version") != FRAMEWORK_METRICS_SCHEMA_VERSION:
        raise ValueError(
            f"metrics payload schema_version must be '{FRAMEWORK_METRICS_SCHEMA_VERSION}'."
        )
    predictions = metrics_payload["predictions"]
    if not isinstance(predictions, dict):
        raise ValueError("metrics payload predictions section must be a mapping.")
    required_prediction_keys = ("image_count", "images_with_detections", "total_detections")
    missing_prediction = [key for key in required_prediction_keys if key not in predictions]
    if missing_prediction:
        raise ValueError(
            "metrics payload predictions section missing required keys: "
            f"{', '.join(missing_prediction)}"
        )
    validation = metrics_payload["validation"]
    if not isinstance(validation, dict):
        raise ValueError("metrics payload validation section must be a mapping.")
    if "status" not in validation:
        raise ValueError("metrics payload validation section missing required 'status' key.")
    allowed_status = set(VALIDATION_STATUS_VALUES)
    status = validation["status"]
    if status not in allowed_status:
        raise ValueError(
            f"metrics payload validation.status must be one of {sorted(allowed_status)}, got: {status}"
        )


def _read_json_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WARNING: Failed to read JSON mapping at '{path}': {exc}")
        return {}
    if not isinstance(payload, dict):
        return {}
    return cast(dict[str, Any], payload)


def _split_attack_metadata_payload(attack_meta: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(attack_meta, dict):
        return {}, {}
    raw = dict(attack_meta)
    prediction_metadata = raw.pop("prediction_metadata", {})
    explicit_run_metadata = raw.pop("run_metadata", None)
    run_metadata: dict[str, Any]
    if isinstance(explicit_run_metadata, dict):
        run_metadata = {**explicit_run_metadata, **raw}
    else:
        run_metadata = raw
    if not isinstance(prediction_metadata, dict):
        prediction_metadata = {}
    return dict(run_metadata), dict(prediction_metadata)


def _attach_attack_metadata_to_predictions(
    predictions: list[PredictionRecord],
    attack_prediction_metadata: dict[str, dict[str, Any]],
) -> list[PredictionRecord]:
    if not attack_prediction_metadata:
        return predictions
    for record in predictions:
        image_id = str(record.get("image_id", "")).strip()
        if not image_id:
            continue
        attack_meta = attack_prediction_metadata.get(image_id)
        if not attack_meta:
            continue
        metadata = record.get("metadata")
        merged_metadata = dict(metadata) if isinstance(metadata, dict) else {}
        merged_metadata["attack"] = dict(attack_meta)
        record["metadata"] = merged_metadata
    return predictions


def _is_none_name(name: str) -> bool:
    return name.strip().lower() in {"", "none", "identity"}


def _device_hint() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _collect_summary_candidates(
    *,
    output_root: Path,
    model_name: str,
    seed: int,
    current_run_dir: Path,
    current_attack_name: str,
    current_defense_name: str,
    current_metrics: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = [
        {
            "run_dir": current_run_dir,
            "attack": current_attack_name,
            "defense": current_defense_name,
            "attack_signature": "",
            "defense_signature": "",
            "metrics": current_metrics,
        }
    ]
    if not output_root.exists():
        return candidates

    for run_dir in sorted(path for path in output_root.iterdir() if path.is_dir()):
        if run_dir.resolve() == current_run_dir.resolve():
            continue
        summary_payload = _read_json_mapping(run_dir / "run_summary.json")
        metrics_payload = _read_json_mapping(run_dir / "metrics.json")
        if not summary_payload or not metrics_payload:
            continue

        summary_model = str((summary_payload.get("model") or {}).get("name", "")).strip().lower()
        if summary_model != model_name.strip().lower():
            continue
        try:
            summary_seed = int(summary_payload.get("seed", 0))
        except (TypeError, ValueError):
            summary_seed = 0
        if summary_seed != seed:
            continue

        candidates.append(
            {
                "run_dir": run_dir,
                "attack": str((summary_payload.get("attack") or {}).get("name", "none")),
                "defense": str((summary_payload.get("defense") or {}).get("name", "none")),
                "attack_signature": _build_attack_signature(
                    attack_name=str((summary_payload.get("attack") or {}).get("name", "none")),
                    attack_params=dict((summary_payload.get("attack") or {}).get("params") or {}),
                    resolved_objective=dict((summary_payload.get("attack") or {}).get("resolved_objective") or {}),
                ),
                "defense_signature": _build_defense_signature(
                    defense_name=str((summary_payload.get("defense") or {}).get("name", "none")),
                    defense_params=dict((summary_payload.get("defense") or {}).get("params") or {}),
                ),
                "metrics": metrics_payload,
            }
        )
    return candidates


def _select_related_summary_metrics(
    candidates: list[dict[str, Any]],
    *,
    current_attack_name: str,
    current_attack_signature: str,
    current_defense_signature: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    baseline_candidate = next(
        (
            item
            for item in candidates
            if _is_none_name(str(item.get("attack", "none"))) and _is_none_name(str(item.get("defense", "none")))
        ),
        None,
    )
    if baseline_candidate is None:
        return None, None, None

    attack_name = current_attack_name.strip().lower()
    if _is_none_name(attack_name):
        inferred_attack_names = sorted(
            {
                str(item.get("attack", "")).strip().lower()
                for item in candidates
                if not _is_none_name(str(item.get("attack", "")))
            }
        )
        if not inferred_attack_names:
            return baseline_candidate.get("metrics"), None, None
        attack_name = inferred_attack_names[0]

    attack_candidate = next(
        (
            item
            for item in candidates
            if (
                str(item.get("attack_signature", "")) == current_attack_signature
                or str(item.get("attack", "")).strip().lower() == attack_name
            )
            and _is_none_name(str(item.get("defense", "none")))
        ),
        None,
    )
    defense_candidate = next(
        (
            item
            for item in candidates
            if (
                str(item.get("attack_signature", "")) == current_attack_signature
                or str(item.get("attack", "")).strip().lower() == attack_name
            )
            and str(item.get("defense_signature", "")) == current_defense_signature
        ),
        None,
    )
    baseline_metrics = cast(dict[str, Any], baseline_candidate.get("metrics"))
    attack_metrics = cast(dict[str, Any] | None, attack_candidate.get("metrics") if attack_candidate else None)
    defense_metrics = cast(dict[str, Any] | None, defense_candidate.get("metrics") if defense_candidate else None)
    return baseline_metrics, attack_metrics, defense_metrics


@dataclass
class UnifiedExperimentRunner:
    """Unified runner with structured outputs and metrics capture."""

    config: dict[str, Any]
    config_path: Path | None = None

    @classmethod
    def from_yaml(cls, config_path: Path) -> "UnifiedExperimentRunner":
        return cls(config=load_yaml_mapping(config_path), config_path=config_path)

    def _resolve_run_dir(self) -> Path:
        runner_cfg = as_mapping(self.config, "runner")
        output_root = Path(str(runner_cfg.get("output_root", "outputs/framework_runs")))
        output_root = output_root.expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)

        model_name = str(as_mapping(self.config, "model").get("name", "model"))
        attack_name = str(as_mapping(self.config, "attack").get("name", "none"))
        defense_name = str(as_mapping(self.config, "defense").get("name", "none"))

        run_name = runner_cfg.get("run_name")
        if run_name is None or not str(run_name).strip():
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            run_name = (
                f"{ts}__{sanitize_segment(model_name, 'model')}"
                f"__{sanitize_segment(attack_name, 'attack')}"
                f"__{sanitize_segment(defense_name, 'defense')}"
            )
        run_dir = output_root / str(run_name)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _prepare_images(
        self,
        *,
        run_dir: Path,
        model: Any,
        attack: Any,
        defense: Any,
        images: list[Path],
        seed: int,
        attack_name: str,
    ) -> tuple[list[Path], int, int, dict[str, Any], dict[str, dict[str, Any]], dict[str, float]]:
        """Apply attack and defense preprocessing, write results to images/.

        Returns (prepared_paths, skipped_unreadable, failed_writes, attack_metadata,
        attack_prediction_metadata, timing_ms).
        """
        prepared_dir = run_dir / "images"
        prepared_dir.mkdir(parents=True, exist_ok=True)
        prepared_paths: list[Path] = []
        skipped_unreadable = 0
        failed_writes = 0
        attack_metadata: dict[str, Any] = {}
        attack_prediction_metadata: dict[str, dict[str, Any]] = {}
        attack_elapsed = 0.0
        defense_preprocess_elapsed = 0.0
        image_write_elapsed = 0.0
        for index, image_path in enumerate(
            tqdm(images, desc="Preparing images", unit="img", dynamic_ncols=True)
        ):
            image = cv2.imread(str(image_path))
            if image is None:
                skipped_unreadable += 1
                continue
            transformed = image
            prediction_attack_meta: dict[str, Any] = {}
            if attack is not None:
                attack_started = time.monotonic()
                transformed, attack_meta = attack.apply(
                    image,
                    model=model,
                    seed=int(seed) + index,
                )
                attack_elapsed += time.monotonic() - attack_started
                run_attack_meta, prediction_attack_meta = _split_attack_metadata_payload(attack_meta)
                if run_attack_meta and not attack_metadata:
                    attack_metadata = cast(dict[str, Any], dict(run_attack_meta))
            defense_started = time.monotonic()
            defended_image, _ = defense.preprocess(
                transformed,
                attack_hint=attack_name,
                attack_metadata=prediction_attack_meta,
                attack_run_metadata=attack_metadata,
            )
            defense_preprocess_elapsed += time.monotonic() - defense_started
            target = prepared_dir / image_path.name
            write_started = time.monotonic()
            wrote = cv2.imwrite(str(target), defended_image)
            image_write_elapsed += time.monotonic() - write_started
            if not wrote:
                failed_writes += 1
                continue
            prepared_paths.append(target)
            if prediction_attack_meta:
                attack_prediction_metadata[target.name] = dict(prediction_attack_meta)
        if not prepared_paths:
            raise ValueError(
                "No images were prepared for inference. "
                f"unreadable={skipped_unreadable}, failed_writes={failed_writes}, "
                f"source_count={len(images)}"
            )
        if attack_metadata and attack_prediction_metadata:
            base_patch_size = attack_metadata.get("applied_patch_size")
            attack_metadata = {
                **attack_metadata,
                "images_with_person_detection": sum(
                    1 for meta in attack_prediction_metadata.values() if bool(meta.get("person_found"))
                ),
                "images_with_center_fallback": sum(
                    1 for meta in attack_prediction_metadata.values() if bool(meta.get("fallback_used"))
                ),
                "images_with_patch_downscale": sum(
                    1
                    for meta in attack_prediction_metadata.values()
                    if base_patch_size is not None and meta.get("applied_patch_size") != base_patch_size
                ),
            }
        return prepared_paths, skipped_unreadable, failed_writes, attack_metadata, attack_prediction_metadata, {
            "attack_ms": round(attack_elapsed * 1000, 1),
            "defense_preprocess_ms": round(defense_preprocess_elapsed * 1000, 1),
            "image_write_ms": round(image_write_elapsed * 1000, 1),
        }

    def _run_inference(
        self,
        *,
        model: Any,
        prepared_paths: list[Path],
        predict_cfg: dict[str, Any],
        defense: Any,
        attack_prediction_metadata: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[list[PredictionRecord], dict[str, float]]:
        """Run model prediction and defense postprocessing."""
        predict_started = time.monotonic()
        predictions = model.predict(prepared_paths, **predict_cfg)
        predict_elapsed = time.monotonic() - predict_started
        postprocessed: list[PredictionRecord] = []
        defense_postprocess_elapsed = 0.0
        for record in predictions:
            postprocess_started = time.monotonic()
            records, _ = defense.postprocess([record])
            defense_postprocess_elapsed += time.monotonic() - postprocess_started
            postprocessed.extend(records)
        postprocessed = _attach_attack_metadata_to_predictions(
            postprocessed,
            attack_prediction_metadata or {},
        )
        if prepared_paths and not postprocessed:
            raise RuntimeError(
                "Model returned zero prediction records for non-empty prepared inputs. "
                f"processed_image_count={len(prepared_paths)}"
            )
        validate_prediction_records(postprocessed)
        return postprocessed, {
            "predict_ms": round(predict_elapsed * 1000, 1),
            "defense_postprocess_ms": round(defense_postprocess_elapsed * 1000, 1),
        }

    def _run_validation(
        self,
        *,
        model: Any,
        validation_cfg: dict[str, Any],
        prepared_dir: Path,
    ) -> tuple[dict[str, Any], str | None]:
        """Run optional model validation against the attacked prepared images.

        Returns ({cleaned_metrics..., status}, error_message).
        """
        validation_enabled = bool(validation_cfg.get("enabled", False))
        validation_dataset = validation_cfg.get("dataset")
        validation_params = dict(as_mapping(validation_cfg, "params"))
        raw_validation_metrics: dict[str, Any] | None = None
        validation_error: str | None = None
        validation_traceback: str | None = None
        capability_supported = validation_enabled
        capability_reason: str | None = None
        if validation_enabled:
            if not validation_dataset:
                raise ValueError(
                    "validation.enabled=true requires config.validation.dataset "
                    "(for example: configs/coco_subset500.yaml)."
                )
            try:
                # Build a temporary dataset YAML pointing at the attacked images
                # so validation measures mAP on the perturbed inputs, not the originals.
                orig_yaml_path = Path(str(validation_dataset)).expanduser().resolve()
                orig_cfg = yaml.safe_load(orig_yaml_path.read_text(encoding="utf-8"))
                orig_root = Path(str(orig_cfg.get("path", ""))).expanduser()
                if not orig_root.is_absolute():
                    orig_root = (Path.cwd() / orig_root).resolve()
                orig_labels = orig_root / "labels"

                # Ultralytics path substitution replaces /images/ with /labels/
                # when locating label files. Attacked images are stored in the
                # "images/" subdirectory; we symlink "labels/" → orig_labels so
                # the substitution resolves correctly.
                run_dir = prepared_dir.parent
                labels_link = run_dir / "labels"
                if not labels_link.exists():
                    labels_link.symlink_to(orig_labels.resolve())

                # Write a minimal dataset YAML that points val at images/.
                attacked_yaml = run_dir / "val_attacked_dataset.yaml"
                attacked_cfg = {k: v for k, v in orig_cfg.items() if k not in ("path", "train", "val", "test")}
                attacked_cfg["path"] = str(run_dir)
                attacked_cfg["train"] = "images"
                attacked_cfg["val"] = "images"
                attacked_yaml.write_text(yaml.safe_dump(attacked_cfg, sort_keys=False), encoding="utf-8")

                raw_validation_metrics = model.validate(str(attacked_yaml), **validation_params)
            except Exception as exc:  # pragma: no cover - runtime path
                validation_error = str(exc)
                validation_traceback = traceback.format_exc(limit=12)
        if isinstance(raw_validation_metrics, dict):
            raw_status = str(raw_validation_metrics.get("_status") or "").strip().lower()
            if raw_status == "not_supported":
                capability_supported = False
                capability_reason = "model_adapter_reports_not_supported"
        cleaned = sanitize_validation_metrics(raw_validation_metrics)
        state = validation_status(cleaned)
        if validation_error is not None:
            state = "error"
            if capability_reason is None and validation_enabled:
                capability_reason = "validation_runtime_error"
        if state == "partial":
            print(
                "WARNING: validation metrics are partial — some metrics could not be computed. "
                "Check that a validation dataset was provided and is accessible."
            )
        return {
            **cleaned,
            "status": state,
            "capability_supported": capability_supported,
            "capability_reason": capability_reason,
            "error_traceback": validation_traceback,
        }, validation_error

    def _generate_experiment_summary(
        self,
        *,
        run_dir: Path,
        model_name: str,
        seed: int,
        attack_name: str,
        defense_name: str,
        attack_params: dict[str, Any],
        defense_params: dict[str, Any],
        attack_metadata: dict[str, Any],
        metrics_payload: dict[str, Any],
        runner_cfg: dict[str, Any],
    ) -> None:
        """Generate optional multi-run comparison summary."""
        summary_cfg = as_mapping(self.config, "summary")
        if not bool(summary_cfg.get("enabled", False)):
            return
        from lab.reporting.local import generate_summary

        output_root = Path(
            str(runner_cfg.get("output_root", "outputs/framework_runs"))
        ).expanduser().resolve()
        candidates = _collect_summary_candidates(
            output_root=output_root,
            model_name=model_name,
            seed=seed,
            current_run_dir=run_dir,
            current_attack_name=attack_name,
            current_defense_name=defense_name,
            current_metrics=metrics_payload,
        )
        current_attack_signature = _build_attack_signature(
            attack_name=attack_name,
            attack_params=attack_params,
            resolved_objective=attack_metadata,
        )
        current_defense_signature = _build_defense_signature(
            defense_name=defense_name,
            defense_params=defense_params,
        )
        candidates[0]["attack_signature"] = current_attack_signature
        candidates[0]["defense_signature"] = current_defense_signature
        baseline_metrics, attack_metrics, defense_metrics = _select_related_summary_metrics(
            candidates,
            current_attack_name=attack_name,
            current_attack_signature=current_attack_signature,
            current_defense_signature=current_defense_signature,
        )
        if baseline_metrics is None or attack_metrics is None:
            print(
                "WARNING: Summary generation skipped; related baseline/attack framework runs were not found."
            )
            return
        experiment_summary = generate_summary(
            baseline_metrics=baseline_metrics,
            attack_metrics=attack_metrics,
            defense_metrics=defense_metrics,
        )
        experiment_summary_file = run_dir / "experiment_summary.json"
        experiment_summary_file.write_text(
            json.dumps(experiment_summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(f"Experiment summary written: {experiment_summary_file}")

    def run(self) -> dict[str, Any]:
        model_cfg = as_mapping(self.config, "model")
        data_cfg = as_mapping(self.config, "data")
        attack_cfg = as_mapping(self.config, "attack")
        defense_cfg = as_mapping(self.config, "defense")
        runner_cfg = as_mapping(self.config, "runner")
        predict_cfg = as_mapping(self.config, "predict")
        validation_cfg = as_mapping(self.config, "validation")
        reporting_context = _resolved_reporting_context(self.config)

        model_name = str(model_cfg.get("name", ""))
        if not model_name:
            raise ValueError("config.model.name is required")
        source_dir_raw = data_cfg.get("source_dir")
        if not source_dir_raw:
            raise ValueError("config.data.source_dir is required")

        seed = int(runner_cfg.get("seed", 42))
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        source_dir = Path(str(source_dir_raw)).expanduser().resolve()
        if not source_dir.exists():
            raise FileNotFoundError(f"source_dir not found: {source_dir}")

        run_dir = self._resolve_run_dir()

        max_images = int(runner_cfg.get("max_images", 0))
        images = _collect_images(source_dir, max_images=max_images)
        if not images:
            raise ValueError(f"No images discovered under: {source_dir}")

        run_started_at = datetime.now(timezone.utc)
        run_started_mono = time.monotonic()
        include_extra = should_include_extra_plugins(self.config)
        model_params = dict(as_mapping(model_cfg, "params"))
        model = build_model(model_name, include_extra=include_extra, **model_params)
        model.load()

        attack_name = str(attack_cfg.get("name", "none")).strip().lower()
        attack_params = dict(as_mapping(attack_cfg, "params"))
        attack, attack_params, resolved_objective = resolve_attack_instance(
            attack_name,
            attack_params,
            include_extra=include_extra,
        )

        defense_name = str(defense_cfg.get("name", "none")).strip().lower()
        defense_params = dict(as_mapping(defense_cfg, "params"))
        defense, defense_params, defense_checkpoint_provenance = resolve_defense_instance(
            defense_name,
            defense_params,
            include_extra=include_extra,
        )

        (
            prepared_paths,
            skipped_unreadable,
            failed_writes,
            attack_metadata,
            attack_prediction_metadata,
            prepare_timing,
        ) = self._prepare_images(
            run_dir=run_dir,
            model=model,
            attack=attack,
            defense=defense,
            images=images,
            seed=seed,
            attack_name=attack_name or "none",
        )
        resolved_objective = {
            **resolved_objective,
            **{
                key: attack_metadata.get(key, resolved_objective.get(key))
                for key in ("objective_mode", "target_class", "attack_roi", "preserve_weight")
            },
        }

        postprocessed, inference_timing = self._run_inference(
            model=model,
            prepared_paths=prepared_paths,
            predict_cfg=predict_cfg,
            defense=defense,
            attack_prediction_metadata=attack_prediction_metadata,
        )
        runtime_metrics: dict[str, float | None] = {
            **prepare_timing,
            **inference_timing,
            "validation_ms": None,
            "artifact_write_ms": None,
            "total_ms": None,
        }

        prediction_metrics = summarize_prediction_metrics(postprocessed)

        validation_started = time.monotonic()
        validation_section, validation_error = self._run_validation(
            model=model,
            validation_cfg=validation_cfg,
            prepared_dir=run_dir / "images",
        )
        runtime_metrics["validation_ms"] = round((time.monotonic() - validation_started) * 1000, 1)
        validation_enabled = bool(validation_cfg.get("enabled", False))
        validation_dataset = validation_cfg.get("dataset")
        runtime_payload = {
            "started_at_utc": run_started_at.isoformat(),
            "finished_at_utc": None,
            "attack_ms": runtime_metrics["attack_ms"],
            "defense_preprocess_ms": runtime_metrics["defense_preprocess_ms"],
            "image_write_ms": runtime_metrics["image_write_ms"],
            "predict_ms": runtime_metrics["predict_ms"],
            "defense_postprocess_ms": runtime_metrics["defense_postprocess_ms"],
            "validation_ms": runtime_metrics["validation_ms"],
            "artifact_write_ms": runtime_metrics["artifact_write_ms"],
            "total_ms": runtime_metrics["total_ms"],
        }
        metrics_payload: dict[str, Any] = {
            "schema_version": FRAMEWORK_METRICS_SCHEMA_VERSION,
            "validation": {
                **validation_section,
                "enabled": validation_enabled,
                "dataset": str(validation_dataset) if validation_dataset else None,
                "error": validation_error,
            },
            "predictions": prediction_metrics,
            "provenance": {
                "transform_order": list(CURRENT_PIPELINE_TRANSFORM_ORDER),
                "semantic_order": PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE,
                "attack_applied": attack is not None,
            },
            "runtime": dict(runtime_payload),
        }
        _assert_metrics_payload_contract(metrics_payload)
        resolved_config_file = run_dir / "resolved_config.yaml"
        resolved_config_text = resolved_config_yaml_text(self.config)
        run_intent = build_run_intent(self.config, cwd=Path.cwd())
        config_fingerprint = str(run_intent.get("config_fingerprint_sha256") or config_fingerprint_sha256(self.config))
        checkpoint_fingerprint = run_intent.get("checkpoint_fingerprint_sha256")
        checkpoint_source = run_intent.get("checkpoint_fingerprint_source")
        defense_checkpoint_provenance = list(run_intent.get("defense_checkpoints") or defense_checkpoint_provenance)
        pipeline_profile = run_intent.get("pipeline_profile")
        authoritative_metric = run_intent.get("authoritative_metric")
        profile_compatibility = run_intent.get("profile_compatibility")
        attack_signature = str(
            run_intent.get("attack_signature")
            or _build_attack_signature(
                attack_name=attack_name or "none",
                attack_params=attack_params,
                resolved_objective=resolved_objective,
            )
        )
        defense_signature = str(
            run_intent.get("defense_signature")
            or _build_defense_signature(
                defense_name=defense_name or "none",
                defense_params=defense_params,
            )
        )
        predictions_file = run_dir / "predictions.jsonl"
        metrics_file = run_dir / "metrics.json"
        summary_file = run_dir / "run_summary.json"
        provenance_payload = cast(dict[str, Any], metrics_payload["provenance"])
        provenance_payload["pipeline_profile"] = pipeline_profile
        provenance_payload["authoritative_metric"] = authoritative_metric
        provenance_payload["profile_compatibility"] = profile_compatibility
        provenance_payload["attack_metadata"] = attack_metadata if attack_metadata else None

        run_summary = {
            "schema_version": FRAMEWORK_RUN_SUMMARY_SCHEMA_VERSION,
            "runner": "lab.runners.run_experiment.UnifiedExperimentRunner",
            "run_dir": str(run_dir),
            "source_dir": str(source_dir),
            "input_image_count": len(images),
            "processed_image_count": len(prepared_paths),
            "skipped_unreadable_images": skipped_unreadable,
            "failed_image_writes": failed_writes,
            "prediction_record_count": len(postprocessed),
            "model": {"name": model_name, "params": model_params},
            "attack": {
                "name": attack_name or "none",
                "params": attack_params,
                "signature": attack_signature,
                "metadata": attack_metadata if attack_metadata else None,
                "resolved_objective": {
                    "objective_mode": resolved_objective.get("objective_mode"),
                    "target_class": resolved_objective.get("target_class"),
                    "attack_roi": resolved_objective.get("attack_roi"),
                    "preserve_weight": resolved_objective.get("preserve_weight"),
                },
            },
            "defense": {
                "name": defense_name or "none",
                "params": defense_params,
                "signature": defense_signature,
            },
            "pipeline": {
                "transform_order": list(CURRENT_PIPELINE_TRANSFORM_ORDER),
                "semantic_order": PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE,
                "attack_applied": attack is not None,
            },
            "predict": predict_cfg,
            "validation": metrics_payload["validation"],
            "metrics_path": str(metrics_file),
            "seed": seed,
            "pipeline_profile": pipeline_profile,
            "authoritative_metric": authoritative_metric,
            "profile_compatibility": profile_compatibility,
            "reproducibility": {
                "seed": seed,
                "torch_version": torch.__version__,
                "platform": f"{sys.platform}-{_platform.machine()}",
                "torch_seeded": True,
            },
            "provenance": {
                "config_fingerprint_sha256": config_fingerprint,
                "config_fingerprint_source": str(resolved_config_file),
                "checkpoint_fingerprint_sha256": checkpoint_fingerprint,
                "checkpoint_fingerprint_source": checkpoint_source,
                "defense_checkpoints": defense_checkpoint_provenance,
            },
            "runtime": {
                **runtime_payload,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": f"{sys.platform}-{_platform.machine()}",
                "device_hint": _device_hint(),
            },
        }
        if reporting_context:
            run_summary["reporting_context"] = reporting_context

        artifact_write_started = time.monotonic()
        write_predictions_jsonl(postprocessed, predictions_file)

        self._generate_experiment_summary(
            run_dir=run_dir,
            model_name=model_name,
            seed=seed,
            attack_name=attack_name or "none",
            defense_name=defense_name or "none",
            attack_params=attack_params,
            defense_params=defense_params,
            attack_metadata=resolved_objective,
            metrics_payload=metrics_payload,
            runner_cfg=runner_cfg,
        )

        resolved_config_file.write_text(resolved_config_text, encoding="utf-8")
        # metrics.json and run_summary.json are written once below, after the
        # runtime block is fully populated. A prior double-write left partial
        # artifacts on disk (missing total_ms / finished_at_utc) if a crash
        # occurred between the two writes; the single write eliminates that window.

        runtime_payload["artifact_write_ms"] = round((time.monotonic() - artifact_write_started) * 1000, 1)
        run_finished_at = datetime.now(timezone.utc)
        runtime_payload["finished_at_utc"] = run_finished_at.isoformat()
        runtime_payload["total_ms"] = round((time.monotonic() - run_started_mono) * 1000, 1)
        metrics_payload["runtime"] = dict(runtime_payload)
        run_summary["runtime"] = {
            **runtime_payload,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": f"{sys.platform}-{_platform.machine()}",
            "device_hint": _device_hint(),
        }
        # Write run_summary.json first, metrics.json last.
        # metrics.json is the completion sentinel checked by run_single — it must only
        # appear on disk after both other required artifacts are durably written.
        summary_tmp = summary_file.with_suffix(".json.tmp")
        summary_tmp.write_text(json.dumps(run_summary, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(summary_tmp, summary_file)

        metrics_tmp = metrics_file.with_suffix(".json.tmp")
        metrics_tmp.write_text(json.dumps(metrics_payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(metrics_tmp, metrics_file)
        return run_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified framework runner.")
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Path to framework config YAML.",
    )
    config_group.add_argument(
        "--profile",
        help="Named pipeline profile from configs/pipeline_profiles.yaml.",
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
    try:
        args, unknown = parser.parse_known_args()

        if args.list_plugins:
            inventory_profile = args.profile or "yolo11n_lab_v1"
            payload = {
                "models": list_available_models(),
                "attacks": ["none", *list_available_attack_plugins()],
                "defenses": list_available_defense_plugins(),
                "plugin_inventory": build_plugin_inventory(inventory_profile),
            }
            print(json.dumps(payload, indent=2))
            return

        config_path_arg = None if args.profile else Path(args.config).expanduser().resolve()
        resolved_config, resolved_path = resolve_framework_config(
            config_path=config_path_arg,
            profile_name=args.profile,
        )
        runner = UnifiedExperimentRunner(config=resolved_config, config_path=resolved_path)

        overrides = list(args.set)
        overrides.extend(item for item in unknown if "=" in item)
        if unknown and len(overrides) != len(unknown):
            bad = [item for item in unknown if "=" not in item]
            raise ValueError(f"Unknown arguments: {bad}. Use --set key=value for overrides.")
        if overrides:
            merged = deepcopy(runner.config)
            for assignment in overrides:
                apply_override(merged, assignment)
            runner.config = merged

        if args.dry_run:
            print("Unified framework runner (dry-run)")
            print(json.dumps(runner.config, indent=2, sort_keys=True))
            return
        summary = runner.run()
        print(json.dumps(summary, indent=2, sort_keys=True))
    except (ValueError, FileNotFoundError, RuntimeError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
