# Full Tracked Deletion Inventory

Date: 2026-04-21  
Scope: tracked-and-existing repo content only (`git ls-files` filtered to paths still present in the worktree)  
Goal: list only items recommended for deletion after verification

## Method

- Included only tracked files or tracked subtrees that still exist in the current worktree.
- Excluded untracked machine state, caches, local envs, and already-deleted tracked paths.
- Used first-added git date (`git log --diff-filter=A --follow`) as `written_on`.
- Verified usage by scanning current runtime code, tests, CI, policy docs, and runbook docs.
- Classified usage as `core`, `compatibility`, `optional-maintained`, `historical`, or `orphaned`.
- Reserved `high` deletion confidence for items with no maintained writer/default path, no live reporting/test coupling, and no tracked provenance dependency that would be left dangling.

## Rating scale

- `quality_rating`
  - `1`: broken, misleading, stale, or junk
  - `2`: low-value historical/generated residue
  - `3`: understandable but redundant or non-canonical
  - `4`: decent quality but sidecar/non-essential
  - `5`: strong current artifact
- `usage_rating`
  - `0`: no live refs
  - `1`: archival/manual only
  - `2`: mentioned by docs or one-off workflow
  - `3`: optional current workflow
  - `4`: CI/tests/compatibility surface
  - `5`: core runtime surface

## Verified retain surfaces

These were checked and intentionally left out of the deletion tables:

- Root wrapper CLIs under `scripts/*.py`: protected by compatibility tests in `tests/test_repo_structure_compat.py`, `tests/test_reporting_and_demo_script_compat.py`, `tests/test_training_script_compat.py`, and `tests/test_cli_wrapper_entrypoints.py`.
- Current runbook/policy docs: `README.md`, `PROJECT_STATE.md`, `CODE_QUALITY_STANDARD.md`, `docs/FRESH_CLONE_SETUP.md`, `docs/LOOP_DESIGN.md`, `docs/LOCAL_CONFIG_POLICY.md`, `docs/ATTACK_TEMPLATE.md`, `docs/DEFENSE_TEMPLATE.md`.
- `docs/analysis/direction_a_closure_20260409.md`: still referenced exactly by `README.md` and `PROJECT_STATE.md`.
- `notebooks/finetune_dpc_unet.ipynb`: still referenced by `docs/LOOP_DESIGN.md`, `scripts/training/export_training_data.py`, and `scripts/training/train_dpc_unet_local.py`.
- Canonical tracked reporting surfaces under `outputs/cycle_history/**`, `outputs/cycle_report.*`, `outputs/dashboard.html`, and `outputs/framework_reports/<sweep_id>/**`: still described in `README.md`, `PROJECT_STATE.md`, `CLAUDE.md`, and allowed by `tests/test_tracked_output_policy.py`.

Note: the earlier `Homework/` payload is not listed below because it is no longer present in the current worktree.

## High-confidence delete candidates

All previously listed high-confidence candidates were removed in a later cleanup pass. No current tracked-and-existing paths remain in this bucket.

## Medium-confidence delete candidates

| path | kind | brief purpose | written_on | current evidence of use | quality_rating | usage_rating | deletion_confidence | reason to delete | notes / revisit |
|---|---|---|---|---|---:|---:|---|---|---|
| `dpc_unet_adversarial_finetuned.pt.prev` | binary sidecar / provenance dependency | previous checkpoint snapshot for round-3 A/B evidence | 2026-04-07 | exact refs in `outputs/eval_ab_square_round3.json`, `outputs/eval_ab_deepfool_round3.json`, `.claude` skill material, and AB notebooks | 4 | 2 | medium | tracked provenance still points at this checkpoint, so it is not a safe standalone delete | remove only with the paired round-3 A/B evidence JSONs, or after rewriting those JSONs to stop naming it and preserving any needed provenance summary |
| `outputs/summaries/` | generated output subtree | auto-summary outputs (`headline_metrics.csv`, `summary.json`, `warnings.json`, etc.) | 2026-03-29 | maintained writer default in `scripts/reporting/generate_auto_summary.py`; tracked `outputs/report_tables/...` rows still record concrete files under this subtree | 2 | 3 | medium | not obvious residue; this is a repo policy decision about whether maintained generated summaries stay versioned | if the feature stays, decide explicitly whether this subtree remains tracked or becomes generated-and-untracked, then clean up policy/docs together |
| `outputs/eval_ab_clean.json` | evidence artifact / sentinel | clean A/B checkpoint result; current clean validation sentinel path | 2026-04-01 | exact refs in `CLAUDE.md`, `.claude` research/colab skills, `scripts/training/evaluate_checkpoint.py` sentinel logic, `src/lab/reporting/team_summary.py` external clean-gate provenance support, and `tests/test_framework_reporting.py` coverage | 4 | 4 | medium | current file is still coupled to training sentinel logic, reporting provenance rendering, tests, and instruction material | delete only in a coordinated pass that updates reporting, tests, and instruction/skill references, then switches any remaining workflow to regeneration instead of a tracked sentinel |
| `outputs/eval_ab_deepfool_round3.json` | evidence artifact | round-3 attacked A/B checkpoint result | 2026-04-07 | exact ref in `CLAUDE.md` checkpoint-facts section | 3 | 1 | medium | tracked evidence file embedded in agent instructions, not part of canonical reports | remove only after rewriting the checkpoint-facts section |
| `outputs/eval_ab_square_round3.json` | evidence artifact | round-3 attacked A/B checkpoint result | 2026-04-07 | exact ref in `CLAUDE.md` checkpoint-facts section | 3 | 1 | medium | tracked evidence file embedded in agent instructions, not part of canonical reports | remove only after rewriting the checkpoint-facts section |

## Low-confidence delete candidates

| path | kind | brief purpose | written_on | current evidence of use | quality_rating | usage_rating | deletion_confidence | reason to delete | notes / revisit |
|---|---|---|---|---|---:|---:|---|---|---|
| `docs/index.html` | generated page artifact | GitHub Pages / dashboard output mirror | 2026-03-21 | exact refs in `scripts/reporting/generate_dashboard.py`, `scripts/sweep_and_report.py`, `src/lab/reporting/aggregate/dashboard.py`, and `tests/test_auto_cycle_and_dashboard.py` | 3 | 4 | low | generated artifact living in the repo root docs surface rather than a pure source doc | only delete after retiring the `docs/index.html` write contract and updating tests/runtime flags |

## Later-pass recommendations

- If the goal is maximum slimming, the next pass should target instruction files that still encode historical evidence paths:
  - `CLAUDE.md` checkpoint facts referencing `outputs/eval_ab_*.json`
  - `.claude/skills/**` references to old evidence files and sidecar checkpoints
- If you want to delete more tracked outputs after that, decide explicitly whether the repo will keep:
  - long-horizon `outputs/cycle_history/**`
  - per-sweep `outputs/framework_reports/<sweep_id>/**`
  - the Colab retraining notebook path
- Once those policy decisions are made, rerun this inventory and expect the candidate set to grow materially.
