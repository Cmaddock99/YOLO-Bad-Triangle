---
name: experiment-planner
description: Recommend the next 3-5 highest-value framework experiments using recent evidence, allowed plugins, and budget constraints. Use when deciding what to run next.
argument-hint: "--budget <time_or_runs> --attacks <list> --defenses <list> [--cycle-path <path>]"
disable-model-invocation: true
context: fork
allowed-tools: Read, Glob, Grep
---

Build a prioritized, budget-aware experiment queue from verified evidence.

## Inputs
- Budget constraints (time budget, max run count, or image budget).
- Allowed attacks list and allowed defenses list.
- Optional explicit cycle/report path; otherwise resolve latest cycle under `outputs/framework_reports/`.
- Optional delivery timeline constraints.

## Steps
1. Resolve planning evidence path from input or newest `outputs/framework_reports/` directory.
2. Extract baseline, attack-only, and defended outcomes relevant to allowed plugins.
3. Validate comparability prerequisites before proposing runs (baseline presence, compatible image counts, compatible eval assumptions).
4. Generate candidate next experiments inside budget and plugin constraints.
5. Score candidates by information gain, recovery potential, and cost/risk.
6. Return a priority queue of 3-5 runs with explicit params, stop conditions, and risk notes.
7. If evidence quality is insufficient, return blocked recommendations via `blocked_by`.

## Constraints
- Read-only behavior only; do not execute runs or edit repository files.
- Recommend only framework-first runs; no ad-hoc entrypoints.
- Do not recommend non-comparable experiments as if they were reliable.
- Do not infer missing evidence; use `blocked_by` and conservative status.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
