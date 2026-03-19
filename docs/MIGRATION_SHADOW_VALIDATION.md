# Migration Shadow Validation Gates

Use these gates for each migrated surface before enabling framework-first defaults.

## Gate Inputs

- `legacy_csv`: operator-approved legacy output (`metrics_summary.csv`)
- `framework_runs_root`: framework run folders (`metrics.json`, `run_summary.json`)
- `compat_output_root`: location for generated legacy-compatible artifacts

## Gate Steps

1. Generate compatibility artifacts from framework runs:

   - `./.venv/bin/python scripts/generate_legacy_compat_artifacts.py --runs-root <framework_runs_root> --output-root <compat_output_root>`

2. Compare legacy vs compatibility contracts:

   - `./.venv/bin/python scripts/validate_migration_shadow.py --legacy-csv <legacy_csv> --compat-csv <compat_output_root>/metrics_summary.csv --max-metric-delta 1e-6`

3. Validate demo checks on compatibility CSV:

   - `./.venv/bin/python scripts/check_metrics_integrity.py --csv <compat_output_root>/metrics_summary.csv --attack fgsm`
   - `./.venv/bin/python scripts/check_fgsm_sanity.py --csv <compat_output_root>/metrics_summary.csv --attack fgsm`

## Pass Criteria

- `validate_migration_shadow.py` returns `status=PASS`
- Demo gate scripts pass against compatibility CSV
- `experiment_table.md` exists in compatibility output root

## Failure Handling

- If parity fails, keep legacy path as default for that surface.
- Capture failure JSON and attach to migration evidence.
- Fix adapters first; do not change canonical framework metrics semantics to satisfy legacy formatting.
