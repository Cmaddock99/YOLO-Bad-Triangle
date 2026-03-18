# ULTIMATE_CURSOR_PROMPT.md

You are a senior ML security engineer and adversarial research architect working on this exact repository:

- `run_experiment.py`
- `run_experiment_api.py`
- `scripts/run_framework.py`
- `src/lab/runners/experiment_runner.py`
- `src/lab/runners/run_experiment.py`
- `src/lab/attacks/*`
- `src/lab/defenses/*`
- `src/lab/models/*`
- `src/lab/eval/*`

Your task is to refactor this repo into a modular adversarial ML framework **without breaking current working behavior**.

## Critical Operating Mode: Non-Destructive Migration

Mandatory rules:

1. Do not delete, move, or rewrite legacy working paths first.
2. Keep these legacy operator paths intact until parity gates pass:
   - `run_experiment.py`
   - `scripts/run_framework.py` + `src/lab/runners/cli.py`
   - `scripts/run_week1_stabilization.sh`
   - `scripts/demo/run_demo_package.sh`
3. Add framework logic alongside current code under `src/lab/`.
4. Prefer wrappers/adapters over rewrites.
5. Parity before elegance.

## Repository Facts You Must Respect

1. There are two active execution stacks:
   - Legacy: `ExperimentRunner` in `src/lab/runners/experiment_runner.py` with global CSV metrics (`src/lab/eval/metrics.py`).
   - Framework: `UnifiedExperimentRunner` in `src/lab/runners/run_experiment.py` with per-run JSON artifacts.
2. Config schemas are currently split:
   - Legacy alias/matrix schema: `configs/experiment_lab.yaml`, `configs/modular_experiments.yaml`, `configs/week1_stabilization_*.yaml`.
   - Framework schema: `configs/lab_framework_phase5.yaml`.
3. YOLO loading currently comes from:
   - `src/lab/models/yolo_model.py` (legacy wrapper)
   - `src/lab/models/yolo_adapter.py` (framework adapter).
4. Metrics reliability is a known focus area:
   - legacy partial/missing metrics handled by warnings/status columns
   - framework path sanitizes non-finite values via `src/lab/eval/framework_metrics.py`.

## Required End State

Implement a modular, config-driven adversarial ML framework with:

- `BaseModel`
- `BaseAttack`
- `BaseDefense`
- one canonical runner interface
- model/attack/defense registries
- reliable metric capture
- standardized output artifacts
- support for:
  - baseline
  - blur
  - FGSM
  - PGD
  - DeepFool (with explicit limitations if needed)

## Mandatory Interface Contracts

1. `BaseModel`
   - `load()`
   - `predict(images, **kwargs)`
   - `validate(dataset, **kwargs)`
2. `BaseAttack`
   - `apply(image, model=None, **kwargs) -> (perturbed_image, metadata)`
3. `BaseDefense`
   - `preprocess(image, **kwargs) -> (image, metadata)`
   - `postprocess(predictions, **kwargs) -> (predictions, metadata)`
4. Prediction schema must normalize to:
   - `image_id`
   - `boxes`
   - `scores`
   - `class_ids`
   - `metadata`

Do not expose raw Ultralytics result objects outside model adapter boundaries.

## Required Output Standard

For each framework run, produce:

- `resolved_config.yaml`
- `predictions.jsonl`
- `metrics.json`
- `run_summary.json`
- optional transformed/prepared images directory

Preserve legacy outputs simultaneously:

- `metrics_summary.csv`
- `experiment_table.md`
- existing week1/demo plot artifact names

## Execution Plan (Implement In Phases)

### Phase A — Stabilize runner unification surface

1. Keep `src/lab/runners/run_experiment.py` as framework runner core.
2. Add compatibility wrappers so legacy CLIs can route to framework mode safely when explicitly enabled (do not switch default yet).
3. Document exact command-to-schema compatibility.

### Phase B — Attack plugin expansion (framework path)

1. Add framework attack plugins for:
   - FGSM (wrapping/adapting logic from `src/lab/attacks/fgsm.py`)
   - PGD (from `src/lab/attacks/pgd.py`)
   - DeepFool (from `src/lab/attacks/deepfool.py`)
2. Keep blur plugin behavior stable from `src/lab/attacks/blur_adapter.py`.
3. Explicitly document limitations where detector-gradient assumptions are unstable.

### Phase C — Defense plugin expansion

1. Add at least:
   - preprocessing defense plugin
   - confidence-threshold postprocess defense plugin
2. Keep current none/identity adapter behavior unchanged.

### Phase D — Metrics hardening

1. Keep framework `metrics.json` as canonical structured artifact.
2. Enforce finite-or-null semantics on all numeric metric fields.
3. Surface validation state explicitly (`missing|partial|complete|error`) in summaries and CLI output.
4. Ensure attack/defense deltas can be computed from run outputs.

### Phase E — Comparison/reporting

1. Add framework-native comparison utilities under `src/lab/reporting/`.
2. Generate:
   - CSV summary
   - markdown report
   - optional plots
3. Do not break existing week1 plotting scripts while introducing this.

## Validation Gates (Do Not Skip)

Before any default-path switch:

1. Legacy baseline run still passes.
2. Framework baseline run passes on same dataset/model/conf.
3. Detection counts and key metrics are within accepted delta.
4. Framework outputs are complete (`predictions.jsonl`, `metrics.json`, `run_summary.json`, `resolved_config.yaml`).
5. Week1 demo package still works unchanged.

## Implementation Constraints

- Use existing files and symbols where possible; do not invent parallel abstractions unnecessarily.
- Prefer additive changes in:
  - `src/lab/models/`
  - `src/lab/attacks/`
  - `src/lab/defenses/`
  - `src/lab/runners/`
  - `src/lab/eval/`
  - `src/lab/reporting/`
- Keep docs updated when behavior changes:
  - `docs/TEAM_GUIDE.md`
  - `docs/WEEK1_DEMO_RUNBOOK.md`
  - `MIGRATION_PLAN.md`

## Final Deliverables Required From The Refactor

1. Final file-level old->new mapping.
2. List of all modified/new files.
3. Commands for:
   - baseline
   - blur
   - FGSM
   - PGD
   - DeepFool
   - defense-enabled runs
4. Clear notes on limitations and fallback behavior.
5. Explicit statement of what remains legacy-compatible.
