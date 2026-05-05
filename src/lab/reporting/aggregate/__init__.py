"""Stable aggregate-reporting namespace for new code."""

from ..auto_summary import (
    build_auto_summary_payload,
    render_auto_summary_markdown,
    write_auto_summary,
)
from ..warnings import (
    WARN_ATTACK_BELOW_NOISE,
    WARN_DEFENSE_DEGRADES_PERFORMANCE,
    WARN_DEFENSE_RECOVERY_UNDEFINED,
    WARN_HIGH_CONFIDENCE_FLOOR,
    WARN_LOW_ATTACK_COUNT,
    WARN_LOW_CONFIDENCE_FLOOR,
    WARN_MISSING_PER_CLASS,
    WARN_MULTIPLE_BASELINES,
    WARN_NO_BASELINE,
    WARN_NO_VALIDATION,
    evaluate_warnings,
)
from .dashboard import generate_dashboard

__all__ = [
    "WARN_ATTACK_BELOW_NOISE",
    "WARN_DEFENSE_DEGRADES_PERFORMANCE",
    "WARN_DEFENSE_RECOVERY_UNDEFINED",
    "WARN_HIGH_CONFIDENCE_FLOOR",
    "WARN_LOW_ATTACK_COUNT",
    "WARN_LOW_CONFIDENCE_FLOOR",
    "WARN_MISSING_PER_CLASS",
    "WARN_MULTIPLE_BASELINES",
    "WARN_NO_BASELINE",
    "WARN_NO_VALIDATION",
    "build_auto_summary_payload",
    "evaluate_warnings",
    "generate_dashboard",
    "render_auto_summary_markdown",
    "write_auto_summary",
]
