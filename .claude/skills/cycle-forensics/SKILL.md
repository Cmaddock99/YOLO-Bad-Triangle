---
name: cycle-forensics
description: Summarize the latest completed framework cycle, rank attack damage and defense recovery, and flag anomalies that affect comparability or trust.
argument-hint: "[optional cycle_id or path to cycle_history JSON]"
allowed-tools: Read, Glob, Grep
disable-model-invocation: false
---

Produce a strict, evidence-backed cycle outcome snapshot.

## Inputs
- Optional explicit cycle ID (e.g. `cycle_20260329_125124`) or direct path to a cycle history JSON.
- If omitted, resolve the most recent entry in `outputs/cycle_history/` (sort by filename).
- Also read `outputs/cycle_state.json` when present for current phase and active-run context.
- Also check `outputs/eval_ab_*.json` for checkpoint A/B evaluation context.

## Steps
1. Resolve `cycle_path` from input or newest file in `outputs/cycle_history/`.
2. Read cycle history JSON: extract `top_attacks`, `top_defenses`, `validation_results`, `best_attack_params`, `checkpoint_fingerprint`.
3. Identify comparable baseline (`validate_baseline`), attack-only (`validate_atk_<attack>`), and attack+defense (`validate_<attack>_<defense>`) rows from `validation_results`.
4. Compute `damage_pct` per attack: `(baseline_mAP50 - attack_mAP50) / baseline_mAP50 * 100`. Use mAP50 only — not confidence suppression.
5. Compute `recovery_pct` per attack+defense pair: `(defended_mAP50 - attack_mAP50) / (baseline_mAP50 - attack_mAP50) * 100`. Negative values are valid and must be reported.
6. Rank attacks by `damage_pct` descending; rank defenses by `recovery_pct` descending (include negatives).
7. Flag anomalies: missing pairs, image-count mismatches, negative recovery, param bound hits, conditional A/B eval (clean validation pending).
8. Read `outputs/cycle_state.json` if present; note active cycle phase and whether Phase 4 is still in progress.
9. Populate all required JSON fields; set `status` to reflect evidence completeness.

## Constraints
- Read-only; do not execute experiments or modify files.
- Do not infer missing evidence; record unknowns explicitly in JSON fields.
- Compute all metrics from mAP50 in Phase 4 `validate_*` runs — not from Phase 1/2 confidence suppression metrics.
- `warnings.json` from auto_summary may contain false-positive `NO_VALIDATION` and `DEFENSE_DEGRADES_PERFORMANCE` entries when Phase 1/2 smoke runs shadow Phase 4 results. Do not propagate these without verifying the source metric.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
