# Framework Coverage Proof

Date: 2026-03-18

## Purpose

Provide explicit evidence that the framework path now covers legacy core behavior and extends functionality.

## Coverage Map

| Legacy Capability | Legacy Path | Framework Equivalent | Evidence |
|---|---|---|---|
| Model load/infer | `src/lab/models/yolo_model.py` + `ExperimentRunner` | `src/lab/models/yolo_adapter.py` + `UnifiedExperimentRunner` | Framework baseline run `fw_baseline_val` completed with predictions + validation metrics |
| Baseline run | `attack=none defense=none` in legacy CLIs | `attack.name=none defense.name=none` in `src/lab/runners/run_experiment.py` | `outputs/stability_framework/fw_baseline_val/*` |
| Blur attack | `src/lab/attacks/blur.py` | `src/lab/attacks/blur_adapter.py` | `fw_blur_none` run completed |
| FGSM attack | `src/lab/attacks/fgsm.py` | `src/lab/attacks/fgsm_adapter.py` | `fw_fgsm_none` run completed; plugin tests pass |
| PGD attack | `src/lab/attacks/pgd.py` | `src/lab/attacks/pgd_adapter.py` | `fw_pgd_none` run completed; plugin tests pass |
| DeepFool attack | `src/lab/attacks/deepfool.py` | `src/lab/attacks/deepfool_adapter.py` | `fw_deepfool_none` run completed; plugin tests pass |
| No-op defense | `src/lab/defenses/none.py` | `src/lab/defenses/none_adapter.py` | baseline/attack framework runs completed |
| Preprocess defense | legacy median/denoise preprocessing path | `src/lab/defenses/preprocess_median_blur_adapter.py` | `fw_blur_preprocess_median` run completed |
| Postprocess defense | legacy path has no normalized postprocess hook | `src/lab/defenses/confidence_filter_adapter.py` | `fw_blur_conf_filter` run completed |
| Validation metrics capture | `val/metrics.json` + CSV append | framework `metrics.json.validation` | baseline validation status `complete` with precision/recall/mAP fields |
| Prediction stats | label parsing in legacy CSV appender | framework `metrics.json.predictions` | all framework runs emit confidence/detection summary |
| Structured outputs | legacy mixed run files + CSV | `predictions.jsonl`, `metrics.json`, `run_summary.json`, `resolved_config.yaml` | verified in framework run directories |
| Comparison/reporting | legacy CSV table + plot scripts | `src/lab/reporting/framework_comparison.py` + `scripts/generate_framework_report.py` | report generation succeeded (`framework_run_summary.csv`, `framework_run_report.md`) |

## Test Evidence

- Focused framework tests:
  - `tests/test_framework_attack_plugins.py`
  - `tests/test_framework_defense_plugins.py`
  - `tests/test_framework_reporting.py`
- Full regression suite:
  - `python -m unittest discover -s tests -p "test_*.py"` -> `42` tests passed

## Runtime Evidence

- Framework matrix output root: `outputs/stability_framework`
  - baseline + blur + FGSM + PGD + DeepFool + defense variants completed.
- Framework report output root: `outputs/stability_framework_reports`
  - `framework_run_summary.csv`
  - `framework_run_report.md`
- Legacy smoke matrix output root: `outputs/stability_legacy_tiny`
  - `metrics_summary.csv`
  - `experiment_table.md`
  - integrity check status: `ok`

## Go/No-Go Decision

Decision: **GO (Stage 1 deprecation)** and **conditional GO (Stage 2 cleanup)**

Rationale:

- Framework path now covers required baseline and attack/defense feature set.
- Validation and reporting artifacts are stable and reproducible.
- Legacy path still passes smoke verification, enabling controlled migration.

Condition for Stage 2 cleanup:

- Keep thin compatibility wrappers/documentation redirects where needed.
- Run full regression and stability matrix after cleanup to confirm no critical regressions.
