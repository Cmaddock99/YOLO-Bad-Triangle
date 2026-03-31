# artifact-contract-checker reference

## Required artifacts (default)
- `metrics.json`
- `predictions.jsonl`
- `run_summary.json`

## Optional provenance artifacts
- If present, track and report auxiliary provenance files (for example resolved config snapshots).
- Optional provenance absence should normally be `warn`, not `fail`, unless strictness rules override.

## Consistency focus
- Cross-file counts where comparable.
- Run identity and seed coherence where available.
- References in summary artifacts should not point to missing dependencies.

## Severity intent
- `fail`: missing required artifacts or hard consistency contradictions.
- `warn`: optional/provenance gaps or soft inconsistencies.
- `pass`: required contract and consistency checks pass without actionable issues.

## Notes
- Keep this skill read-only.
- TODO: Add explicit optional provenance filename allowlist if the repo standardizes one.
