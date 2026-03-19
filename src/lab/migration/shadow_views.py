from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .metric_semantics import (
    PREDICTION_CONFIDENCE_METRIC_KEYS,
    PREDICTION_DETECTION_METRIC_KEYS,
    VALIDATION_METRIC_KEYS,
)


SHADOW_PAIRED_METRICS_CSV_FIELDS = (
    "pair_id",
    "source",
    "run_name",
    "model",
    "attack",
    "defense",
    "seed",
    "images_with_detections",
    "total_detections",
    "avg_conf",
    "median_conf",
    "p25_conf",
    "p75_conf",
    "precision",
    "recall",
    "mAP50",
    "mAP50-95",
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalized_model_name_from_summary(model_payload: Mapping[str, Any]) -> str:
    name = str(model_payload.get("name", "")).strip().lower()
    params = _mapping(model_payload.get("params"))
    model_ref = str(params.get("model", "")).strip()
    stem = Path(model_ref).stem.lower() if model_ref else ""

    # Framework runner often reports generic plugin name "yolo".
    # For parity metadata, prefer concrete model stem when available.
    if name in {"", "yolo", "ultralytics_yolo"} and stem:
        name = stem
    if name.endswith(".pt"):
        name = name[:-3]

    alias_map = {
        "yolov8n": "yolo8n",
        "yolov8s": "yolo8s",
        "yolov11n": "yolo11n",
        "yolov11s": "yolo11s",
    }
    return alias_map.get(name, name)


def build_legacy_shadow_artifact(legacy_row: Mapping[str, Any]) -> dict[str, Any]:
    predictions: dict[str, Any] = {}
    for key in (*PREDICTION_DETECTION_METRIC_KEYS, *PREDICTION_CONFIDENCE_METRIC_KEYS):
        predictions[key] = legacy_row.get(key)
    validation: dict[str, Any] = {}
    for key in VALIDATION_METRIC_KEYS:
        validation[key] = legacy_row.get(key)
    return {
        "metadata": {
            "run_name": legacy_row.get("run_name", ""),
            "model": legacy_row.get("MODEL", legacy_row.get("model", "")),
            "attack": legacy_row.get("attack", ""),
            "defense": legacy_row.get("defense", ""),
            "seed": legacy_row.get("seed", 0),
        },
        "predictions": predictions,
        "validation": validation,
    }


def build_framework_shadow_artifact(
    *,
    framework_metrics: Mapping[str, Any],
    framework_run_summary: Mapping[str, Any],
) -> dict[str, Any]:
    predictions_payload = _mapping(framework_metrics.get("predictions"))
    confidence_payload = _mapping(predictions_payload.get("confidence"))
    validation_payload = _mapping(framework_metrics.get("validation"))
    model_payload = _mapping(framework_run_summary.get("model"))
    attack_payload = _mapping(framework_run_summary.get("attack"))
    defense_payload = _mapping(framework_run_summary.get("defense"))
    run_name = framework_run_summary.get(
        "run_name",
        Path(str(framework_run_summary.get("run_dir", ""))).name,
    )

    predictions = {
        "images_with_detections": predictions_payload.get("images_with_detections"),
        "total_detections": predictions_payload.get("total_detections"),
        "avg_conf": confidence_payload.get("mean"),
        "median_conf": confidence_payload.get("median"),
        "p25_conf": confidence_payload.get("p25"),
        "p75_conf": confidence_payload.get("p75"),
    }
    validation: dict[str, Any] = {}
    for key in VALIDATION_METRIC_KEYS:
        validation[key] = validation_payload.get(key)
    return {
        "metadata": {
            "run_name": run_name,
            "model": _normalized_model_name_from_summary(model_payload),
            "attack": attack_payload.get("name", ""),
            "defense": defense_payload.get("name", ""),
            "seed": framework_run_summary.get("seed", 0),
        },
        "predictions": predictions,
        "validation": validation,
    }


def build_paired_metrics_row(pair_id: str, source: str, artifact: Mapping[str, Any]) -> dict[str, Any]:
    metadata = _mapping(artifact.get("metadata"))
    predictions = _mapping(artifact.get("predictions"))
    validation = _mapping(artifact.get("validation"))
    return {
        "pair_id": pair_id,
        "source": source,
        "run_name": metadata.get("run_name", ""),
        "model": metadata.get("model", ""),
        "attack": metadata.get("attack", ""),
        "defense": metadata.get("defense", ""),
        "seed": metadata.get("seed", ""),
        "images_with_detections": predictions.get("images_with_detections", ""),
        "total_detections": predictions.get("total_detections", ""),
        "avg_conf": predictions.get("avg_conf", ""),
        "median_conf": predictions.get("median_conf", ""),
        "p25_conf": predictions.get("p25_conf", ""),
        "p75_conf": predictions.get("p75_conf", ""),
        "precision": validation.get("precision", ""),
        "recall": validation.get("recall", ""),
        "mAP50": validation.get("mAP50", ""),
        "mAP50-95": validation.get("mAP50-95", ""),
    }
