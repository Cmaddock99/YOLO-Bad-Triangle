from __future__ import annotations

from typing import Any, Mapping


VALIDATION_METRIC_KEYS = ("precision", "recall", "mAP50", "mAP50-95")
PREDICTION_DETECTION_METRIC_KEYS = ("images_with_detections", "total_detections")
PREDICTION_CONFIDENCE_METRIC_KEYS = ("avg_conf", "median_conf", "p25_conf", "p75_conf")


def to_optional_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def legacy_row_status(
    *,
    validation_status: str,
    metric_values: dict[str, float | None],
) -> tuple[str, str]:
    missing = [name for name, value in metric_values.items() if value is None]
    if missing:
        return "partial", ",".join(missing)
    if validation_status.lower() not in {"ok", "enabled"}:
        return "partial", ""
    return "ok", ""


def prediction_confidence_quantiles(
    metrics: Mapping[str, Any],
) -> tuple[float | None, float | None, float | None]:
    predictions = metrics.get("predictions", {})
    if not isinstance(predictions, Mapping):
        predictions = {}
    confidence = predictions.get("confidence", {})
    if not isinstance(confidence, Mapping):
        confidence = {}
    return (
        to_optional_float(confidence.get("median")),
        to_optional_float(confidence.get("p25")),
        to_optional_float(confidence.get("p75")),
    )
