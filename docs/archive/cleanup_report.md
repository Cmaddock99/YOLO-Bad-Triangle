# Cleanup Report

## Deleted in this pass (safe)

- `scripts/run.py`
  - Reason: shell-script content stored in a `.py` file, no references in code/docs/tests, and functionally superseded by `scripts/run_unified.py` + `scripts/sweep_and_report.py`.
  - Risk: low.

## Scope dependency cleanup check (`src/lab/config/*`)

- High-confidence dead code removal in this scope: none.
  - Reason: `src/lab/config/contracts.py` constants are actively imported by migration and runner paths; `src/lab/config/__init__.py` is retained as the package export surface.
  - Action: no code deletion performed for config scope.

## Deprecated but retained

- `run_experiment_api.py`
  - Status: retained for compatibility, deduplicated scalar parsing, and now emits canonical entrypoint guidance.
  - Suggested future action: retire after consumers migrate to `scripts/run_unified.py`.

- `run_experiment.py`
  - Status: retained wrapper; now routes framework-first usage to `scripts/run_unified.py run-one`.
  - Suggested future action: keep as compatibility shim only.

- `scripts/run_framework.py`
  - Status: retained wrapper; now routes framework-first mode to `scripts/run_unified.py sweep`.
  - Suggested future action: keep only until external automation is migrated.

- `configs/lab_framework_phase3_compat.yaml`
  - Status: retained compatibility config; partially stale against current unified runner expectations.
  - Suggested future action: retire once no longer required by rollback/legacy migration tests.

- `configs/lab_framework_skeleton.yaml`
  - Status: retained scaffold reference for phased migration history.
  - Suggested future action: archive or retire after docs/tests no longer reference scaffold flows.

## Potential follow-up cleanup candidates

- `src/lab/migration/diagnostics.py`
  - Confidence: medium.
  - Note: exported and likely intended for operational flows; no removal made in this pass.

- one-off verification scripts in `scripts/verify_wrapper_*.py`
  - Confidence: medium.
  - Note: remove only after auditing downstream docs or ad-hoc operator usage.

## Stale reference cleanup suggested

- Documentation references to removed or non-existent historical files should be pruned in a docs-only pass to reduce operator confusion.
