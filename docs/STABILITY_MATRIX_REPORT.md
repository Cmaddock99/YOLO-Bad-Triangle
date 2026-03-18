# Stability Matrix Report

Date: 2026-03-18

## Scope

Pragmatic stability verification over both execution families:

- Framework path (`src/lab/runners/run_experiment.py`)
- Legacy path (`scripts/run_framework.py` + `ExperimentRunner`)

## Framework Matrix Executed

Output root: `outputs/stability_framework`

Runs executed:

1. `fw_baseline_val` (attack=`none`, defense=`none`, validation enabled)
2. `fw_blur_none` (attack=`blur`, defense=`none`)
3. `fw_fgsm_none` (attack=`fgsm`, defense=`none`)
4. `fw_pgd_none` (attack=`pgd`, defense=`none`)
5. `fw_deepfool_none` (attack=`deepfool`, defense=`none`)
6. `fw_blur_preprocess_median` (attack=`blur`, defense=`preprocess_median_blur`)
7. `fw_blur_conf_filter` (attack=`blur`, defense=`confidence_filter`)

Framework artifacts verified per run:

- `predictions.jsonl`
- `metrics.json`
- `run_summary.json`
- `resolved_config.yaml`
- `prepared_images/`

Validation check:

- Baseline validation status: `complete`
- Baseline metrics present:
  - precision: `0.7047237418497081`
  - recall: `0.5317958856923016`
  - mAP50: `0.5991404622367279`
  - mAP50-95: `0.4370359443024839`

Framework reporting utilities:

- `scripts/generate_framework_report.py` executed successfully.
- Generated:
  - `outputs/stability_framework_reports/framework_run_summary.csv`
  - `outputs/stability_framework_reports/framework_run_report.md`

## Legacy Matrix Executed

Command family:

- `scripts/run_framework.py --config configs/pgd_eot_tiny_smoke_matrix.yaml --output_root outputs/stability_legacy_tiny`
- followed by:
  - `scripts/check_metrics_integrity.py`
  - `scripts/generate_experiment_table.py`

Legacy runs completed:

- `yolo26n_baseline-tiny-smoke-conf025`
- `yolo26n_pgd-tiny-smoke-conf025`
- `yolo26n_eot-pgd-tiny-smoke-conf025`

Legacy artifacts verified:

- `outputs/stability_legacy_tiny/metrics_summary.csv`
- `outputs/stability_legacy_tiny/experiment_table.md`
- run directories under `outputs/stability_legacy_tiny/`
- integrity gate status: `ok` with `rows_total=3`

## Result

Pragmatic stability gate: **PASS**

- Full framework matrix scenarios completed (baseline + blur + FGSM + PGD + DeepFool + defense variants).
- Legacy canonical matrix path remained functional and produced expected artifacts.
- Framework comparison/report generation produced valid outputs.

## Notes

- Framework matrix used `max_images=12` for runtime-efficient smoke coverage except baseline validation, which used full validation dataset.
- Legacy verification used tiny smoke matrix for repeatable and bounded runtime.
