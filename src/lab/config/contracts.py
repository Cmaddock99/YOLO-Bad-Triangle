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

# Backward-compatible names used by existing callers.
FRAMEWORK_METRICS_SCHEMA_VERSION = SCHEMA_ID_FRAMEWORK_METRICS
FRAMEWORK_RUN_SUMMARY_SCHEMA_VERSION = SCHEMA_ID_FRAMEWORK_RUN_SUMMARY
LEGACY_COMPAT_CSV_SCHEMA_VERSION = SCHEMA_ID_LEGACY_COMPAT_CSV

# Canonical runtime entrypoint and compatibility wrappers.
CANONICAL_RUNTIME_ENTRYPOINT = "scripts/run_unified.py"
CANONICAL_RUNTIME_COMMANDS = ("run-one", "sweep")
COMPAT_WRAPPER_ENTRYPOINTS = (
    "run_experiment.py",
    "run_experiment_api.py",
    "scripts/run_framework.py",
)

# Toggle paths in run configs. These dotted keys are documentation/runtime anchors.
TOGGLE_VALIDATION_ENABLED = "validation.enabled"
TOGGLE_PARITY_ENABLED = "parity.enabled"
TOGGLE_PARITY_FAIL_ON_MISMATCH = "parity.fail_on_mismatch"
TOGGLE_SUMMARY_ENABLED = "summary.enabled"
TOGGLE_USE_LEGACY_RUNTIME = "migration.use_legacy_runtime"

# Shared threshold defaults/keys used across migration and parity checks.
PARITY_THRESHOLD_KEY_DETECTION = "max_detection_relative_delta_pct"
PARITY_THRESHOLD_KEY_CONFIDENCE = "max_conf_relative_delta_pct"
PARITY_THRESHOLD_KEYS = (
    PARITY_THRESHOLD_KEY_DETECTION,
    PARITY_THRESHOLD_KEY_CONFIDENCE,
)
PARITY_MAX_DETECTION_DELTA_PCT_DEFAULT = 5.0
PARITY_MAX_CONFIDENCE_DELTA_PCT_DEFAULT = 5.0

# Backward-compatible names used by existing callers.
DEFAULT_MAX_DETECTION_DELTA_PCT = PARITY_MAX_DETECTION_DELTA_PCT_DEFAULT
DEFAULT_MAX_CONFIDENCE_DELTA_PCT = PARITY_MAX_CONFIDENCE_DELTA_PCT_DEFAULT

# Global governance guardrails.
MAX_FIX_LOOP = 5

# Legacy-compat inference defaults.
LEGACY_CONF_DEFAULT = 0.25
LEGACY_IOU_DEFAULT = 0.7
LEGACY_IMGSZ_DEFAULT = 640

# Backward-compatible names used by existing callers.
DEFAULT_CONF = LEGACY_CONF_DEFAULT
DEFAULT_IOU = LEGACY_IOU_DEFAULT
DEFAULT_IMGSZ = LEGACY_IMGSZ_DEFAULT
