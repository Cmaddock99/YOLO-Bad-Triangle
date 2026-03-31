---
name: cycle-forensics
description: Analyze the latest framework cycle, rank attack damage and defense recovery, and flag comparability anomalies. Use when reviewing what happened in the most recent sweep.
argument-hint: "[optional cycle report path]"
disable-model-invocation: false
qallowed-tools: Read, Glob, Grep
---

Produce a strict, evidence-backed cycle outcome snapshot.

## Inputs
- Optional explicit cycle report directory or report file path.
- If omitted, resolve the newest directory under `outputs/framework_reports/`.
- Use report artifacts when present (for example `framework_run_summary.csv` and report tables).

## Steps
1. Resolve `cycle_path` from input or newest `outputs/framework_reports/` directory.
2. Identify comparable baseline, attack-only, and attack+defense rows when available.
3. Compute or extract attack damage and defense recovery for valid comparable pairs.
4. Rank strongest attacks by damage and strongest defenses by recovery.
5. Flag anomalies that weaken trust (missing pairs, image-count mismatch, suspicious outlier behavior).
6. Populate all required JSON fields; use `status` to signal partial/insufficient evidence.

## Constraints
- Read-only behavior only; do not execute experiments or modify files.
- Do not infer missing evidence; record unknowns explicitly in JSON.
- Keep conclusions traceable to available artifacts only.

## Output
Return JSON only matching `examples/schema.json`.
Do not add extra narrative after the JSON contract.
