from __future__ import annotations

from types import MappingProxyType

# Canonical schema IDs
SCHEMA_ID_FRAMEWORK_METRICS = "framework_metrics/v1"
SCHEMA_ID_FRAMEWORK_RUN_SUMMARY = "framework_run_summary/v1"
SCHEMA_ID_LEGACY_COMPAT_CSV = "legacy_compat_csv/v1"

SCHEMA_IDS = MappingProxyType(
    {
        "framework_metrics": SCHEMA_ID_FRAMEWORK_METRICS,
        "framework_run_summary": SCHEMA_ID_FRAMEWORK_RUN_SUMMARY,
        "legacy_compat_csv": SCHEMA_ID_LEGACY_COMPAT_CSV,
    }
)

# NOTE: framework_metrics.py writes per_class keys as str(int) — e.g. "0", "42".
# All readers must cast: int(k) for numeric use or keep as str for JSON passthrough.
# Do NOT change the writer — existing metrics.json files on disk use str keys.

# Backward-compatible names used by existing callers.
FRAMEWORK_METRICS_SCHEMA_VERSION = SCHEMA_ID_FRAMEWORK_METRICS
FRAMEWORK_RUN_SUMMARY_SCHEMA_VERSION = SCHEMA_ID_FRAMEWORK_RUN_SUMMARY
LEGACY_COMPAT_CSV_SCHEMA_VERSION = SCHEMA_ID_LEGACY_COMPAT_CSV

# Canonical runtime entrypoint.
CANONICAL_RUNTIME_ENTRYPOINT = "scripts/run_unified.py"
CANONICAL_RUNTIME_COMMANDS = ("run-one", "sweep")

# Toggle dotted keys used in run configs.
TOGGLE_VALIDATION_ENABLED = "validation.enabled"
TOGGLE_SUMMARY_ENABLED = "summary.enabled"

# Global governance guardrails.
MAX_FIX_LOOP = 5

# Image pixel range constant (8-bit unsigned integer images).
PIXEL_MAX: float = 255.0

# Semantic attack objective modes.
ATTACK_OBJECTIVE_UNTARGETED = "untargeted_conf_suppression"
ATTACK_OBJECTIVE_TARGET_CLASS = "target_class_misclassification"
ATTACK_OBJECTIVE_CLASS_HIDE = "class_conditional_hiding"
ATTACK_OBJECTIVE_MODES = (
    ATTACK_OBJECTIVE_UNTARGETED,
    ATTACK_OBJECTIVE_TARGET_CLASS,
    ATTACK_OBJECTIVE_CLASS_HIDE,
)

