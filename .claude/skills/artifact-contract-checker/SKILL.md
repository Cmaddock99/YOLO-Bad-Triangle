---
name: artifact-contract-checker
description: Validate framework run artifact completeness and internal consistency before analysis, reporting, or parity checks. Use when output integrity must be verified.
argument-hint: "<framework_run_path> [strictness]"
disable-model-invocation: false
allowed-tools: Read, Glob, Grep
---

Verify run artifact contract integrity and analysis readiness.

## Inputs
- Single framework run directory path (or cycle history JSON path for cycle-level checks).
- Optional strictness mode (`strict` raises provenance gaps to `fail`; default treats them as `warn`).
- Optional required-file override list.

## Steps
1. Resolve and validate the target path exists.
2. Check required artifact presence (`metrics.json`, `predictions.jsonl`, `run_summary.json` unless overridden).
3. Check optional provenance artifacts when present: `outputs/cycle_state.json`, `outputs/eval_ab_*.json`, `resolved_config.yaml`. Record presence/absence for each.
4. Evaluate consistency checks across artifacts:
   - prediction count alignment (predictions.jsonl record count vs processed image count in run_summary)
   - run identity and seed coherence where available
   - `validation.status` field value: `"complete"` is the correct value (not `"success"`) — check for unexpected values
   - references in summary artifacts pointing to missing dependencies
5. If `eval_ab_*.json` is present or known to have been run: check whether a clean (no-attack) A/B validation run is also present. If absent and the artifact set may be used for deployment decisions, flag as `warn` with deployment-blocker detail.
6. Classify findings by severity and derive overall status (`pass`, `warn`, `fail`).
7. Set `ready_for_analysis` based on required-file and hard consistency outcomes only. Do not set `ready_for_analysis: false` solely due to provenance gaps or conditional A/B status.

## Constraints
- Read-only behavior only; do not rewrite or regenerate artifacts.
- Do not assert presence of optional files without direct evidence (Glob or Read confirms they exist).
- Do not set `ready_for_analysis: true` without qualification when the artifact set will be used for a deployment decision and clean validation is absent.
- Prefer explicit evidence over assumptions; record unknowns directly.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
