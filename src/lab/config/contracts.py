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
)

# Toggle dotted keys used in run configs.
TOGGLE_VALIDATION_ENABLED = "validation.enabled"
TOGGLE_SUMMARY_ENABLED = "summary.enabled"

# Global governance guardrails.
MAX_FIX_LOOP = 5

# Image pixel range constant (8-bit unsigned integer images).
PIXEL_MAX: float = 255.0

# Legacy-compat inference defaults.
# These apply ONLY to the legacy compat path (ExperimentRunner).
# The framework path (UnifiedExperimentRunner) reads conf/iou/imgsz
# from the YAML config's `predict:` section (default: conf=0.5 in configs/default.yaml).
LEGACY_CONF_DEFAULT = 0.25
LEGACY_IOU_DEFAULT = 0.7
LEGACY_IMGSZ_DEFAULT = 640

# Backward-compatible names used by existing callers.
DEFAULT_CONF = LEGACY_CONF_DEFAULT
DEFAULT_IOU = LEGACY_IOU_DEFAULT
DEFAULT_IMGSZ = LEGACY_IMGSZ_DEFAULT

# Default confidence threshold used when running a legacy conf sweep (distinct from
# LEGACY_CONF_DEFAULT which is the per-run YOLO inference threshold).
LEGACY_SWEEP_CONF_DEFAULT: float = 0.5
