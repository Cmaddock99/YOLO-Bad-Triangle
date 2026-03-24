# Repository Health Closure (2026-03-24)

## Goal

Complete the phased repository quality program with evidence-backed scoring, prioritized risks, quick wins, and closure actions while staying framework-first.

## Phase 1 - Baseline Scorecard

| Category | Rating | Evidence |
|---|---|---|
| Architecture consistency | Needs Attention | Canonical flow is clear in `scripts/run_unified.py` -> `src/lab/runners/run_experiment.py`, but guardrail docs referenced a non-existent runner registry path before this closure pass. |
| Correctness and orchestration | Needs Attention | `run_unified.py` previously forwarded unsupported legacy sweep args; `sweep_and_report.py` command paths were cwd-sensitive. |
| Typing and contracts | Needs Attention | Typed helpers exist, but plugin boundaries still rely on broad runtime typing in orchestration paths. |
| Tests and CI | Needs Attention | CI runs tests and artifact-presence checks, but documented mypy gate is not enforced in workflows. |
| Docs and onboarding | Needs Attention | Strong core docs, but some operational docs contain stale or contradictory historical instructions. |
| Repo hygiene | Needs Attention | `.gitignore` policy is mostly solid; generated transfer artifacts are excluded, but process docs still need pruning. |

## Phase 2 - Severity-Ranked Findings

### P0

- CLI mismatch: `scripts/run_unified.py` exposed sweep flags not recognized by `scripts/sweep_and_report.py`, causing avoidable failures.

### P1

- Sweep command builders used relative script paths and could break outside repo-root working directories.
- Framework guardrail rule listed `src/lab/runners/experiment_registry.py`, which is not present.
- `scripts/export_training_data.py` defaulted to a stale date-pinned sweep directory likely missing on clean checkouts.
- Operational handoff docs include contradictory historical guidance.

### P2

- Some docs still need consolidation to reduce accidental reliance on outdated sections.
- Full schema-level output validation in CI can be strengthened beyond presence-only checks.

## Phase 3 - Quick-Win Remediation Blueprint

The following safe, low-churn remediations were applied:

1. Removed unsupported sweep legacy flags from `scripts/run_unified.py`.
2. Made `scripts/sweep_and_report.py` script invocations resolve from repo root, not caller cwd.
3. Corrected the Phase 3 image count in `scripts/auto_cycle.py` docstring to match current tune behavior.
4. Fixed the framework-first rule path in `.cursor/rules/framework-first-architecture.mdc`.
5. Reworked `scripts/export_training_data.py` to auto-resolve the latest `outputs/framework_runs/sweep_*` when `--sweep-root` is omitted.

## Phase 4 - Deeper Refactor Backlog (Second Wave)

1. **CI parity hardening**: enforce mypy in both GitHub and GitLab pipelines; keep lint/type/test requirements symmetric.
2. **Validation depth**: extend CI output checks from required-file presence to schema-validated framework bundle checks for produced artifacts.
3. **CLI surface consolidation**: centralize sweep argument definitions to prevent future drift between wrapper and direct script.
4. **Doc pruning and archival**: separate historical operator notes from canonical runbook guidance.
5. **Plugin interface tightening**: incrementally improve typing around plugin boundaries with explicit protocols where practical.

## Phase 5 - Healthy Coding Habits Operating Standard

Use this routine on every meaningful change:

1. `git status` to verify only intended files changed.
2. `ruff check src tests scripts`
3. `mypy src tests scripts`
4. `PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` (or `pytest -q`)
5. Run one framework smoke command through canonical entrypoints.
6. Validate artifacts with `scripts/ci/validate_outputs.py` when run/report code is touched.

## Phase 6 - Final Overlying Health Check

### Closure verdict

**Overall: Needs Attention (improving).**

The repository is on a correct framework-first path and core execution contracts are intact, but process quality is not yet "Strong" due to CI/type-gate and doc drift.

### What is healthy now

- Canonical framework entrypoints are preserved.
- Quick-win operational blockers identified in this closure pass were remediated.
- Output and reporting paths remain consistent with framework-first constraints.

### Residual risks

- CI still does not require mypy.
- Some process/handoff docs remain noisy and partially contradictory.
- Schema-depth validation in CI can be stricter than required-artifact presence.

### Next 5 prioritized actions

1. Add mypy gate to both CI workflows.
2. Add schema-level JSON validation for framework run artifacts in CI.
3. Consolidate sweep CLI argument definitions/shared parser helpers.
4. Canonicalize `MESSAGES_FOR_NUC_CLAUDE.md` into current + archived sections.
5. Add targeted tests for wrapper CLI argument compatibility and path-resolution behavior.
