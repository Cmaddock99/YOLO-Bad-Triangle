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

## Maintenance guidance for skills

- Keep project-wide rules in this file; keep each skill task-specific.
- Use `.claude/skills/<skill-name>/SKILL.md` with support files (`reference.md`, `examples/`).
- Use least-privilege `allowed-tools` and set `disable-model-invocation: true` for manual-only strategic skills.
- Prefer `context: fork` for isolated planner/judge workflows.
- Keep `SKILL.md` concise; place detailed examples and contracts in support files.
