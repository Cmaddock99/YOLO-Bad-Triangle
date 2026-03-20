# REPO_INVENTORY.md

## Scope

This inventory is based on direct repository inspection of the current codebase state.  
No code execution behavior was changed while producing this file.

## Cleaned Directory Structure (Audit-Focused)

- `run_experiment.py` - compatibility CLI wrapper (legacy path; framework mode forwards to unified runtime).
- `run_experiment_api.py` - argparse compatibility wrapper for explicit single-run invocation.
- `scripts/`
  - `run_unified.py` - canonical runtime entrypoint (`run-one`, `sweep`).
  - `run_framework.py` - compatibility matrix wrapper (legacy path, forwards to unified sweep unless `--legacy`).
  - `run_week1_stabilization.sh` - preflight + matrix + integrity + plotting orchestration.
  - `demo/run_demo_package.sh` - demo action router (`preflight`, `live-demo`, `fast`, `full-demo`, etc.).
  - `check_environment.py` - environment preflight validation.
  - `check_metrics_integrity.py` - CSV integrity/sweep sanity checks.
  - `check_fgsm_sanity.py` - attack trend/collapse sanity checks.
  - `plot_*.py` and `generate_week1_demo_artifacts.sh` - reporting/plot pipelines.
- `src/lab/`
  - `attacks/` - legacy attack interface + implementations + new framework attack interfaces/registries/adapters.
  - `defenses/` - legacy defense interface + implementations + new framework defense interfaces/registries/adapters.
  - `models/` - YOLO wrapper (`YOLOModel`) + framework adapter (`YOLOModelAdapter`) + model registries.
  - `runners/` - legacy orchestration runner, registry resolver, YAML CLI, and unified framework runner.
  - `eval/` - legacy CSV metrics, experiment table, and framework prediction/metrics schema utilities.
  - `datasets/`, `reporting/`, `utils/` - framework scaffold/support packages.
- `configs/`
  - Registry/default config family (`experiment_lab.yaml`).
  - Legacy matrix config family (`modular_experiments.yaml`, `week1_*`, `five_attack_variants_*`, `pgd_eot_*`).
  - Dataset yaml (`coco_subset500.yaml`).
  - Framework config family (`lab_framework_*`).
- `tests/`
  - Runner, attack, FGSM/PGD/EOT, and metrics integrity tests.
- `docs/`
  - Team/operator docs and runbooks; week1/demo legacy workflows retained with unified-runtime-first guidance.

## Python Files By Role

## Experiment Execution / Orchestration

- `run_experiment.py`
- `run_experiment_api.py`
- `scripts/run_unified.py`
- `scripts/run_framework.py`
- `src/lab/runners/cli.py`
- `src/lab/runners/experiment_runner.py`
- `src/lab/runners/experiment_registry.py`
- `src/lab/runners/run_experiment.py`

## Model Loading / Inference

- `src/lab/models/yolo_model.py`
- `src/lab/models/yolo_adapter.py`
- `src/lab/models/registry.py`
- `src/lab/models/plugin_registry.py`
- `src/lab/models/base_model.py`
- `src/lab/models/model_utils.py`

## Attacks

- Legacy attack stack:
  - `src/lab/attacks/base.py`
  - `src/lab/attacks/registry.py`
  - `src/lab/attacks/none.py`
  - `src/lab/attacks/blur.py`
  - `src/lab/attacks/noise.py`
  - `src/lab/attacks/noise_blockwise.py`
  - `src/lab/attacks/fgsm.py`
  - `src/lab/attacks/fgsm_center_mask.py`
  - `src/lab/attacks/fgsm_edge_mask.py`
  - `src/lab/attacks/pgd.py`
  - `src/lab/attacks/eot_pgd.py`
  - `src/lab/attacks/deepfool.py`
  - `src/lab/attacks/deepfool_band_limited.py`
  - `src/lab/attacks/blur_anisotropic.py`
  - `src/lab/attacks/center_mask_blur_noise.py`
  - `src/lab/attacks/patch_occlusion_affine.py`
  - `src/lab/attacks/brightness_contrast_noise.py`
- Framework attack stack:
  - `src/lab/attacks/base_attack.py`
  - `src/lab/attacks/plugin_registry.py`
  - `src/lab/attacks/framework_registry.py`
  - `src/lab/attacks/blur_adapter.py`

## Defenses

- Legacy defense stack:
  - `src/lab/defenses/base.py`
  - `src/lab/defenses/registry.py`
  - `src/lab/defenses/none.py`
  - `src/lab/defenses/median_blur.py`
  - `src/lab/defenses/denoise.py`
- Framework defense stack:
  - `src/lab/defenses/base_defense.py`
  - `src/lab/defenses/plugin_registry.py`
  - `src/lab/defenses/framework_registry.py`
  - `src/lab/defenses/none_adapter.py`

## Metrics / Evaluation / Reporting Data

- `src/lab/eval/metrics.py` (legacy CSV appender)
- `src/lab/eval/experiment_table.py`
- `src/lab/eval/framework_metrics.py` (framework metrics sanitization/summaries)
- `src/lab/eval/prediction_schema.py`
- `src/lab/eval/prediction_adapter.py`
- `src/lab/eval/prediction_io.py`
- `scripts/check_metrics_integrity.py`
- `scripts/check_fgsm_sanity.py`
- `scripts/generate_experiment_table.py`
- `scripts/plot_results.py`
- `scripts/plot_week1_snapshot.py`
- `scripts/plot_week1_report_card.py`
- `scripts/demo/summary_interpretation.py`

## Data Loading / Dataset Wiring

- `configs/coco_subset500.yaml`
- `scripts/convert_coco_to_yolo.py`
- `src/lab/attacks/utils.py` (image discovery helper)
- `src/lab/runners/experiment_runner.py` (`data_yaml`, `image_dir`, labels resolution)
- `src/lab/runners/run_experiment.py` (`data.source_dir` framework schema)

## Key Directories Requested

- `scripts/` - operational entry scripts, environment checks, integrity checks, plotting, demo orchestration.
- `src/` - core implementation tree.
- `src/lab/attacks/` - attack modules (legacy + framework adapters).
- `src/lab/defenses/` - defense modules (legacy + framework adapters).
- `configs/` - all run/config schemas (legacy and framework families).
- `outputs/` - primary artifact root in active scripts/configs.
- `results/` - referenced only as a fallback in plotting auto-detection (`plot_results.py`), not the canonical active output path.

## Suspected And Confirmed CLI Entry Points

## Confirmed executable entrypoints

- `scripts/run_unified.py` (`run-one`, `sweep`; canonical runtime entrypoint)
- `run_experiment.py` (`main()` + `if __name__ == "__main__":`)
- `run_experiment_api.py` (`main()` + `if __name__ == "__main__":`)
- `scripts/run_framework.py` (wrapper to `lab.runners.cli.main`)
- `src/lab/runners/cli.py` (`main()` + `if __name__ == "__main__":`)
- `src/lab/runners/run_experiment.py` (`main()` + `if __name__ == "__main__":`)
- `scripts/run_week1_stabilization.sh`
- `scripts/demo/run_demo_package.sh`

## Secondary executable/utility scripts

- `scripts/check_environment.py`
- `scripts/check_metrics_integrity.py`
- `scripts/check_fgsm_sanity.py`
- `scripts/plot_results.py`
- `scripts/plot_week1_snapshot.py`
- `scripts/plot_week1_report_card.py`
- `scripts/generate_experiment_table.py`
- `scripts/demo/summary_interpretation.py`

## Config Usage Summary

Two active config schemas coexist:

1. **Legacy/registry and matrix schema**
   - Alias/default config: `configs/experiment_lab.yaml`
   - Matrix configs: `configs/modular_experiments.yaml`, `configs/week1_stabilization_*.yaml`, etc.
   - Runtime consumers: `run_experiment.py`, `run_experiment_api.py`, `scripts/run_framework.py`, `src/lab/runners/experiment_runner.py`

2. **Unified framework schema**
   - `configs/default.yaml` (current runnable framework config)
   - Runtime consumers: `scripts/run_unified.py`, `src/lab/runners/run_experiment.py`

Canonical constants source:
- `src/lab/config/contracts.py` centralizes schema IDs, parity thresholds/defaults, runtime toggle keys, and canonical runtime path identifiers.

Known mismatch risk:
- `configs/lab_framework_phase3_compat.yaml` and `configs/lab_framework_skeleton.yaml` are framework-era configs but not aligned with current unified runner expectations for all fields.
