# artifact-contract-checker reference

## Required artifacts (default)
- `metrics.json` — schema: `framework_metrics/v1`
- `predictions.jsonl` — per-image prediction records
- `run_summary.json` — schema: `framework_run_summary/v1`

## Optional provenance artifacts (named allowlist)
- `outputs/cycle_state.json` — current cycle phase, active run, top_attacks, top_defenses
- `outputs/eval_ab_*.json` — checkpoint A/B evaluation result files (glob pattern)
- `resolved_config.yaml` — full resolved config snapshot for the run

Optional provenance absence is `warn` (not `fail`) unless `strictness=strict` is specified.

## validation.status field

The `validation.status` field in `metrics.json` uses the value `"complete"` — **not** `"success"`.

Using `"success"` triggers a false `NO_VALIDATION` warning in `generate_auto_summary.py`. When checking validation status, accept `"complete"` as the correct indicator of a completed mAP50 validation run.

## A/B eval and clean validation requirement

If `eval_ab_*.json` artifacts are present (or known to have been run in the current session):
- Check whether a clean (no-attack) A/B run is also present in the artifact set.
- If absent and the artifact set may inform a deployment decision: add a `warn`-level issue with detail: `"finetuned checkpoint has CONDITIONAL PASS on attacked conditions only; clean (no-attack) baseline A/B not present in this artifact set — deployment decision requires this run"`
- Do NOT raise this to `fail` — the artifact set is still valid for analysis purposes.

## Consistency focus
- Cross-file counts: predictions.jsonl record count vs processed image count in run_summary.json.
- Run identity and seed coherence where available.
- `validation.status` value check (see above).
- References in summary artifacts that point to missing files.

## Severity intent
- `fail`: missing required artifacts or hard consistency contradictions.
- `warn`: optional/provenance gaps, conditional A/B status, soft inconsistencies.
- `pass`: required contract and consistency checks pass without actionable issues.

## ready_for_analysis semantics
- `true`: all required files present and no hard consistency failures.
- `false`: one or more required files missing or hard consistency failure.
- Provenance gaps, conditional A/B status, and validation.status quirks do not set this to `false` — they appear as `warn` in `issues`.

## Notes
- Keep this skill read-only.
- Do not assert optional file presence without direct Glob or Read evidence.
