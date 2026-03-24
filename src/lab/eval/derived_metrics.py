from __future__ import annotations

import math
from typing import Any


def to_finite_float(value: Any) -> float | None:
    """Convert value to float, returning None for non-numeric or non-finite inputs."""
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _safe_ratio(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    try:
        num = float(numerator)
        den = float(denominator)
    except (TypeError, ValueError):
        return None
    if den == 0.0:
        return None
    return num / den


def compute_detection_drop(
    baseline_detections: float | int | None,
    attack_detections: float | int | None,
) -> float | None:
    if baseline_detections is None or attack_detections is None:
        return None
    return _safe_ratio(float(baseline_detections) - float(attack_detections), baseline_detections)


def compute_defense_recovery(
    baseline_detections: float | int | None,
    attack_detections: float | int | None,
    defense_detections: float | int | None,
) -> float | None:
    if baseline_detections is None or attack_detections is None or defense_detections is None:
        return None
    if float(baseline_detections) == 0:
        return None  # no baseline detections — recovery undefined
    return _safe_ratio(float(defense_detections) - float(attack_detections), baseline_detections)


def compute_per_class_detection_drop(
    baseline_per_class: dict[int, dict],
    attacked_per_class: dict[int, dict],
) -> dict[int, float | None]:
    """Per-class detection drop fraction: (baseline_count - attack_count) / baseline_count."""
    all_ids = set(baseline_per_class) | set(attacked_per_class)
    result: dict[int, float | None] = {}
    for class_id in all_ids:
        baseline_count = baseline_per_class.get(class_id, {}).get("count")
        attack_count = attacked_per_class.get(class_id, {}).get("count", 0)
        result[class_id] = compute_detection_drop(baseline_count, attack_count)
    return result


def compute_confidence_drop(
    baseline_avg_conf: float | int | None,
    attack_avg_conf: float | int | None,
) -> float | None:
    if baseline_avg_conf is None or attack_avg_conf is None:
        return None
    return _safe_ratio(float(baseline_avg_conf) - float(attack_avg_conf), baseline_avg_conf)
