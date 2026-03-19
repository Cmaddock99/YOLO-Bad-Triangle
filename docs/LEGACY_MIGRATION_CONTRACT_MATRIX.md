# Legacy-to-Framework Contract Matrix

This matrix defines strict compatibility requirements for phased migration.

## Metadata

- `validated_at_utc`: `2026-03-19T17:55:15Z`
- `validated_against_commit`: `4a11a17`
- `migration_strategy`: phased-by-surface
- `compatibility_bar`: strict-contract-preservation

## Contract Table

| Legacy contract | Current producer | Framework source of truth | Adapter/bridge | Owner | Status |
|---|---|---|---|---|---|
| `outputs/metrics_summary.csv` | `src/lab/eval/metrics.py` via legacy runners | `outputs/framework_runs/*/{metrics.json,run_summary.json}` | `scripts/generate_legacy_compat_artifacts.py` | Migration layer | In progress |
| `outputs/experiment_table.md` | `generate_experiment_table` from legacy CSV | Legacy-compatible CSV generated from framework runs | `scripts/generate_legacy_compat_artifacts.py` | Migration layer | In progress |
| Demo gate expectations (`check_metrics_integrity.py`) | Legacy CSV columns/semantics | Adapter-generated CSV columns/semantics | `scripts/generate_legacy_compat_artifacts.py` | Demo ops | In progress |
| Demo sanity expectations (`check_fgsm_sanity.py`) | Legacy FGSM rows and params in CSV | Adapter-generated FGSM rows from framework runs | `scripts/generate_legacy_compat_artifacts.py` | Demo ops | In progress |
| Framework canonical metrics | `src/lab/runners/run_experiment.py` | Same | none | Framework runtime | Complete |
| Framework reports (`framework_run_summary.csv`, `framework_run_report.md`) | `scripts/generate_framework_report.py` | Same | none | Reporting | Complete |
| Team summary (`team_summary.json`, `team_summary.md`) | `scripts/generate_team_summary.py` | Same | none | Reporting | Complete |
| Overnight status/report contracts | `scripts/run_overnight_stress.py` | Same | none | Ops | Complete |

## Surface Migration Mapping

| Surface | Legacy entry | Target entry | Compatibility requirement |
|---|---|---|---|
| One-run CLI | `run_experiment.py` | `src/lab/runners/run_experiment.py` | Keep legacy command available as wrapper/deprecated compat |
| Batch/matrix CLI | `scripts/run_framework.py` | `scripts/sweep_and_report.py` | Legacy batch path remains supported until dual-cycle parity |
| Demo orchestration | `scripts/run_week1_stabilization.sh` | framework-backed runner + adapter output | Preserve exact user-facing command and gate behavior |
| Reporting | legacy CSV + plot scripts | framework reports + legacy-compatible CSV view | Both report families available during migration |

## Compatibility Rules

1. Never remove a legacy contract unless an adapter-backed equivalent is available.
2. Legacy and framework runs may coexist, but compatibility artifacts must be explicit and reproducible.
3. Any changed default entrypoint must have rollback instructions for one release window.
4. Contract checks must be runnable via automated scripts before cutover.

