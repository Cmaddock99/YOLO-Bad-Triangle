"""Stable aggregate-reporting namespace for new code."""

from .dashboard import generate_dashboard
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

__all__ = [
    "generate_dashboard",
    "build_auto_summary_payload",
    "render_auto_summary_markdown",
    "write_auto_summary",
    "evaluate_warnings",
    "WARN_NO_BASELINE",
    "WARN_MULTIPLE_BASELINES",
    "WARN_NO_VALIDATION",
    "WARN_LOW_ATTACK_COUNT",
    "WARN_LOW_CONFIDENCE_FLOOR",
    "WARN_HIGH_CONFIDENCE_FLOOR",
    "WARN_DEFENSE_RECOVERY_UNDEFINED",
    "WARN_DEFENSE_DEGRADES_PERFORMANCE",
    "WARN_ATTACK_BELOW_NOISE",
    "WARN_MISSING_PER_CLASS",
]
