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
- In `run_summary.json`, `provenance.checkpoint_fingerprint_*` identifies the primary model artifact only.
- For checkpointed defenses such as `c_dog`, read defense model identity from `provenance.defense_checkpoints`, not from `defense.params` or the primary model fingerprint fields.
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
- Do not infer deployment readiness from attacked-only A/B results. Clean (no-attack) baseline A/B must be confirmed before a deployment decision.

## Review and audit posture

- Default review stance is skeptical and evidence-gated. Approval is earned; do not rubber-stamp.
- Findings come before summary. Use `P0` / `P1` / `P2` / `P3` severity labels and include exact file + line references whenever available.
- Prefer the smallest diff that fixes the issue. Reject drive-by refactors in high-risk areas unless they are required for correctness or maintainability of the target change.
- If a claim cannot be proven from code, artifacts, tests, or docs, report it as unknown, inconclusive, or missing evidence.
- When no issue is provable, say "no finding" explicitly and then list residual risks or missing verification instead of inventing weaknesses.

### High-risk surfaces

- `scripts/auto_cycle.py`
- `src/lab/runners/run_experiment.py`
- `src/lab/reporting/`
- `src/lab/eval/`
- `src/lab/config/contracts.py`
- `schemas/v1/`
- checkpointed defenses such as `c_dog` / `c_dog_ensemble`
- objective-aware or differentiable attacks

### Merge blockers

Block or escalate changes that:

- can silently corrupt state, reports, or run artifacts
- weaken like-for-like comparability or mix authoritative and diagnostic evidence without explicit handling
- change pipeline semantics without updating contracts, schemas, and downstream reporting
- introduce nondeterminism without explicit seed plumbing and documentation
- guess missing evidence, provenance, or deployment readiness
- hide failures behind broad exception handling or fallback behavior that changes experiment meaning

### Required checks by change type

- Stateful or resumable code: require atomic writes, explicit lock cleanup, interruption safety, and idempotent resume behavior.
- Reporting or summary code: require deterministic machine-parseable outputs, correct authority selection, comparability guards, and explicit handling of missing pairs.
- Attack plugins: require registration, objective/ROI correctness, seeded randomness, bounded outputs, same image shape/dtype, and focused smoke validation.
- Defense plugins: require preprocess/postprocess separation, checkpoint provenance, clean-image regression awareness, same image shape/dtype, and focused smoke validation.
- Schema or contract changes: require fixture updates, schema validation, and a deliberate compatibility note.

### Review output format

- Findings first, ordered by severity.
- For each finding: short title, severity, file/line, concrete failure mode, evidence, and the minimal fix.
- Then list open questions or missing tests.
- End with a merge verdict and any residual risk that still needs verification.

## Skills & analysis conventions

### Checkpoint facts (current as of 2026-04-07)

- `dpc_unet_final_golden.pt` — production baseline. Active via `DPC_UNET_CHECKPOINT_PATH` in `.env`.
- `dpc_unet_adversarial_finetuned.pt` — adversarially finetuned checkpoint. Status: **DEPLOYED 2026-04-05 VIA CLEAN GATE; attacked A/B follow-up found no measurable attack-resistance change vs round 2**.
  - Trained on: square_retention round 3 — square x5 oversample + deepfool + blur pairs; resumed from round 2
  - Clean (no-attack) A/B (2026-04-05, 500 images, c_dog): new +0.0025 mAP50 vs prior — no clean regression.
  - Attacked A/B round 3 vs round 2 (2026-04-07, seed 137, defense=c_dog):
    - square (50 img): delta=-0.0032 — within noise
    - deepfool (100 img): delta=-0.0022 — within noise
  - Evidence: `outputs/eval_ab_clean.json`, `outputs/eval_ab_square_round3.json`, `outputs/eval_ab_deepfool_round3.json`

### Canonical paths for skills

- Cycle history: `outputs/cycle_history/<cycle_id>.json` (newest = latest cycle)
- Cycle state: `outputs/cycle_state.json`
- A/B eval artifacts: `outputs/eval_ab_*.json` (may not exist)
- Framework reports: `outputs/framework_reports/<sweep_id>/`

### mAP50 source rule

Use Phase 4 `validate_*` rows from `cycle_history/<cycle_id>.json` as the authoritative source for mAP50. Phase 1/2 smoke runs use detection confidence metrics and are not comparable to Phase 4 full-dataset mAP50 values.

### auto_summary false-positive warning

`generate_auto_summary.py` may emit false-positive `NO_VALIDATION` and `DEFENSE_DEGRADES_PERFORMANCE` warnings. Root cause: Phase 1 smoke runs are processed before Phase 4 `validate_*` rows and may shadow them. Do not propagate these warnings without verifying that the source row in `validation_results` is from Phase 4.

### Stale cycle state rule

`outputs/cycle_state.json` may be stale. If its `cycle_id` does not match the target run context or the latest `cycle_history` entry, do not treat it as authoritative for the current analysis. Surface the mismatch explicitly as a `stale_cycle_state` anomaly or warn-level issue. Always prefer the resolved cycle artifact over cycle_state when they conflict.

### Evidence integrity rule

Do not infer missing evidence. If a metric, file, or result is absent, record it as unknown or missing explicitly — do not fill the gap with assumptions or interpolation.

## Maintenance guidance for skills

- Keep project-wide rules in this file; keep each skill task-specific.
- Use `.claude/skills/<skill-name>/SKILL.md` with support files (`reference.md`, `examples/`).
- Use least-privilege `allowed-tools` and set `disable-model-invocation: true` for manual-only strategic skills.
- Prefer `context: fork` for isolated planner/judge workflows.
- Keep `SKILL.md` concise; place detailed examples and contracts in support files.

## PR and commit discipline

- Each PR must address exactly one concern. Do not bundle unrelated fixes, features, or subsystems into a single PR without explicit instruction.
- Omnibus PRs that simultaneously touch runner code, reporting code, new scripts, schemas, and tests across unrelated areas will be held for split-and-re-review.
- Each commit within a PR must be atomic: one logical change per commit with a message that states what changed and why, not just what files were touched.
- Before opening a PR, state in the description: (1) the single concern this PR addresses, and (2) what it explicitly does not address.
- If a task requires changes across many subsystems, open one PR per subsystem boundary and reference the others. Prefer sequential PRs over a single large one.
- For pre-merge or post-change review passes, prefer `.claude/skills/big-brother-auditor/` and keep its checklist aligned with this file.

## Local configuration policy

- Follow `docs/LOCAL_CONFIG_POLICY.md` for local-vs-shared config governance.
- Keep editor-local state and secrets out of version control; use `.env` and ignored local settings.
