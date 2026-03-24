from __future__ import annotations

from typing import Any

from lab.eval.derived_metrics import (
    compute_confidence_drop,
    compute_defense_recovery,
    compute_detection_drop,
    to_finite_float,
)


def _extract_total_detections(metrics: dict[str, Any] | None) -> float | None:
    if not isinstance(metrics, dict):
        return None
    predictions = metrics.get("predictions", {})
    if not isinstance(predictions, dict):
        return None
    return to_finite_float(predictions.get("total_detections"))


def _extract_avg_confidence(metrics: dict[str, Any] | None) -> float | None:
    if not isinstance(metrics, dict):
        return None
    predictions = metrics.get("predictions", {})
    if not isinstance(predictions, dict):
        return None
    confidence = predictions.get("confidence", {})
    if not isinstance(confidence, dict):
        return None
    return to_finite_float(confidence.get("mean"))


def _interpretation(detection_drop: float | None, defense_recovery: float | None) -> str:
    if detection_drop is None:
        return "Insufficient data for robustness interpretation"
    if detection_drop < 0.01:
        return "No effect detected (verify metric or params)"
    strong_attack = detection_drop > 0.15
    weak_defense = defense_recovery is not None and defense_recovery < 0.05
    if strong_attack and weak_defense:
        return "Strong attack effect, weak defense"
    if strong_attack:
        return "Strong attack effect"
    if weak_defense:
        return "Weak defense"
    return "Moderate robustness"


def generate_summary(
    baseline_metrics: dict[str, Any] | None,
    attack_metrics: dict[str, Any] | None,
    defense_metrics: dict[str, Any] | None = None,
) -> dict[str, float | str | None]:
    baseline_detections = _extract_total_detections(baseline_metrics)
    attack_detections = _extract_total_detections(attack_metrics)
    defense_detections = _extract_total_detections(defense_metrics)

    baseline_avg_conf = _extract_avg_confidence(baseline_metrics)
    attack_avg_conf = _extract_avg_confidence(attack_metrics)

    detection_drop = compute_detection_drop(baseline_detections, attack_detections)
    defense_recovery = compute_defense_recovery(
        baseline_detections,
        attack_detections,
        defense_detections,
    )
    confidence_drop = compute_confidence_drop(baseline_avg_conf, attack_avg_conf)

    return {
        "attack_effectiveness": detection_drop,
        "defense_recovery": defense_recovery,
        "confidence_drop": confidence_drop,
        "interpretation": _interpretation(detection_drop, defense_recovery),
    }
