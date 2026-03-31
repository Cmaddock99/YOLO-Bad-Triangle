---
name: research-brief
description: Cross-cycle research brief. Reads the last N completed cycles and produces findings, trends, recommended next experiments, and warnings. Run after a cycle completes.
argument-hint: "[--lookback N]  default: 5 cycles"
allowed-tools: Read, Glob, Grep
disable-model-invocation: false
---

Produce an evidence-backed cross-cycle research brief.

## Inputs
- Optional `--lookback N`: how many past cycles to analyze (default 5).
- Cycle histories: `outputs/cycle_history/` — sort by filename, take the N most recent.
- Clean A/B sentinel: `outputs/eval_ab_clean.json` — present if clean validation completed.
- Current cycle state: `outputs/cycle_state.json` — check phase; note if a cycle is still active.

## Steps
1. Glob `outputs/cycle_history/cycle_*.json`, sort, take last N.
2. For each cycle, extract: `top_attacks`, `top_defenses`, `best_attack_params`, and Phase 4 `validation_results` (mAP50 values only).
3. Compute `damage_pct` and `recovery_pct` per cycle using the formulas in `reference.md`.
4. Identify cross-cycle trends: are param trajectories converging or diverging? Is any attack/defense pair consistently improving or degrading?
5. Read `outputs/eval_ab_clean.json` if present — record checkpoint deployment status.
6. Read `outputs/cycle_state.json` — note current phase and whether analysis is mid-cycle.
7. Populate all required JSON fields. Set `status` to reflect evidence completeness.

## Constraints
- Read-only. Do not execute experiments or modify files.
- Do not infer missing evidence. If a cycle is missing Phase 4 validation, note it explicitly.
- Do not claim trends from fewer than 2 data points. Use `"insufficient data"` instead.
- Do not recommend checkpoint deployment unless `eval_ab_clean.json` confirms clean validation complete.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
