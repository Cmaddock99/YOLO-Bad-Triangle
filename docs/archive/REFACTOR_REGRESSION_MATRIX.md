# Refactor Regression Matrix

This matrix defines the minimum behavior checks to run before/after structural refactors.

## Canonical Runtime Paths

1. Unified single run dry-check
   - `python scripts/run_unified.py run-one --config configs/lab_framework_phase5.yaml --set runner.max_images=1 --set runner.run_name=regression_smoke --set summary.enabled=false --set parity.enabled=false --set validation.enabled=false`
2. Unified sweep dry-check
   - `python scripts/run_unified.py sweep --config configs/lab_framework_phase5.yaml --attacks fgsm --no-legacy-compat`
3. Root wrapper forwards to framework path
   - `python run_experiment.py --dry-run`
4. Framework batch wrapper forwards to unified/sweep path
   - `python scripts/run_framework.py --config configs/week1_stabilization_demo_matrix.yaml --output-root outputs/regression_wrapper --attacks fgsm`

## Migration/CI Gates

5. Parity gate entrypoint
   - `python scripts/ci/check_parity_gate.py --config configs/parity_test.yaml`
6. Demo gate entrypoint
   - `python scripts/ci/check_demo_gate.py --profile week1-demo --output-root outputs/demo-gate-ci`
7. Artifact gate against demo outputs
   - `python scripts/ci/check_artifact_gate.py --output-root outputs/demo-gate-ci`
8. Schema gate against latest run outputs
   - `python scripts/ci/validate_output_schemas.py --framework-run-dir <run_dir> --legacy-compat-csv <metrics_summary.csv>`
9. Full migration gate orchestrator
   - `python scripts/ci/run_migration_gates.py --parity-config configs/parity_test.yaml --demo-profile week1-demo --allow-missing-baseline`

## Sanity/Regression Checks

10. Metrics integrity
    - `python scripts/check_metrics_integrity.py --csv outputs/metrics_summary.csv --attack fgsm`
11. FGSM sanity (latest session)
    - `python scripts/check_fgsm_sanity.py --csv outputs/metrics_summary.csv --use-latest-session --fail-on-all-zero-fgsm`

## Pass Criteria

- Exit code is 0 for all checks.
- Artifact contracts are unchanged (`metrics_summary.csv`, `experiment_table.md`, `metrics.json`, `run_summary.json`).
- Parity thresholds remain unchanged unless intentionally modified in config/policy (canonical defaults/keys live in `src/lab/config/contracts.py`).
- Output files preserve schema versions:
  - `framework_metrics/v1`
  - `framework_run_summary/v1`
  - `legacy_compat_csv/v1`
