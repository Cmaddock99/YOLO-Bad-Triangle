from __future__ import annotations


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
    return _safe_ratio(float(defense_detections) - float(attack_detections), baseline_detections)


def compute_confidence_drop(
    baseline_avg_conf: float | int | None,
    attack_avg_conf: float | int | None,
) -> float | None:
    if baseline_avg_conf is None or attack_avg_conf is None:
        return None
    return _safe_ratio(float(baseline_avg_conf) - float(attack_avg_conf), baseline_avg_conf)
