# CLAUDE.md

Shared project guidance for YOLO-Bad-Triangle skills and code changes.

## Mission and framework-first orientation

- This repo is framework-first: use existing runner/registry/reporting paths instead of parallel systems.
- Canonical execution entrypoints are `scripts/run_unified.py` and `scripts/sweep_and_report.py`.
- Core orchestration is `src/lab/runners/run_experiment.py`.

## Canonical artifact paths

- Single-run artifacts: `outputs/framework_runs/<run_name>/`
- Sweep/report artifacts: `outputs/framework_reports/<sweep_id>/`
- Required run outputs:
  - `metrics.json`
  - `predictions.jsonl`
  - `run_summary.json`

## Artifact and provenance expectations

- Treat required run outputs as the minimum contract before analysis or reporting.
- Keep schema/contract references aligned with:
  - `schemas/v1/`
  - `src/lab/config/contracts.py`
  - `scripts/ci/validate_outputs.py`
- Preserve run naming as `<model>__<attack>__<defense>` for matrix-style comparisons.
- If a provenance field or optional artifact is missing, report uncertainty explicitly; do not guess.

## Comparability and parity rules

- Do not compare runs unless baseline/eval scope are like-for-like enough to support the claim.
- Surface comparability blockers explicitly (for example missing pairs or count mismatches).
- For parity work, return `inconclusive` when comparability prerequisites fail.
- Do not infer root cause without evidence from artifacts.

## Planning and reporting rules

- Planning outputs must be evidence-gated and budget-aware.
- Do not recommend non-comparable experiments as reliable next steps.
- Reporting outputs must stay deterministic and machine-parseable where a schema is defined.
- If evidence is partial, downgrade status rather than filling gaps with assumptions.

## Skills & analysis conventions

### Checkpoint facts (current as of 2026-03-30)

- `dpc_unet_final_golden.pt` — production baseline. Active via `DPC_UNET_CHECKPOINT_PATH` in `.env`.
- `dpc_unet_adversarial_finetuned.pt` — adversarially finetuned checkpoint. Status: **CONDITIONAL PASS**.
  - A/B eval (deepfool eps=0.1): finetuned +0.006 mAP50 (marginal)
  - A/B eval (square eps=0.3): finetuned +0.027 mAP50 (meaningful)
  - Clean (no-attack) A/B: **NOT YET RUN** — do not declare deployment readiness until this completes.

### Canonical paths for skills

- Cycle history: `outputs/cycle_history/<cycle_id>.json` (newest = latest cycle)
- Cycle state: `outputs/cycle_state.json`
- A/B eval artifacts: `outputs/eval_ab_*.json` (may not exist)
- Framework reports: `outputs/framework_reports/<sweep_id>/`

### mAP50 source rule

Use Phase 4 `validate_*` rows from `cycle_history/<cycle_id>.json` as the authoritative source for mAP50. Phase 1/2 smoke runs use detection confidence metrics and are not comparable to Phase 4 full-dataset mAP50 values.

### auto_summary false-positive warning

`generate_auto_summary.py` may emit false-positive `NO_VALIDATION` and `DEFENSE_DEGRADES_PERFORMANCE` warnings. Root cause: Phase 1 smoke runs are processed before Phase 4 `validate_*` rows and may shadow them. Do not propagate these warnings without verifying that the source row in `validation_results` is from Phase 4.

### Evidence integrity rule

Do not infer missing evidence. If a metric, file, or result is absent, record it as unknown or missing explicitly — do not fill the gap with assumptions or interpolation.

## Maintenance guidance for skills

- Keep project-wide rules in this file; keep each skill task-specific.
- Use `.claude/skills/<skill-name>/SKILL.md` with support files (`reference.md`, `examples/`).
- Use least-privilege `allowed-tools` and set `disable-model-invocation: true` for manual-only strategic skills.
- Prefer `context: fork` for isolated planner/judge workflows.
- Keep `SKILL.md` concise; place detailed examples and contracts in support files.
