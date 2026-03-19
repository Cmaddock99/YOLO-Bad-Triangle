from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Mapping

from lab.eval.metric_deltas import (
    delta_entry_within_threshold,
    metric_delta_entry,
    worst_relative_delta_pct,
)
from lab.config.contracts import (
    DEFAULT_MAX_CONFIDENCE_DELTA_PCT,
    DEFAULT_MAX_DETECTION_DELTA_PCT,
)
from lab.migration.metric_semantics import (
    PREDICTION_CONFIDENCE_METRIC_KEYS,
    PREDICTION_DETECTION_METRIC_KEYS,
    VALIDATION_METRIC_KEYS,
    to_optional_float,
)
from lab.migration.shadow_views import (
    build_framework_shadow_artifact,
    build_legacy_shadow_artifact,
)
from lab.reporting.name_normalization import is_none_like, normalize_name


@dataclass
class ValidationGateConfig:
    required_attacks: set[str]


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _read_last_legacy_row(csv_path: Path) -> dict[str, str]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows found in legacy metrics CSV: {csv_path}")
    return rows[-1]


def _load_prediction_stats(predictions_jsonl_path: Path) -> dict[str, float | int | None]:
    if not predictions_jsonl_path.is_file():
        raise FileNotFoundError(f"framework predictions.jsonl not found: {predictions_jsonl_path}")

    image_count = 0
    total_detections = 0
    images_with_detections = 0
    scores: list[float] = []

    with predictions_jsonl_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            image_count += 1
            parsed = json.loads(line)
            boxes = parsed.get("boxes", [])
            box_count = len(boxes) if isinstance(boxes, list) else 0
            total_detections += box_count
            if box_count > 0:
                images_with_detections += 1
            raw_scores = parsed.get("scores", [])
            if isinstance(raw_scores, list):
                for raw_score in raw_scores:
                    score = to_optional_float(raw_score)
                    if score is not None:
                        scores.append(score)

    return {
        "image_count": image_count,
        "images_with_detections": images_with_detections,
        "total_detections": total_detections,
        "avg_conf": (sum(scores) / len(scores)) if scores else None,
        "median_conf": float(median(scores)) if scores else None,
    }


def _relative_delta_pct(legacy_value: float, framework_value: float) -> float | None:
    if legacy_value == 0.0:
        return None
    return ((framework_value - legacy_value) / abs(legacy_value)) * 100.0


def compare_legacy_csv_to_framework_artifacts(
    *,
    legacy_csv: str | Path,
    framework_metrics_json: str | Path,
    predictions_jsonl: str | Path,
    float_tolerance: float = 1e-6,
) -> dict[str, Any]:
    """Single-source parity comparator for legacy CSV vs framework artifacts."""
    legacy_csv_path = Path(legacy_csv).expanduser().resolve()
    framework_metrics_path = Path(framework_metrics_json).expanduser().resolve()
    predictions_jsonl_path = Path(predictions_jsonl).expanduser().resolve()

    legacy_row = _read_last_legacy_row(legacy_csv_path)
    framework_metrics = read_framework_metrics(framework_metrics_path.parent)
    prediction_stats = _load_prediction_stats(predictions_jsonl_path)

    framework_predictions = framework_metrics.get("predictions", {})
    framework_validation = framework_metrics.get("validation", {})
    if not isinstance(framework_predictions, Mapping):
        framework_predictions = {}
    if not isinstance(framework_validation, Mapping):
        framework_validation = {}

    metric_pairs = [
        (
            "images_with_detections",
            to_optional_float(legacy_row.get("images_with_detections")),
            to_optional_float(prediction_stats.get("images_with_detections")),
            0.0,
        ),
        (
            "total_detections",
            to_optional_float(legacy_row.get("total_detections")),
            to_optional_float(prediction_stats.get("total_detections")),
            0.0,
        ),
        (
            "avg_conf",
            to_optional_float(legacy_row.get("avg_conf")),
            to_optional_float(prediction_stats.get("avg_conf")),
            float_tolerance,
        ),
        (
            "median_conf",
            to_optional_float(legacy_row.get("median_conf")),
            to_optional_float(prediction_stats.get("median_conf")),
            float_tolerance,
        ),
        (
            "precision",
            to_optional_float(legacy_row.get("precision")),
            to_optional_float(framework_validation.get("precision")),
            float_tolerance,
        ),
        (
            "recall",
            to_optional_float(legacy_row.get("recall")),
            to_optional_float(framework_validation.get("recall")),
            float_tolerance,
        ),
        (
            "mAP50",
            to_optional_float(legacy_row.get("mAP50")),
            to_optional_float(framework_validation.get("mAP50")),
            float_tolerance,
        ),
        (
            "mAP50-95",
            to_optional_float(legacy_row.get("mAP50-95")),
            to_optional_float(framework_validation.get("mAP50-95")),
            float_tolerance,
        ),
    ]

    compared_metrics: list[dict[str, Any]] = []
    fail_count = 0
    compared_count = 0
    worst_metric_delta: dict[str, Any] | None = None

    for metric_name, legacy_value, framework_value, tolerance in metric_pairs:
        if legacy_value is None or framework_value is None:
            compared_metrics.append(
                {
                    "metric": metric_name,
                    "legacy_value": legacy_value,
                    "framework_value": framework_value,
                    "tolerance": tolerance,
                    "status": "SKIP",
                    "delta": None,
                    "relative_delta_pct": None,
                }
            )
            continue

        compared_count += 1
        delta = framework_value - legacy_value
        delta_abs = abs(delta)
        relative_delta = _relative_delta_pct(legacy_value, framework_value)
        status = "PASS" if delta_abs <= tolerance else "FAIL"
        if status == "FAIL":
            fail_count += 1

        metric_result = {
            "metric": metric_name,
            "legacy_value": legacy_value,
            "framework_value": framework_value,
            "tolerance": tolerance,
            "status": status,
            "delta": delta,
            "absolute_delta": delta_abs,
            "relative_delta_pct": relative_delta,
        }
        compared_metrics.append(metric_result)

        if worst_metric_delta is None or delta_abs > float(worst_metric_delta["absolute_delta"]):
            worst_metric_delta = {
                "metric": metric_name,
                "absolute_delta": delta_abs,
                "relative_delta_pct": relative_delta,
            }

    overall_status = "PASS"
    notes: list[str] = []
    if compared_count == 0:
        overall_status = "FAIL"
        notes.append("No comparable parity metrics were available.")
    elif fail_count > 0:
        overall_status = "FAIL"

    framework_summary = {
        "predictions": {
            "image_count_metrics_json": to_optional_float(framework_predictions.get("image_count")),
            "image_count_predictions_jsonl": to_optional_float(prediction_stats.get("image_count")),
            "images_with_detections": to_optional_float(prediction_stats.get("images_with_detections")),
            "total_detections": to_optional_float(prediction_stats.get("total_detections")),
        },
        "validation_status": framework_validation.get("status"),
    }

    return {
        "overall_status": overall_status,
        "legacy_csv_path": str(legacy_csv_path),
        "framework_metrics_json_path": str(framework_metrics_path),
        "predictions_jsonl_path": str(predictions_jsonl_path),
        "compared_metrics": compared_metrics,
        "compared_metric_count": compared_count,
        "failed_metric_count": fail_count,
        "worst_metric_delta": worst_metric_delta,
        "framework_summary": framework_summary,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }


def _normalize_model_name(value: object) -> str:
    raw = normalize_name(value)
    if raw.endswith(".pt"):
        raw = raw[:-3]
    # Normalize common aliases to avoid false mismatches.
    alias_map = {
        "yolov8n": "yolo8n",
        "yolov8s": "yolo8s",
        "yolov11n": "yolo11n",
        "yolov11s": "yolo11s",
        "yolo": "yolo",
    }
    return alias_map.get(raw, raw)


def _normalize_run_name(value: object) -> str:
    raw = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9_-]+", "-", raw).strip("-")


def normalize_run_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    attack = metadata.get("attack", "none")
    defense = metadata.get("defense", "none")
    normalized_attack = "none" if is_none_like(attack) else normalize_name(attack)
    normalized_defense = "none" if is_none_like(defense) else normalize_name(defense)
    return {
        "run_name": _normalize_run_name(metadata.get("run_name", "")),
        "model": _normalize_model_name(metadata.get("model", "")),
        "attack": normalized_attack,
        "defense": normalized_defense,
        "seed": _to_int(metadata.get("seed", 0), default=0),
    }


def enforce_validation_gate(
    *,
    attack_name: str,
    legacy_row: Mapping[str, Any],
    framework_metrics: Mapping[str, Any],
    gate_config: ValidationGateConfig,
) -> list[str]:
    attack_norm = "none" if is_none_like(attack_name) else normalize_name(attack_name)
    if attack_norm not in gate_config.required_attacks:
        return []

    errors: list[str] = []
    # Legacy metrics presence check.
    for key in VALIDATION_METRIC_KEYS:
        if to_optional_float(legacy_row.get(key)) is None:
            errors.append(f"legacy missing required validation metric: {key}")

    # Framework validation status/metric check.
    validation = framework_metrics.get("validation", {})
    if not isinstance(validation, Mapping):
        errors.append("framework validation payload missing or invalid")
        return errors

    enabled = bool(validation.get("enabled", False))
    status = normalize_name(validation.get("status", "missing"))
    if not enabled:
        errors.append("framework validation.enabled=false for validation-required attack")
    if status not in {"complete"}:
        errors.append(f"framework validation.status must be 'complete', got '{status or 'missing'}'")
    for key in VALIDATION_METRIC_KEYS:
        if to_optional_float(validation.get(key)) is None:
            errors.append(f"framework missing required validation metric: {key}")
    return errors


def compare_shadow_runs(
    legacy: Mapping[str, Any],
    framework: Mapping[str, Any],
    *,
    max_detection_relative_delta_pct: float = DEFAULT_MAX_DETECTION_DELTA_PCT,
    max_conf_relative_delta_pct: float = DEFAULT_MAX_CONFIDENCE_DELTA_PCT,
) -> dict[str, Any]:
    legacy_meta = normalize_run_metadata(legacy.get("metadata", {}))
    framework_meta = normalize_run_metadata(framework.get("metadata", {}))

    metadata_mismatches = []
    for key in ("run_name", "model", "attack", "defense", "seed"):
        if legacy_meta.get(key) != framework_meta.get(key):
            metadata_mismatches.append(
                {
                    "field": key,
                    "legacy": legacy_meta.get(key),
                    "framework": framework_meta.get(key),
                }
            )

    legacy_predictions = legacy.get("predictions", {})
    framework_predictions = framework.get("predictions", {})
    legacy_validation = legacy.get("validation", {})
    framework_validation = framework.get("validation", {})

    detection_entries = [
        metric_delta_entry(
            key,
            to_optional_float(legacy_predictions.get(key)),
            to_optional_float(framework_predictions.get(key)),
        )
        for key in PREDICTION_DETECTION_METRIC_KEYS
    ]
    confidence_entries = [
        metric_delta_entry(
            key,
            to_optional_float(legacy_predictions.get(key)),
            to_optional_float(framework_predictions.get(key)),
        )
        for key in PREDICTION_CONFIDENCE_METRIC_KEYS
    ]
    validation_entries = [
        metric_delta_entry(
            key,
            to_optional_float(legacy_validation.get(key)),
            to_optional_float(framework_validation.get(key)),
        )
        for key in VALIDATION_METRIC_KEYS
    ]

    detection_compared = sum(1 for entry in detection_entries if entry.get("relative_delta_pct") is not None)
    detection_passes = sum(
        1
        for entry in detection_entries
        if entry.get("relative_delta_pct") is not None
        and delta_entry_within_threshold(entry, max_detection_relative_delta_pct)
    )
    confidence_compared = sum(1 for entry in confidence_entries if entry.get("relative_delta_pct") is not None)
    confidence_passes = sum(
        1
        for entry in confidence_entries
        if entry.get("relative_delta_pct") is not None
        and delta_entry_within_threshold(entry, max_conf_relative_delta_pct)
    )
    validation_compared = sum(1 for entry in validation_entries if entry.get("relative_delta_pct") is not None)
    validation_passes = sum(
        1
        for entry in validation_entries
        if delta_entry_within_threshold(entry, max_detection_relative_delta_pct)
    )

    total_checks = detection_compared + confidence_compared + validation_compared + 1
    total_passes = detection_passes + confidence_passes + validation_passes + (1 if not metadata_mismatches else 0)
    parity_score = round((total_passes / total_checks) * 100.0, 2) if total_checks else 0.0

    parity_pass = (
        not metadata_mismatches
        and detection_passes == detection_compared
        and confidence_passes == confidence_compared
        and (validation_passes == validation_compared)
    )

    detection_worst = worst_relative_delta_pct(detection_entries)
    confidence_worst = worst_relative_delta_pct(confidence_entries)

    return {
        "parity_pass": parity_pass,
        "parity_score": parity_score,
        "metadata_mismatches": metadata_mismatches,
        "deltas": {
            "detection": detection_entries,
            "confidence": confidence_entries,
            "validation": validation_entries,
        },
        "delta_summary": {
            "detection_worst_relative_pct": detection_worst,
            "confidence_worst_relative_pct": confidence_worst,
        },
        "thresholds": {
            "max_detection_relative_delta_pct": max_detection_relative_delta_pct,
            "max_conf_relative_delta_pct": max_conf_relative_delta_pct,
        },
    }


def read_last_legacy_row(metrics_csv: Path) -> dict[str, Any]:
    with metrics_csv.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows found in legacy metrics CSV: {metrics_csv}")
    return rows[-1]


def read_framework_metrics(run_dir: Path) -> dict[str, Any]:
    metrics_path = run_dir / "metrics.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid framework metrics payload in {metrics_path}")
    return payload


def build_shadow_artifacts(
    *,
    legacy_row: Mapping[str, Any],
    framework_metrics: Mapping[str, Any],
    framework_run_summary: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    legacy_artifact = build_legacy_shadow_artifact(legacy_row)
    framework_artifact = build_framework_shadow_artifact(
        framework_metrics=framework_metrics,
        framework_run_summary=framework_run_summary,
    )
    return legacy_artifact, framework_artifact
