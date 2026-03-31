---
name: experiment-planner
description: Recommend the next 3-5 highest-value framework experiments using recent evidence, allowed plugins, and budget constraints. Use when deciding what to run next.
argument-hint: "--budget <time_or_runs> --attacks <list> --defenses <list> [--cycle-path <path>]"
disable-model-invocation: false
context: fork
allowed-tools: Read, Glob, Grep
---

Build a prioritized, budget-aware experiment queue from verified evidence.

## Inputs
- Budget constraints (time budget, max run count, or image budget). Format: `max_runs=N`, `max_images=N`, or `wall_hours=N`.
- Allowed attacks list and allowed defenses list (default: all registered plugins).
- Optional explicit cycle path; otherwise resolve latest file in `outputs/cycle_history/`.
- Optional delivery timeline constraints.

## Steps
1. Read `outputs/cycle_state.json` if present — check current phase. If Phase 4 is still active, note it; do not propose runs that conflict with an in-progress cycle.
2. Read `outputs/eval_ab_*.json` if present — check checkpoint deployment status. If a CONDITIONAL PASS exists and clean (no-attack) validation is absent, insert clean baseline A/B as priority 1 before any other recommendations.
3. Resolve planning evidence from input path or newest `outputs/cycle_history/<cycle_id>.json`.
4. Extract baseline, attack-only, and defended `validation_results` relevant to allowed plugins.
5. Validate comparability prerequisites before proposing runs: baseline present, compatible image counts, compatible eval assumptions. If prerequisites fail, use `blocked_by` instead of fabricating rankings.
6. Generate candidate next experiments inside budget and plugin constraints.
7. Score candidates by: information gain, recovery improvement potential, checkpoint deployment unblocking, cost/risk.
8. Return a priority queue of 3–5 runs with explicit params, stop conditions, and risk notes.
9. If evidence quality is insufficient, return blocked recommendations via `blocked_by`.

## Constraints
- Read-only behavior only; do not execute runs or edit repository files.
- Recommend only framework-first runs through `scripts/run_unified.py` or `scripts/sweep_and_report.py`; no ad-hoc entrypoints.
- Do not recommend non-comparable experiments as if they were reliable.
- Do not infer missing evidence; use `blocked_by` and conservative status.
- Do not recommend deployment of `dpc_unet_adversarial_finetuned.pt` unless clean validation is confirmed present.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
