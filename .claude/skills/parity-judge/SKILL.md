---
name: parity-judge
description: Judge legacy-versus-framework parity for one experiment using explicit tolerance thresholds and strict comparability gates. Use when validating migration confidence.
argument-hint: "<legacy_artifact_path> <framework_artifact_path> [tolerance settings]"
disable-model-invocation: true
context: fork
allowed-tools: Read, Glob, Grep
---

Decide parity only when like-for-like evidence supports it.

## Inputs
- Legacy artifact root path.
- Framework artifact root path.
- Tolerance thresholds for key comparable metrics.
- Optional required artifact list or strictness preferences.

## Steps
1. Validate both input roots and enumerate comparable artifact files.
2. Check like-for-like prerequisites first (experiment intent, eval scope, count compatibility, config compatibility).
3. If comparability fails, return `inconclusive` with explicit issues.
4. Extract key comparable metrics and compute absolute/percent deltas.
5. Record artifact mismatches (missing files, incompatible shapes, count/config mismatches).
6. Apply tolerances and return `pass`, `fail`, or `inconclusive`.

## Constraints
- Read-only behavior only; do not rerun experiments or modify artifacts.
- Do not infer parity from incomplete evidence.
- Keep outputs deterministic and machine-parseable.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
