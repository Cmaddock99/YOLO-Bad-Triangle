from __future__ import annotations

from types import MappingProxyType

# Canonical schema IDs
SCHEMA_ID_FRAMEWORK_METRICS = "framework_metrics/v1"
SCHEMA_ID_FRAMEWORK_RUN_SUMMARY = "framework_run_summary/v1"
SCHEMA_ID_LEGACY_COMPAT_CSV = "legacy_compat_csv/v1"
SCHEMA_ID_CYCLE_SUMMARY = "cycle_summary/v1"
SCHEMA_ID_WARNINGS = "warnings/v1"
SCHEMA_ID_HEADLINE_METRICS_CSV = "headline_metrics_csv/v1"
SCHEMA_ID_PER_CLASS_VULNERABILITY_CSV = "per_class_vulnerability_csv/v1"
SCHEMA_ID_SYSTEM_HEALTH_SUMMARY = "system_health_summary/v1"
SCHEMA_ID_DEMO_MANIFEST = "demo_manifest/v1"

SCHEMA_IDS = MappingProxyType(
    {
        "framework_metrics": SCHEMA_ID_FRAMEWORK_METRICS,
        "framework_run_summary": SCHEMA_ID_FRAMEWORK_RUN_SUMMARY,
        "legacy_compat_csv": SCHEMA_ID_LEGACY_COMPAT_CSV,
        "cycle_summary": SCHEMA_ID_CYCLE_SUMMARY,
        "warnings": SCHEMA_ID_WARNINGS,
        "headline_metrics_csv": SCHEMA_ID_HEADLINE_METRICS_CSV,
        "per_class_vulnerability_csv": SCHEMA_ID_PER_CLASS_VULNERABILITY_CSV,
        "system_health_summary": SCHEMA_ID_SYSTEM_HEALTH_SUMMARY,
        "demo_manifest": SCHEMA_ID_DEMO_MANIFEST,
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

# Canonical pipeline semantics markers and transform orders.
PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE = "attack_then_defense"
PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK = "defense_then_attack"
PIPELINE_SEMANTIC_LEGACY_UNKNOWN = "legacy_unknown"
CURRENT_PIPELINE_TRANSFORM_ORDER = (
    "attack.apply",
    "defense.preprocess",
    "model.predict",
    "defense.postprocess",
)
LEGACY_PIPELINE_TRANSFORM_ORDER = (
    "defense.preprocess",
    "attack.apply",
    "model.predict",
    "defense.postprocess",
)

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

# Reporting context metadata written into run_summary.json when present.
REPORTING_RUN_ROLE_BASELINE = "baseline"
REPORTING_RUN_ROLE_ATTACK_ONLY = "attack_only"
REPORTING_RUN_ROLE_DEFENDED = "defended"
REPORTING_RUN_ROLE_TUNE = "tune"
REPORTING_RUN_ROLE_CONSISTENCY = "consistency"
REPORTING_RUN_ROLES = (
    REPORTING_RUN_ROLE_BASELINE,
    REPORTING_RUN_ROLE_ATTACK_ONLY,
    REPORTING_RUN_ROLE_DEFENDED,
    REPORTING_RUN_ROLE_TUNE,
    REPORTING_RUN_ROLE_CONSISTENCY,
)

REPORTING_DATASET_SCOPE_SMOKE = "smoke"
REPORTING_DATASET_SCOPE_TUNE = "tune"
REPORTING_DATASET_SCOPE_FULL = "full"
REPORTING_DATASET_SCOPES = (
    REPORTING_DATASET_SCOPE_SMOKE,
    REPORTING_DATASET_SCOPE_TUNE,
    REPORTING_DATASET_SCOPE_FULL,
)

REPORTING_AUTHORITY_DIAGNOSTIC = "diagnostic"
REPORTING_AUTHORITY_AUTHORITATIVE = "authoritative"
REPORTING_AUTHORITIES = (
    REPORTING_AUTHORITY_DIAGNOSTIC,
    REPORTING_AUTHORITY_AUTHORITATIVE,
)

REPORTING_SOURCE_PHASE_1 = "phase1"
REPORTING_SOURCE_PHASE_2 = "phase2"
REPORTING_SOURCE_PHASE_3 = "phase3"
REPORTING_SOURCE_PHASE_4 = "phase4"
REPORTING_SOURCE_PHASE_MANUAL = "manual"
REPORTING_SOURCE_PHASES = (
    REPORTING_SOURCE_PHASE_1,
    REPORTING_SOURCE_PHASE_2,
    REPORTING_SOURCE_PHASE_3,
    REPORTING_SOURCE_PHASE_4,
    REPORTING_SOURCE_PHASE_MANUAL,
)

REPORTING_CONTEXT_KEYS = (
    "run_role",
    "dataset_scope",
    "authority",
    "source_phase",
)
