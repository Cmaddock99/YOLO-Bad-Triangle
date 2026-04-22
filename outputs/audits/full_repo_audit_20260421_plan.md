# Full-Repo Audit Plan — 2026-04-21

## Context

[CODE_QUALITY_STANDARD.md](../../CODE_QUALITY_STANDARD.md) (added in PR #91)
plus [CLAUDE.md](../../CLAUDE.md) define the contract this repo must uphold.
The recent-updates audit
([outputs/audits/recent_updates_20260420.md](recent_updates_20260420.md))
graded PRs #80–#91 against that contract; all 10 findings were remediated in
PRs #92–#98 (merged 2026-04-21). That covered the last ~2 weeks of changes.

This plan audits **the whole repo** so that code outside the PR #80–#91
window — i.e. everything that was already in the tree when the standard was
introduced — gets graded against the same rubric.

The repo has a skill built for exactly this:
[`.claude/skills/full-repo-audit/`](../../.claude/skills/full-repo-audit/SKILL.md).
Its 7-domain partition is the backbone of this plan. One historical audit
exists ([docs/audit_findings.md](../../docs/audit_findings.md) — Domain 1,
2026-04-07, pre-PR-#91); this run continues that accumulator.

## Standards being graded against

Same rubric as the recent-updates audit:

1. **CODE_QUALITY_STANDARD.md** — 6-axis rubric (Correctness / Simplicity /
   Boundary hygiene / Testability / Compatibility / Doc honesty),
   non-negotiables (smallest change, behavior preservation, no dead code,
   intentional boundaries, tested wrappers/shims, no silent contract
   weakening, honest docs), per-change-type rules.
2. **CLAUDE.md merge-blockers** — silent state/artifact corruption,
   comparability loss, semantic changes without contract updates,
   nondeterminism, swallowed errors, fabricated provenance.
3. **High-risk-surface emphasis** — `scripts/auto_cycle.py` (now
   `scripts/automation/auto_cycle.py`), `src/lab/runners/run_experiment.py`,
   `src/lab/reporting/`, `src/lab/eval/`, `src/lab/config/contracts.py`,
   `schemas/v1/`, c_dog defenses, objective-aware/differentiable attacks.

Scope: **full rubric including testability** (flag missing tests for
high-risk surfaces even when code is correct).

## Approach

### Branch

Create `audit/full-repo-20260421` off `main` (367ffb8) before any commits.
Stage files by name — **never** `git add -A`. Local `main` has unrelated
dirty state (`.gitignore`, `Homework/.playwright-cli/` churn) that must not
land in this branch.

### Pass 0 — Skill refresh (doc-only, one commit)

Update [`.claude/skills/full-repo-audit/domains.md`](../../.claude/skills/full-repo-audit/domains.md)
to reflect the PR #91 post-modularization layout. Current lists point at
pre-refactor paths (e.g. `scripts/auto_cycle.py` — now a 25-line wrapper;
real code at `scripts/automation/auto_cycle.py`). Each domain's file list
expands to include:

- **Domain 1**: add `scripts/automation/{auto_cycle,cleanup_stale_runs,watch_cycle}.py`
- **Domain 2**: add `scripts/training/{run_training_ritual,train_from_signal,export_training_data,evaluate_checkpoint,train_dpc_unet_local,train_dpc_unet_feature_loss}.py`
- **Domain 4**: add `scripts/reporting/{generate_auto_summary,generate_cycle_report,generate_dashboard,generate_failure_gallery,generate_framework_report,generate_team_summary,print_summary}.py`;
  add `scripts/demo/run_demo.py`;
  split `src/lab/reporting/` into `aggregate/`, `framework/`, `local/` subdirs
- **Domain 5**: add `src/lab/plugins/{core,extra}/attacks/` directories
- **Domain 6**: add `src/lab/plugins/{core,extra}/defenses/` +
  `src/lab/plugins/{core,extra}/models/` directories
- **Domain 7**: add `src/lab/plugins/{catalog,core_registry,extra_registry,routing_policy}.py`
  at whichever path those actually live (resolve via glob during execution)

Commit message: `docs(audit): refresh full-repo-audit domain list for PR #91 layout`.

### Pass 1 — Mechanical gate

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/run_repo_standards_audit.py --lane full
```

Capture ruff, mypy, and compat-test results verbatim. Anything the gate
already flags goes into a separate "Mechanical findings" section of the
final report and is excluded from the human-judgment passes (no
double-counting).

### Pass 2 — Domain audits (hybrid: 3 direct + 4 parallel)

#### Main thread audits (sequential, high-risk / cross-cutting)

Graded by reading every file end-to-end.

1. **Domain 1 — Core orchestration** (~27 files)
   `scripts/sweep_and_report.py`, `scripts/run_unified.py`,
   `scripts/automation/{auto_cycle,cleanup_stale_runs,watch_cycle}.py`,
   `src/lab/runners/{run_experiment,run_intent,cli_utils}.py`.
   Focus: atomic writes, warm-start idempotency, provenance fingerprint
   completeness, phase gating, cycle-state authority.
   Known open items from 2026-04-07 audit to confirm-or-close:
   - `run_single` skips on `metrics.json` alone (P2)
   - `metrics.json` + `run_summary.json` non-atomic write pair (P2)

2. **Domain 3 — Eval & metrics** (~17 files)
   `src/lab/eval/*.py`, `src/lab/config/contracts.py`, `schemas/v1/*.json`.
   Focus: Phase 4 mAP50 authority rule, schema-code parity, contract
   enforcement at runtime vs CI.

3. **Domain 7 — Infra, contracts, tests** (~55 files)
   `src/lab/core/*.py`, `src/lab/health_checks/*.py`,
   `scripts/ci/*.py`, `tests/test_*.py`.
   Focus: which high-risk surfaces have NO test coverage; which tests are
   import-smoke only; compat-test depth; CI gate coverage of the merge
   blockers in CLAUDE.md.

#### Parallel Explore-agent audits

Each gets a self-contained prompt with:
- the standards (CODE_QUALITY_STANDARD.md + CLAUDE.md excerpts)
- the exact file list for the domain
- the rubric and output format
- instruction to return findings P0→P3 with file:line evidence

Spawned in a single tool-call block so all four run concurrently.

4. **Domain 2 — Training & gate logic** (~5 + moved files)
   `scripts/training/*.py`. Focus: gate exit-code contracts, seed plumbing,
   training data export reproducibility, checkpoint provenance propagation.

5. **Domain 4 — Reporting** (~20 files)
   `src/lab/reporting/{aggregate,framework,local}/*.py`, `scripts/reporting/*.py`,
   `scripts/demo/run_demo.py`. Focus: authority selection (Phase 4 vs Phase
   1/2), comparability guards, atomic writes, missing-pair handling.

6. **Domain 5 — Attacks** (~36 files)
   `src/lab/attacks/*.py` (legacy shims), `src/lab/plugins/{core,extra}/attacks/*.py`.
   Focus: registration consistency, seeded randomness, bounded outputs,
   image shape/dtype preservation, ROI/objective correctness.

7. **Domain 6 — Defenses & models** (~28 files)
   `src/lab/defenses/*.py`, `src/lab/plugins/{core,extra}/defenses/*.py`,
   `src/lab/models/*.py`, `src/lab/plugins/{core,extra}/models/*.py`.
   Focus: preprocess/postprocess separation, checkpoint fingerprinting,
   clean-image regression risk, routing policy correctness.

### Pass 3 — Cross-domain synthesis

Look for patterns that span domains:
- Same anti-pattern in multiple plugins (e.g. broad `except Exception:`
  across attacks)
- Shared contracts violated inconsistently (e.g. `provenance.defense_checkpoints`
  read by some report paths, bypassed by others)
- Doc/code drift across [PROJECT_STATE.md](../../PROJECT_STATE.md),
  [CLAUDE.md](../../CLAUDE.md), [AGENTS.md](../../AGENTS.md)
- Tests that look like coverage but are import-smoke only
- The two open P2s from 2026-04-07 Domain 1 audit — verify status in the
  current code (`scripts/automation/auto_cycle.py` `run_single`;
  `src/lab/runners/run_experiment.py` write sequence around L755-756)

### Pass 4 — Deliverables (one feature branch, multiple commits)

Output layout mirrors the recent-updates audit format:

| File | Content |
|---|---|
| [`outputs/audits/full_repo_audit_20260421.md`](full_repo_audit_20260421.md) | Executive summary: P0/P1/P2/P3 counts, per-domain 6-axis rubric grid, top-10 findings with minimal-fix sketches, recommended follow-up-PR breakdown |
| [`outputs/audits/full_repo_audit_20260421_followup_prompts.md`](full_repo_audit_20260421_followup_prompts.md) | One self-contained prompt per P0/P1 finding (same pattern as `recent_updates_20260420_followup_prompts.md`) |
| [`docs/audit_findings.md`](../../docs/audit_findings.md) | Per-domain detail appended using the existing `## Domain N — <name> (audited 2026-04-21)` header convention |

## Critical files to read

- [CODE_QUALITY_STANDARD.md](../../CODE_QUALITY_STANDARD.md)
- [CLAUDE.md](../../CLAUDE.md)
- [AGENTS.md](../../AGENTS.md) — check for drift vs CLAUDE.md
- [.claude/skills/full-repo-audit/SKILL.md](../../.claude/skills/full-repo-audit/SKILL.md)
- [.claude/skills/full-repo-audit/reference.md](../../.claude/skills/full-repo-audit/reference.md)
- [docs/audit_findings.md](../../docs/audit_findings.md) — prior findings to carry-forward
- [outputs/audits/recent_updates_20260420.md](recent_updates_20260420.md) — prior
  window's findings, verify remediation in code

## Verification of the audit itself

Before delivering, sanity-check:

- Every cited file:line resolves (spot-check 10% via `Read`).
- Every finding cites evidence from current main, not memory.
- Any cited memory-derived fact (checkpoints, baselines) re-verified against
  `outputs/cycle_history/` per CLAUDE.md "Stale cycle state" rule.
- Pass 1 commands actually ran end-to-end; output quoted verbatim.
- The 6-axis rubric scores sum correctly and correlate with per-domain
  finding density.
- No finding duplicated between mechanical (Pass 1) and human-judgment
  (Pass 2) sections.
- Follow-up prompts are self-contained: each can be handed to a fresh
  session without reading the parent report.

## Out of scope

- Implementing fixes.
- Opening issues / PRs (document-only deliverable).
- Re-running the framework cycle.
- Re-auditing PRs #80–#91 (already graded in
  [recent_updates_20260420.md](recent_updates_20260420.md)).
- Pre-#80 git history analysis (YOLOv8 era is closed per existing memory).

## Estimated cost

- Pass 0: ~15 min (read 1 file, write 1 file, commit).
- Pass 1: ~10 min (subprocess wall-time + capture).
- Pass 2: ~90 min (main thread reads ~100 files; 4 parallel agents ~30 min
  each wall-clock).
- Pass 3: ~30 min (cross-reference + carry-forward check).
- Pass 4: ~45 min (write deliverables, verify cites).

Total: ~3 hours wall-clock, roughly doubled in context-token cost.

## Recommended granularity of follow-up PRs

Same pattern as recent-updates: one atomic PR per finding for P0/P1, bundle
P2s by subsystem, defer P3s to a single "quality-debt cleanup" PR. Exact
breakdown decided after findings are in hand.
