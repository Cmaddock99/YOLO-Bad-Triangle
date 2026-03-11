# Team Guide: Adversarial YOLO Experiment Lab

This guide explains what the project does, how to run it, and what every current function/class is responsible for.

## 1) What this project is

This repository is a modular experiment framework for object detection robustness testing with YOLO.

The run lifecycle is:
1. Resolve experiment settings from YAML + CLI overrides.
2. Optionally generate attacked images.
3. Optionally apply a defense preprocessor.
4. Run YOLO prediction (and optional validation).
5. Aggregate metrics into a CSV.

Primary package: `src/lab`.

## 2) Repository map (current state)

- `src/lab/attacks`: Attack interface + attack implementations + registry loader.
- `src/lab/defenses`: Defense interface + defense implementations + registry loader.
- `src/lab/models`: `YOLOModel` wrapper around Ultralytics YOLO.
- `src/lab/runners`: Experiment orchestration and registry/config resolver.
- `src/lab/eval`: Metrics parsing and CSV appending.
- `configs/`: YAML configs for modular and alias-based experiment execution.
- `scripts/`: CLI wrappers for framework run, metrics append, and dataset conversion.
- `run_experiment.py`: One-command alias-based entrypoint.
- `run_experiment_api.py`, `collect_metrics_api.py`: Compatibility/API-style wrappers.
- `baseline/` and `attacks/`: Legacy/demo entry scripts built on the same core package.

## 3) Prerequisites and environment

## Python and deps

- Use the project virtual environment when available:
  - `./.venv/bin/python --version`
- Install deps (if needed):
  - `./.venv/bin/pip install -r requirements.txt`

Why `.venv` matters: some entrypoints import `ultralytics` at module import time, so system `python3` without installed deps will fail.

## Expected assets

- Model weights expected by default:
  - `yolov8n.pt`
- Dataset expected by default:
  - `coco/val2017_subset500/images`
  - `configs/coco_subset500.yaml`

## 4) How to run the project

## A. One-command lab flow (recommended)

Entrypoint: `run_experiment.py`

Example:
- `python3 run_experiment.py attack=blur model=yolo11 dataset=coco_subset conf=0.25,0.5`

Dry-run only (no model inference, prints resolved config):
- `python3 run_experiment.py attack=deepfool defense=denoise dry_run=true`

Useful overrides:
- `config=configs/experiment_lab.yaml`
- `run_name=my_run run_id=20260311`
- `attack.kernel_size=11 defense.h=12`
- `iou=0.7 imgsz=640 seed=42`
- `validate=true`
- `output_root=outputs/experiments`

How it works:
1. Parses `key=value` tokens.
2. Resolves aliases and parameters with `ExperimentRegistry`.
3. Builds `ExperimentRunner`.
4. Executes attack -> defense -> prediction -> metrics append.

## B. YAML modular flow

Entrypoint: `scripts/run_framework.py` (delegates to `lab.runners.cli.main`)

Example:
- `./.venv/bin/python scripts/run_framework.py --config configs/modular_experiments.yaml`
- `./.venv/bin/python scripts/run_framework.py --config configs/modular_experiments.yaml --confs 0.25,0.5 --output_root outputs/custom`

## C. API/compat wrappers

- `run_experiment_api.py`: CLI wrapper that builds one `ExperimentRunner` config from explicit args.
- `collect_metrics_api.py`: appends metrics for an already-completed run.
- `scripts/collect_metrics.py`: same purpose as above with explicit `--defense`.
- `scripts/run_experiment.py`: runs `configs/baseline_blur_compat.yaml`.

## D. Legacy/demo scripts

- `baseline/run_baseline.py`: one baseline run (`none` attack/defense).
- `baseline/baseline_inference.py`: predicts on `bus.jpg`.
- `attacks/run_confidence_attack.py`: blur attack run example.
- `attacks/confidence_supression.py`: kernel sweep sample for blur confidence effects.

## 5) Config system

## Alias config (`configs/experiment_lab.yaml`)

Defines:
- `defaults` for model/dataset/attack/defense.
- `models`, `datasets` aliases.
- attack and defense aliases with module names + default params.
- runner defaults (`confs`, `iou`, `imgsz`, `seed`, output settings).

Used by:
- `run_experiment.py` + `ExperimentRegistry`.

## Direct modular configs

- `configs/modular_experiments.yaml`: multi-experiment batch examples (baseline, blur, blur+median, noise).
- `configs/baseline_blur_compat.yaml`: compatibility-style runs.

## Dataset yaml

- `configs/coco_subset500.yaml`: dataset root and class names.

## 6) Output structure and artifacts

Common outputs:
- Run directories under configured `output_root`.
- YOLO prediction outputs (images + labels + confidences).
- Optional validation metrics at `run_dir/val/metrics.json`.
- Metrics table at `output_root/metrics_summary.csv`.
- Intermediate transformed images under:
  - `output_root/_intermediates/<run_name>/attacked`
  - `output_root/_intermediates/<run_name>/defended`

## 7) Complete function/class index (current code)

Below is every current top-level function/class and its role.

## Root/API scripts

- `run_experiment.py`
  - `main()`: parse key-value overrides, resolve registry config, optionally dry-run, execute runner.
- `run_experiment_api.py`
  - `main()`: parse explicit CLI args, map to runner config, execute single experiment.
- `collect_metrics_api.py`
  - `main()`: append metrics row for a completed run.

## `scripts/`

- `scripts/run_framework.py`
  - no top-level function; imports and runs `lab.runners.cli.main`.
- `scripts/run_experiment.py`
  - `main()`: run compatibility config `baseline_blur_compat.yaml`.
- `scripts/collect_metrics.py`
  - `main()`: append metrics row with explicit CLI params.
- `scripts/convert_coco_to_yolo.py`
  - script-style module (no function): converts COCO JSON boxes into YOLO label `.txt` files.

## `src/lab/attacks/`

- `base.py`
  - `class Attack`: abstract `apply(...)` interface.
  - `register_attack(*names)`: decorator to register attack class names.
  - `get_attack_class(name)`: lookup from registry.
  - `list_registered_attacks()`: sorted registry keys.
- `registry.py`
  - `_load_builtin_attacks()`: lazy-imports attack modules to trigger decorators.
  - `build_attack(name, params=None)`: instantiate registered attack by name.
- `utils.py`
  - `iter_images(source_dir)`: recursively yields supported image files.
- `none.py`
  - `class NoAttack(Attack).apply(...)`: identity pass-through.
- `blur.py`
  - `class GaussianBlurAttack(Attack)`
    - `__post_init__()`: validates odd kernel size >= 3.
    - `apply(...)`: writes Gaussian-blurred image copies.
- `noise.py`
  - `class GaussianNoiseAttack(Attack).apply(...)`: adds seeded Gaussian noise per pixel.
- `deepfool.py`
  - `class DeepFoolAttack(Attack)`
    - `__post_init__()`: validates `steps` and `epsilon`.
    - `apply(...)`: iterative gradient-style perturbation approximation.

## `src/lab/defenses/`

- `base.py`
  - `class Defense`: abstract `apply(...)` interface.
  - `register_defense(*names)`: decorator to register defense class names.
  - `get_defense_class(name)`: lookup from registry.
  - `list_registered_defenses()`: sorted registry keys.
- `registry.py`
  - `_load_builtin_defenses()`: lazy-import defense modules.
  - `build_defense(name, params=None)`: instantiate registered defense by name.
- `none.py`
  - `class NoDefense(Defense).apply(...)`: identity pass-through.
- `median_blur.py`
  - `class MedianBlurDefense(Defense)`
    - `__post_init__()`: validates odd kernel size >= 3.
    - `apply(...)`: applies median blur defense.
- `denoise.py`
  - `class DenoiseDefense(Defense).apply(...)`: applies OpenCV NLM color denoise.

## `src/lab/models/`

- `yolo_model.py`
  - `class YOLOModel`
    - `__post_init__()`: loads Ultralytics model from `model_path`.
    - `predict(**kwargs)`: forwards to `YOLO.predict`.
    - `validate(**kwargs)`: forwards to `YOLO.val`.

## `src/lab/eval/`

- `metrics.py`
  - `_git_metadata()`: best-effort commit/branch lookup.
  - `_read_json(path)`: safe JSON reader.
  - `_find_label_files(run_dir)`: locate YOLO label text files.
  - `_parse_detection_stats(run_dir)`: aggregate detection counts and confidence stats.
  - `_read_val_metrics(run_dir)`: read precision/recall/mAP from metrics JSON.
  - `append_run_metrics(...)`: build and append CSV row for one run.

## `src/lab/runners/`

- `cli.py`
  - `main()`: argparse wrapper to run modular config with optional overrides.
- `experiment_registry.py`
  - `_parse_scalar(value)`: parse bool/none/int/float/string.
  - `parse_key_value_overrides(tokens)`: parse `key=value` CLI tokens.
  - `_prefixed(overrides, prefix)`: extract prefix-scoped override dict.
  - `_coerce_float_list(value)`: normalize scalar/list into float list.
  - `_merge_dict(base, extra)`: recursive dict merge.
  - `class ResolvedExperiment`: data container (`runner_config`, `summary`).
  - `class ExperimentRegistry`
    - `from_yaml(path)`: load registry config.
    - `resolve(overrides)`: resolve aliases + overrides into runnable config.
- `experiment_runner.py`
  - `class ExperimentSpec`: experiment declaration data model.
  - `class ExperimentRunner`
    - `from_yaml(config_path)`: load runner config from YAML.
    - `from_dict(config)`: construct validated runner from dict.
    - `_conf_token(conf)`: convert confidence to `NNN` token.
    - `_run_name_for(spec, conf)`: render `run_name_template`.
    - `_write_val_metrics(run_dir, validation_results)`: persist validation summary JSON.
    - `_prepare_source(spec, run_name)`: apply attack then defense into intermediate dirs.
    - `run()`: full execution loop and metrics append.

## Baseline/attack demo scripts

- `baseline/baseline_inference.py`
  - `main()`: quick single-image YOLO inference demo.
- `baseline/run_baseline.py`
  - `main()`: baseline experiment run.
- `attacks/run_confidence_attack.py`
  - `main()`: one blur attack experiment run.
- `attacks/confidence_supression.py`
  - `main()`: blur-kernel sweep and sample confidence prints.

## 8) How to extend the framework

## Add a new attack

1. Create file under `src/lab/attacks/`, subclass `Attack`, implement `apply`.
2. Decorate class with `@register_attack("new_name", "...aliases...")`.
3. Add alias entry to `configs/experiment_lab.yaml` under `attacks`.
4. Reference with `attack=new_name` in `run_experiment.py`.

## Add a new defense

1. Create file under `src/lab/defenses/`, subclass `Defense`, implement `apply`.
2. Decorate class with `@register_defense("new_name", "...aliases...")`.
3. Add alias entry under `defenses` in `configs/experiment_lab.yaml`.
4. Run with `defense=new_name`.

## Add a new dataset/model alias

- Add to `datasets:` or `models:` in `configs/experiment_lab.yaml`.
- Use via `dataset=<alias>` and `model=<alias>`.

## 9) Troubleshooting

- `ModuleNotFoundError: ultralytics`
  - Use `./.venv/bin/python ...` or install deps into your active interpreter.
- Empty/partial metrics
  - Ensure YOLO label outputs exist under run folder (`labels/*.txt` or `predict/labels/*.txt`).
- Validation metrics missing
  - Set `validate=true` in one-command flow, or `run_validation: true` in experiment spec.
- One-command alias `none` passed explicitly fails (for example `attack=none`)
  - Current parser converts `none` to null; rely on defaults by omitting the override.
- Unexpected run name
  - `run_name` automatically gets `_conf{conf_token}` suffix if not already present.

## 10) Recommended daily workflow for teammates

1. Activate/use `.venv`.
2. Start with dry-run:
   - `python3 run_experiment.py dry_run=true`
3. Run a small single-conf experiment:
   - `./.venv/bin/python run_experiment.py attack=blur conf=0.25`
4. Inspect:
   - run folder outputs
   - `metrics_summary.csv`
5. Iterate with parameter overrides (`attack.*`, `defense.*`, `imgsz`, `iou`, `seed`, `confs`).
