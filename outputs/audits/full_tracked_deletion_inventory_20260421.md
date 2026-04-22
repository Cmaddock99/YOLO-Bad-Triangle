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

| path | kind | brief purpose | written_on | current evidence of use | quality_rating | usage_rating | deletion_confidence | reason to delete | notes / revisit |
|---|---|---|---|---|---:|---:|---|---|---|
| `setup_assets.sh` | stale bootstrap script | legacy asset/bootstrap helper | 2026-03-11 | no exact refs in runtime, tests, CI, or runbook docs | 1 | 0 | high | stale bootstrap path; superseded by `docs/FRESH_CLONE_SETUP.md`; historically called missing `scripts/convert_coco_to_yolo.py` | delete outright; no migration needed |
| `dpc_unet_adversarial_finetuned.pt.prev` | binary sidecar | previous checkpoint snapshot | 2026-04-07 | exact refs only in `.claude` skill material and AB notebooks | 4 | 1 | high | bulky binary sidecar with no canonical runtime role or current runbook reference | if any provenance matters, record hash/name in a note before removal |
| `SPEC.md` | backlog doc | living improvement backlog from cycle era | 2026-03-28 | no live runbook/CI/test refs; only self-reference and one historical spec mention | 2 | 1 | high | stale planning ledger, superseded by code plus current quality standard | if one or two items still matter, fold them into issues or a short TODO note first |
| `colab_sweep.ipynb` | historical notebook | old GPU sweep notebook; self-labeled non-canonical | 2026-03-20 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | explicitly non-canonical historical workflow | delete outright |
| `notebooks/ab_tests/` | historical notebook subtree | four one-off AB experiment notebooks (`ab_r2_*`, `ab_r3_*`) | 2026-04-07 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | self-contained historical experiment payload | if any result is still important, capture it in one short markdown note before deletion |
| `docs/analysis/cycle6_analysis_and_recommendations.md` | historical analysis doc | one cycle-era recommendation memo | 2026-03-25 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | historical decision memo with no current contract | safe to remove as archive noise |
| `docs/analysis/cycle7_8_status_and_recommendations.md` | historical analysis doc | one cycle-era status memo | 2026-03-26 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | historical operating note, not current guidance | safe to remove as archive noise |
| `docs/analysis/direction_a_square_pivot_contingency.md` | historical analysis doc | contingency memo for an abandoned branch of Direction A | 2026-04-09 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | contingency note for a closed decision branch | safe to remove once closure record is retained |
| `docs/analysis/nuc_execution_spec_20260409.md` | machine execution spec | one-off NUC execution instructions | 2026-04-09 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | dated operator instructions, not a maintained workflow | safe to remove |
| `docs/analysis/nuc_execution_spec_ts7525_500img.md` | machine execution spec | one-off TS7525 500-image execution instructions | 2026-04-09 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | dated operator instructions, not a maintained workflow | safe to remove |
| `outputs/audits/recent_updates_20260420.md` | historical audit output | prior repo audit report artifact | 2026-04-21 | no exact refs in current runbook, tests, or CI | 3 | 0 | high | historical audit artifact with no live dependency | keep only if you want an audit paper trail inside the repo |
| `outputs/audits/recent_updates_20260420_followup_prompts.md` | historical audit output | prompt list derived from the prior audit | 2026-04-21 | no exact refs in current runbook, tests, or CI | 2 | 0 | high | stale follow-up prompt artifact | safe to remove |
| `outputs/eval_ab_deepfool_phase4.json` | historical eval artifact | one-off A/B checkpoint result | 2026-04-04 | no exact refs in runtime, tests, CI, or runbook docs | 3 | 0 | high | standalone evidence artifact not part of current canonical reporting surface | delete or archive outside repo |
| `outputs/eval_ab_square_phase4.json` | historical eval artifact | one-off A/B checkpoint result | 2026-04-04 | no exact refs in runtime, tests, CI, or runbook docs | 3 | 0 | high | standalone evidence artifact not part of current canonical reporting surface | delete or archive outside repo |
| `outputs/eval_bak_vs_golden_blur.json` | historical eval artifact | one-off blur comparison result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_bak_vs_golden_deepfool.json` | historical eval artifact | one-off deepfool comparison result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_normalize_fix_blur.json` | historical eval artifact | one-off normalize-fix blur result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_normalize_fix_deepfool.json` | historical eval artifact | one-off normalize-fix deepfool result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_r2_blur.json` | historical eval artifact | one-off round-2 blur result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_r2_deepfool_old.json` | historical eval artifact | one-off round-2 deepfool baseline result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_r2_deepfool_strong.json` | historical eval artifact | one-off stronger deepfool round-2 result | 2026-03-29 | no exact refs in runtime, tests, CI, or runbook docs | 2 | 0 | high | top-level historical scratch artifact | safe to remove |
| `outputs/eval_normalize_fix_blur.log` | grandfathered log artifact | legacy blur debug log | 2026-03-29 | exact ref only in `scripts/ci/check_tracked_outputs.py` grandfather list | 1 | 1 | high | explicitly grandfathered local-only log, not canonical output | delete and remove from grandfather list in a later cleanup pass |
| `outputs/eval_normalize_fix_deepfool.log` | grandfathered log artifact | legacy deepfool debug log | 2026-03-29 | exact ref only in `scripts/ci/check_tracked_outputs.py` grandfather list | 1 | 1 | high | explicitly grandfathered local-only log, not canonical output | delete and remove from grandfather list in a later cleanup pass |
| `outputs/eval_r2_blur.log` | grandfathered log artifact | legacy round-2 blur debug log | 2026-03-29 | exact ref only in `scripts/ci/check_tracked_outputs.py` grandfather list | 1 | 1 | high | explicitly grandfathered local-only log, not canonical output | delete and remove from grandfather list in a later cleanup pass |
| `outputs/eval_r2_deepfool_old.log` | grandfathered log artifact | legacy round-2 deepfool debug log | 2026-03-29 | exact ref only in `scripts/ci/check_tracked_outputs.py` grandfather list | 1 | 1 | high | explicitly grandfathered local-only log, not canonical output | delete and remove from grandfather list in a later cleanup pass |
| `outputs/eval_r2_deepfool_strong.log` | grandfathered log artifact | legacy round-2 strong deepfool debug log | 2026-03-29 | exact ref only in `scripts/ci/check_tracked_outputs.py` grandfather list | 1 | 1 | high | explicitly grandfathered local-only log, not canonical output | delete and remove from grandfather list in a later cleanup pass |
| `outputs/framework_reports/framework_run_report.md` | legacy generated artifact | top-level report outside canonical `<sweep_id>/` layout | 2026-03-19 | no exact refs; current docs only describe `outputs/framework_reports/<sweep_id>/...` | 3 | 0 | high | stale non-canonical root-level generated artifact | delete unless you intentionally preserve one “latest report” mirror |
| `outputs/framework_reports/framework_run_summary.csv` | legacy generated artifact | top-level CSV outside canonical `<sweep_id>/` layout | 2026-03-19 | no exact refs; current docs only describe `outputs/framework_reports/<sweep_id>/...` | 3 | 0 | high | stale non-canonical root-level generated artifact | delete unless you intentionally preserve one “latest report” mirror |
| `outputs/summaries/` | generated output subtree | auto-summary outputs (`headline_metrics.csv`, `summary.json`, `warnings.json`, etc.) | 2026-03-29 | exact refs only in `.gitignore` and `scripts/reporting/generate_auto_summary.py` default output path | 2 | 2 | high | self-contained generated outputs not mentioned in the current runbook or tracked-output policy | if feature stays, keep the path untracked and regenerate on demand |

## Medium-confidence delete candidates

| path | kind | brief purpose | written_on | current evidence of use | quality_rating | usage_rating | deletion_confidence | reason to delete | notes / revisit |
|---|---|---|---|---|---:|---:|---|---|---|
| `REMEDIATION_PLAN.md` | historical planning doc | remediation checklist from the full-repo audit wave | 2026-03-29 | still named in `CLAUDE.md` and `docs/analysis/repo_audit_remediation_spec_2026-04-08.md` | 3 | 2 | medium | historical plan, largely superseded by current code state and `CODE_QUALITY_STANDARD.md` | remove only after cleaning `CLAUDE.md` and the linked analysis doc |
| `docs/analysis/fix_spec.md` | historical planning doc | detailed fix-spec support doc for the remediation wave | 2026-03-26 | only exact ref is `docs/analysis/repo_audit_remediation_spec_2026-04-08.md` | 2 | 1 | medium | historical planning support doc with no direct current workflow use | delete together with the remediation spec |
| `docs/analysis/repo_audit_remediation_spec_2026-04-08.md` | historical planning doc | execution-ready remediation spec derived from a past audit | 2026-04-08 | no exact current runbook refs, but still forms a small historical doc chain with `fix_spec.md` and `REMEDIATION_PLAN.md` | 3 | 1 | medium | historical audit execution plan, not a current runbook | delete as a bundle with `fix_spec.md` and possibly `REMEDIATION_PLAN.md` |
| `outputs/eval_ab_clean.json` | evidence artifact / sentinel | clean A/B checkpoint result; current clean validation sentinel path | 2026-04-01 | exact refs in `CLAUDE.md`, `.claude` research/colab skills, and `scripts/training/evaluate_checkpoint.py` sentinel logic | 4 | 2 | medium | current file is evidence residue rather than a required checked-in baseline | if removed, update `CLAUDE.md` and rely on regeneration instead of tracking |
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
