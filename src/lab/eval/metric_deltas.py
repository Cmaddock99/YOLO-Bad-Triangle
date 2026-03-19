from __future__ import annotations

from typing import Any, Mapping


def relative_delta_pct(baseline: float | None, candidate: float | None) -> float | None:
    if baseline is None or candidate is None:
        return None
    if baseline == 0.0:
        return None
    return ((candidate - baseline) / abs(baseline)) * 100.0


def metric_delta_entry(name: str, baseline: float | None, candidate: float | None) -> dict[str, Any]:
    absolute_delta = None
    if baseline is not None and candidate is not None:
        absolute_delta = abs(candidate - baseline)
    return {
        "metric": name,
        "legacy": baseline,
        "framework": candidate,
        "absolute_delta": absolute_delta,
        "relative_delta_pct": relative_delta_pct(baseline, candidate),
    }


def delta_entry_within_threshold(entry: Mapping[str, Any], threshold_pct: float) -> bool:
    relative = entry.get("relative_delta_pct")
    if relative is None:
        # Missing values are explicitly excluded from pass counts.
        return False
    return abs(float(relative)) <= threshold_pct


def worst_relative_delta_pct(entries: list[Mapping[str, Any]]) -> float | None:
    return max(
        (
            abs(float(entry["relative_delta_pct"]))
            for entry in entries
            if entry.get("relative_delta_pct") is not None
        ),
        default=None,
    )
