# MIGRATION_PLAN.md

## Purpose

This document defines a **non-destructive migration** from the current YOLO-focused experiment stack into a modular adversarial ML lab framework for the BAD Triangle workflow:

1. BUILD
2. ATTACK
3. DEFEND

The migration is wrapper-first and parity-first. Existing working scripts remain available during transition.

## Audit Refresh (Current Repository State)

This plan has been refreshed against the current codebase state (post framework phases 2-6 foundation work):

- Legacy operational path remains active:
  - `run_experiment.py`
  - `run_experiment_api.py`
  - `scripts/run_framework.py` -> `src/lab/runners/cli.py` -> `ExperimentRunner`
  - week1/demo scripts under `scripts/` and `scripts/demo/`
- Additive framework path exists and is runnable:
  - `src/lab/runners/run_experiment.py` (`UnifiedExperimentRunner`)
  - framework interfaces/registries/adapters under `src/lab/{models,attacks,defenses,eval}`
- Metrics now exist in two parallel systems:
  - legacy CSV/table path (`src/lab/eval/metrics.py`)
  - per-run framework JSON path (`metrics.json` via unified runner)

Current migration stance:
- Preserve legacy path as the canonical operator flow until unified parity covers demo and matrix needs.
- Continue wrapper-first migration, not replacement-first migration.

## Non-Destructive Rules (Must Follow)

- Do not delete or move legacy files in early phases.
- Do not replace working scripts before parity validation.
- Add new framework code alongside current code.
- Treat uncertain dependencies as legacy-critical and keep them.
- Stop after each phase for validation before continuing.
- Prefer adapting existing logic over rewriting.

## Current-State Audit (Phase 1 Output)

### Active Runners / Entrypoints

- `run_experiment.py` (key=value CLI)
- `run_experiment_api.py` (argparse wrapper)
- `scripts/run_framework.py` -> `src/lab/runners/cli.py`
- `scripts/run_week1_stabilization.sh` (demo/stress orchestration)
- `scripts/demo/run_demo_package.sh` (packaged preflight/live/artifacts/gates/summary)

Primary execution converges on:

- `src/lab/runners/experiment_runner.py` -> `ExperimentRunner.run()`

### Attack / Defense Plugin Pattern

- Attack interface and registry:
  - `src/lab/attacks/base.py`
  - `src/lab/attacks/registry.py`
- Defense interface and registry:
  - `src/lab/defenses/base.py`
  - `src/lab/defenses/registry.py`

This already supports decorator registration and dynamic discovery.

### Model Loading / Inference

- `src/lab/models/yolo_model.py` (`YOLOModel`)
  - wraps Ultralytics `YOLO(...)`
  - exposes `predict()` and `validate()`

### Metrics and Reporting

- `src/lab/eval/metrics.py` -> `append_run_metrics(...)`
- `src/lab/eval/experiment_table.py` -> markdown table generation
- Current metrics sources:
  - validation metrics from `run_dir/val/metrics.json`
  - confidence and detection stats from YOLO label text files

### Current Output Shape

Common artifacts currently produced:

- `outputs/<run_name>/...`
- `outputs/_intermediates/<run_name>/attacked/...`
- `outputs/_intermediates/<run_name>/defended/...`
- `outputs/metrics_summary.csv`
- `outputs/experiment_table.md`
- week1/demo plot bundles under `outputs/<root>/plots/*`

### Known Risk Points

- Validation metrics may be missing if validation is disabled or metrics file is absent.
- Confidence metrics are omitted if prediction label rows are malformed/non-6-column.
- NaN-like values may pass field-presence checks without strict finiteness validation.

## Old -> New Mapping (Wrapper-First)

| Legacy Area | Current Path | Target Modular Area | Migration Strategy |
|---|---|---|---|
| CLI runner | `run_experiment.py` | `src/lab/runners/run_experiment.py` | Add new runner; keep legacy CLI as compatibility entrypoint |
| YAML batch runner | `scripts/run_framework.py`, `src/lab/runners/cli.py` | `src/lab/runners/` | Reuse resolution logic first, then normalize config schema |
| Core orchestration | `src/lab/runners/experiment_runner.py` | `src/lab/runners/` | Wrap existing flow into standardized pipeline stages |
| Model wrapper | `src/lab/models/yolo_model.py` | `src/lab/models/base_model.py` + adapter | Keep `YOLOModel` and add standardized adapter interface |
| Attack plugins | `src/lab/attacks/*` | `src/lab/attacks/` with `BaseAttack` | Reuse current implementations via adapter/wrapper |
| Defense plugins | `src/lab/defenses/*` | `src/lab/defenses/` with `BaseDefense` | Reuse current implementations via adapter/wrapper |
| Metrics | `src/lab/eval/metrics.py` | `src/lab/eval/` standardized JSON outputs | Keep CSV path; add structured JSON in parallel |
| Reporting | scripts + table/plots | `src/lab/reporting/` | Keep existing scripts; add comparison APIs/utilities |

## File-by-File Mapping (Detailed)

### Entrypoints and runners

- Legacy key=value CLI:
  - old: `run_experiment.py`
  - bridge target: wrapper to unified runner once compatibility mode exists
  - current status: **legacy-active**
- Legacy argparse one-run CLI:
  - old: `run_experiment_api.py`
  - bridge target: compatibility wrapper over unified schema
  - current status: **legacy-active**
- Legacy matrix CLI:
  - old: `scripts/run_framework.py` + `src/lab/runners/cli.py`
  - bridge target: matrix adapter that feeds unified runner config
  - current status: **legacy-active**
- Legacy core runner:
  - old: `src/lab/runners/experiment_runner.py`
  - bridge target: stage decomposition mirrored in unified runner
  - current status: **legacy-active**
- Unified runner:
  - new: `src/lab/runners/run_experiment.py`
  - current status: **additive-active**

### Models

- Legacy model wrapper:
  - `src/lab/models/yolo_model.py`
- New interface + adapter:
  - `src/lab/models/base_model.py`
  - `src/lab/models/yolo_adapter.py`
  - `src/lab/models/registry.py`

### Attacks

- Legacy attack interface/registry:
  - `src/lab/attacks/base.py`
  - `src/lab/attacks/registry.py`
  - existing concrete attacks remain source of truth
- New framework interface/registry:
  - `src/lab/attacks/base_attack.py`
  - `src/lab/attacks/plugin_registry.py`
  - `src/lab/attacks/framework_registry.py`
  - currently wrapped plugin: `src/lab/attacks/blur_adapter.py`

### Defenses

- Legacy defense interface/registry:
  - `src/lab/defenses/base.py`
  - `src/lab/defenses/registry.py`
- New framework interface/registry:
  - `src/lab/defenses/base_defense.py`
  - `src/lab/defenses/plugin_registry.py`
  - `src/lab/defenses/framework_registry.py`
  - currently wrapped plugin: `src/lab/defenses/none_adapter.py`

### Metrics and outputs

- Legacy metrics path:
  - `src/lab/eval/metrics.py`
  - outputs: `metrics_summary.csv`, `experiment_table.md`, run folders/plots
- New structured path:
  - `src/lab/eval/framework_metrics.py`
  - `src/lab/eval/prediction_schema.py`
  - `src/lab/eval/prediction_io.py`
  - outputs: `predictions.jsonl`, `metrics.json`, `run_summary.json`, `resolved_config.yaml`

## Target Additive Structure

New code is added under existing tree (no destructive move in first pass):

```text
src/lab/
  models/
  attacks/
  defenses/
  datasets/
  runners/
  eval/
  reporting/
  utils/

configs/
outputs/
```

Legacy files remain and are marked "legacy-compatible" until parity is signed off.

## Phased Migration Plan and Hold Gates

### Phase 1: Audit + Plan (Current Phase)

Deliverables:
- this `MIGRATION_PLAN.md`
- architecture inventory
- old->new mapping
- parity gate definitions

Hold gate:
- no runtime behavior changes introduced

### Phase 2: Framework Skeleton (Non-Destructive)

Create minimal framework scaffolding only:
- `BaseModel`
- `BaseAttack`
- `BaseDefense`
- empty registries
- placeholder runner

Hold gate:
- no existing command regressions
- all legacy commands still runnable

### Phase 3: Wrap Existing Functionality

Implement wrappers (not rewrites):
- YOLO wrapper integrated into new interfaces
- Blur attack wrapped from current implementation
- output normalization layer added alongside legacy outputs

Hold gate:
- new baseline/blur path runs end-to-end
- legacy path unchanged

### Phase 4: Baseline Parity Validation

Run old vs new baseline and compare:
- prediction counts
- key metrics
- output artifacts

Hold gate:
- parity accepted (or deltas documented and approved)

### Phase 5: Single Runner + Config

Introduce unified runner:
- `src/lab/runners/run_experiment.py`
- config-driven execution with CLI overrides
- support baseline + blur + none-defense first

Hold gate:
- replaces nothing yet
- passes smoke checks against parity scenarios

Status:
- **Implemented as additive path** in `src/lab/runners/run_experiment.py`
- supports baseline + blur + no-defense in framework schema

### Phase 6: Metrics + Output Standardization

Add structured per-run artifacts:
- `resolved_config.yaml`
- `predictions.jsonl`
- `metrics.json`
- `run_summary.json`

Fix missing metric capture paths and ensure:
- precision
- recall
- mAP50
- mAP50-95
- confidence stats

Hold gate:
- structured outputs generated for each run
- legacy CSV path still produced

Status:
- **Partially implemented and validated in framework path**
  - `metrics.json` now includes sanitized validation fields and status.
  - legacy CSV behavior remains unchanged.

### Phase 7: Extend Attacks and Defenses

Incrementally add:
- FGSM
- PGD
- DeepFool (document limitations)
- defense preprocess/postprocess hooks
- confidence filtering

Hold gate:
- no regression in baseline/blur workflows

Execution intent update:
- Implement FGSM, PGD, DeepFool as framework plugins by wrapping/stabilizing current legacy implementations.
- Add explicit limitations notes for detector-gradient attacks where exact formulation is model-output dependent.

### Phase 8: Reporting + Comparison

Add comparison utilities:
- CSV summaries
- markdown report generation
- optional plots

Hold gate:
- baseline/attack/defense comparisons reproducible by command

Execution intent update:
- Keep legacy week1 plotting scripts as compatibility reports.
- Add framework-native comparison utilities under `src/lab/reporting/` before any script replacement.

## Mandatory Interface Contract (Target)

### BaseModel
- `load()`
- `predict(images)`
- `validate(dataset)`

### BaseAttack
- `apply(image, model=None)` -> perturbed image + metadata

### BaseDefense
- `preprocess(image)`
- `postprocess(predictions)`

### Prediction Schema

Standardized payload consumed by all downstream stages:
- `image_id`
- `boxes`
- `scores`
- `class_ids`
- `metadata`

No direct raw Ultralytics objects outside model adapter boundaries.

## Parity and Validation Gates

Before moving beyond wrapping:

1. Legacy baseline run succeeds.
2. New-framework baseline run succeeds.
3. Prediction count deltas are within agreed tolerance.
4. Metric deltas (precision/recall/mAP) are reviewed and accepted.
5. Output artifact set exists for both old and new flows.

Additional explicit parity checkpoints:

6. Legacy week1 command sequence (`scripts/run_week1_stabilization.sh`) remains functionally unchanged.
7. Demo package actions (`scripts/demo/run_demo_package.sh`) continue to produce expected artifact names.
8. Framework runner emits valid `validation.status` and finite-or-null metrics semantics for every run.

## Risk Register and Mitigation

- **Risk: hidden dependency on legacy scripts**  
  Mitigation: keep scripts intact; add wrappers instead of move/delete.
- **Risk: missing/partial metrics**  
  Mitigation: standardized metric extraction path + explicit null/failure reasons.
- **Risk: gradient attack instability on detector internals**  
  Mitigation: wrapper with documented constraints and fallback modes.
- **Risk: output drift across runners**  
  Mitigation: run-by-run parity checks and schema validation tests.

## Rollback Strategy

- Keep legacy entrypoints untouched during phases 2-6.
- New framework remains opt-in until parity passes.
- If regression appears, route users to legacy commands immediately.
- Merge phases independently to isolate failures.

## Definition of Done for Migration

Migration is considered complete when:

1. New runner reproduces accepted baseline behavior.
2. Attack/defense plugin additions require minimal boilerplate (file + registry + config).
3. Structured outputs are generated consistently.
4. Comparison/reporting pipeline is reproducible.
5. Legacy path can be deprecated safely (not before parity sign-off).

Operational deprecation prerequisites:

6. A single canonical CLI command can run baseline/blur/FGSM/PGD/DeepFool plus defense toggles using one stable schema.
7. Week1/demo package scripts are either safely re-pointed to unified runner or explicitly retained as legacy wrappers with no behavior drift.

