---
name: artifact-contract-checker
description: Validate framework run artifact completeness and internal consistency before analysis, reporting, or parity checks. Use when output integrity must be verified.
argument-hint: "<framework_run_path> [strictness]"
disable-model-invocation: false
allowed-tools: Read, Glob, Grep
---

Verify run artifact contract integrity and analysis readiness.

## Inputs
- Single framework run directory path.
- Optional strictness mode.
- Optional required-file override list.

## Steps
1. Resolve and validate the target framework run directory.
2. Check required artifact presence (`metrics.json`, `predictions.jsonl`, `run_summary.json` unless overridden).
3. Inspect optional provenance files when present and record their presence.
4. Evaluate consistency checks across artifacts (counts, identity/seed consistency, reference integrity).
5. Classify findings by severity and derive overall status (`pass`, `warn`, `fail`).
6. Set `ready_for_analysis` from required-file and consistency outcomes.

## Constraints
- Read-only behavior only; do not rewrite or regenerate artifacts.
- Prefer explicit evidence over assumptions; report unknowns directly.
- Keep outputs deterministic and machine-parseable.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
