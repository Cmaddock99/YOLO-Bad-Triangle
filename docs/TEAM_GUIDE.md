# Team Guide (Beginner + Technical): YOLO Robustness Experiment Lab

This document is written for both:
- people new to ML/engineering workflows, and
- engineers who need implementation details.

If you only read one section, read **Section 3: 10-minute Quick Start**.

For live team presentation flow, use `docs/WEEK1_DEMO_RUNBOOK.md`.

## Templates for new modules

Use these starter docs when creating new components:

- `docs/ATTACK_TEMPLATE.md`: step-by-step template for adding a new attack module.
- `docs/DEFENSE_TEMPLATE.md`: step-by-step template for adding a new defense module.
- `docs/PIPELINE_IN_PLAIN_ENGLISH.md`: plain-language walkthrough of the full experiment flow.

## 1) What this project does (plain English)

This project helps you answer:

**“How does YOLO object detection performance change when images are attacked and then optionally defended?”**

In each run, the framework:
1. chooses a model + dataset + settings,
2. optionally distorts images with an **attack**,
3. optionally cleans images with a **defense**,
4. runs YOLO prediction (and optional validation),
5. writes results and summary metrics.

Core code lives in `src/lab`.

## 2) Key terms (quick glossary)

- **Model**: the YOLO weights file (default: `yolov8n.pt`).
- **Dataset**: images + labels config (default points to COCO subset).
- **Attack**: a transformation that makes images harder (blur, noise, deepfool-like).
- **Defense**: a preprocessing step intended to recover signal (median blur, denoise).
- **Confidence threshold (`conf`)**: minimum score for predicted boxes.
- **IoU threshold (`iou`)**: overlap threshold used in NMS/evaluation logic.
- **Validation**: optional mAP/precision/recall scoring pass.
- **Run**: one full experiment execution with one configuration.

## 3) 10-minute quick start (recommended path)

## Step 0: Use the project environment

Use the repo virtual environment to avoid missing package issues:

- `./.venv/bin/python --version`
- `./.venv/bin/pip install -r requirements.txt` (if needed)

## Step 1: Verify configuration without heavy compute

Dry run resolves config only:

- `./.venv/bin/python run_experiment.py dry_run=true`

You should see a resolved summary and runner config.

## Step 2: Run a small test experiment

- `./.venv/bin/python run_experiment.py attack=blur conf=0.25`

## Step 3: Check outputs

Look at:
- output run folder under `outputs/<run_name>/...`
- `metrics_summary.csv` in that output root
- `val/metrics.json` if validation was enabled

That is enough to prove your environment and workflow are working.

## 4) Which command should I use?

Use this table:

- **I want the simplest command**  
  Use: `run_experiment.py`

- **I want to run a predefined multi-experiment YAML**  
  Use: `scripts/run_framework.py --config <yaml>`

- **I need explicit CLI args from another script/tool**  
  Use: `run_experiment_api.py`

- **I already ran inference and only want to append metrics**  
  Use: this is automatic in `run_experiment.py`/`scripts/run_framework.py`; no separate collector step is required.

## 5) Typical usage examples

## A) One-command run (best default)

- `./.venv/bin/python run_experiment.py attack=deepfool defense=denoise conf=0.25,0.5`

Useful overrides:
- `model=yolo11 dataset=coco_subset`
- `attack.kernel_size=11`
- `defense.h=12`
- `iou=0.7 imgsz=640 seed=42`
- `validate=true`
- `output_root=outputs/custom`

## B) Modular YAML runner

- `./.venv/bin/python scripts/run_framework.py --config configs/modular_experiments.yaml`
- `./.venv/bin/python scripts/run_framework.py --config configs/modular_experiments.yaml --confs 0.25,0.5 --output_root outputs/custom`

## C) API wrappers

- `./.venv/bin/python run_experiment_api.py --help`
- `./.venv/bin/python run_experiment_api.py --list-attacks`

## D) FGSM epsilon sweep (recommended)

Use FGSM with a fixed seed and compare against `attack=none`:

- Baseline:
  - `./.venv/bin/python run_experiment.py conf=0.25 seed=42 run_name=baseline_fgsm_ref`
- FGSM examples:
  - `./.venv/bin/python run_experiment.py attack=fgsm attack.epsilon=0.002 conf=0.25 seed=42 run_name=fgsm_e002`
  - `./.venv/bin/python run_experiment.py attack=fgsm attack.epsilon=0.004 conf=0.25 seed=42 run_name=fgsm_e004`
  - `./.venv/bin/python run_experiment.py attack=fgsm attack.epsilon=0.008 conf=0.25 seed=42 run_name=fgsm_e008`
  - `./.venv/bin/python run_experiment.py attack=fgsm attack.epsilon=0.016 conf=0.25 seed=42 run_name=fgsm_e016`

## E) Week1 rerun and verify (single command)

Use the canonical week1 matrix runner to produce a fresh, timestamped output root:

- `./scripts/run_week1_stabilization.sh --profile week1-demo --mode demo`

What this does:

1. runs baseline + FGSM (`0.0005`, `0.006`, `0.01`) from `configs/week1_stabilization_demo_matrix.yaml`,
2. writes outputs to `outputs/week1_<UTC timestamp>/`,
3. validates metrics integrity with `scripts/check_metrics_integrity.py`,
4. checks FGSM sanity (`warn+continue` in `--mode demo`, `fail` in `--mode strict`),
5. generates `experiment_table.md` and all week1 plots in that same output root.

Current canonical fallback demo root:

- `outputs/demo-reference`

## 6) What happens inside one run?

Pipeline:

`CLI/YAML settings -> registry resolution -> runner build -> attack apply -> defense apply -> YOLO predict/validate -> metrics append`

More detail:
1. `ExperimentRegistry` resolves aliases and merges overrides.
2. `ExperimentRunner` creates a run name and output paths.
3. Attack module transforms source images (or passes through).
4. Defense module transforms attacked images (or passes through).
5. `YOLOModel` runs prediction and optional validation.
6. `append_run_metrics` parses labels/metrics and appends a CSV row.

## 7) Output files and how to read them

Common outputs:
- `output_root/<run_name>/...` (prediction outputs)
- `output_root/_intermediates/<run_name>/attacked/...`
- `output_root/_intermediates/<run_name>/defended/...`
- `output_root/metrics_summary.csv` (one row per run)
- `output_root/<run_name>/val/metrics.json` (if validation is on)

In `metrics_summary.csv`, important columns include:
- `attack`, `defense`, `conf`, `iou`, `imgsz`, `seed`
- `images_with_detections`, `total_detections`
- `avg_conf`, `median_conf`, `p25_conf`, `p75_conf`
- `precision`, `recall`, `mAP50`, `mAP50-95`

## 8) Project layout (quick map)

- `src/lab/attacks`: attack interface + attack implementations
- `src/lab/defenses`: defense interface + defense implementations
- `src/lab/models`: YOLO wrapper
- `src/lab/runners`: registry + experiment orchestration
- `src/lab/eval`: metrics parsing/writing
- `configs/`: dataset and experiment YAMLs
- `scripts/`: helper CLIs
- root scripts: `run_experiment.py`, `run_experiment_api.py`

### Canonical entrypoints (authoritative)

- `run_experiment.py`: easiest one-command operator flow with `key=value` overrides.
- `run_experiment_api.py`: explicit-arg one-run wrapper for script/tool integrations.
- `scripts/run_framework.py`: YAML batch runner backed by `src/lab/runners/cli.py`.
- `scripts/demo/run_demo_package.sh`: demo/rehearsal orchestration (preflight, live run, artifacts, gates, summary).

Where to add new modules:
- attacks: `src/lab/attacks/` (+ registration in `configs/experiment_lab.yaml`)
- defenses: `src/lab/defenses/` (+ registration in `configs/experiment_lab.yaml`)

## 9) Known gotchas (important)

- If you see `ModuleNotFoundError: ultralytics`, use `./.venv/bin/python ...`.
- `attack=none` and `defense=none` are valid explicit values in `run_experiment.py`.
- Missing/empty metrics usually means no label files were produced in the run output.
- Validation metrics only appear when validation is enabled (`validate=true` or `run_validation: true`).

## 10) How to extend the framework (developer notes)

## Add a new attack

1. Create a class in `src/lab/attacks/` that subclasses `Attack`.
2. Implement `apply(source_dir, output_dir, seed=...)`.
3. Register it with `@register_attack("your_name", "alias2")`.
4. Add alias/config defaults in `configs/experiment_lab.yaml` under `attacks`.
5. Run with `attack=your_name`.

## Add a new defense

1. Create a class in `src/lab/defenses/` that subclasses `Defense`.
2. Implement `apply(source_dir, output_dir, seed=...)`.
3. Register it with `@register_defense("your_name", "alias2")`.
4. Add alias/config defaults in `configs/experiment_lab.yaml` under `defenses`.
5. Run with `defense=your_name`.

## Add a new model/dataset alias

Edit `configs/experiment_lab.yaml`:
- add entry under `models` or `datasets`,
- then call it using `model=<alias>` or `dataset=<alias>`.

## 11) Full function and class reference (current code)

This is the full callable index as of now.

## Root scripts

- `run_experiment.py`
  - `main()`: parse key/value overrides, resolve aliases, optionally dry-run, run experiments.
- `run_experiment_api.py`
  - `main()`: explicit CLI wrapper that builds a one-experiment config.

## `scripts/`

- `scripts/run_framework.py`
  - no top-level function (imports and runs `lab.runners.cli.main`).
- `scripts/convert_coco_to_yolo.py`
  - script-style converter (no function) from COCO JSON boxes to YOLO labels.

## `src/lab/attacks/`

- `base.py`
  - `class Attack`: abstract `apply(...)`.
  - `register_attack(*names)`: registry decorator.
  - `get_attack_class(name)`: lookup by key.
  - `list_registered_attacks()`: list keys.
- `registry.py`
  - `_load_builtin_attacks()`: lazy-load modules to register implementations.
  - `build_attack(name, params=None)`: construct attack instance.
- `utils.py`
  - `iter_images(source_dir)`: recursively yield supported image files.
- `none.py`
  - `class NoAttack(Attack).apply(...)`: identity pass-through.
- `blur.py`
  - `class GaussianBlurAttack(Attack)`
    - `__post_init__()`: validates kernel.
    - `apply(...)`: Gaussian blur transform.
- `noise.py`
  - `class GaussianNoiseAttack(Attack).apply(...)`: Gaussian noise transform.
- `deepfool.py`
  - `class DeepFoolAttack(Attack)`
    - `__post_init__()`: validates epsilon/steps.
    - `apply(...)`: iterative gradient-style perturbation approximation.

## `src/lab/defenses/`

- `base.py`
  - `class Defense`: abstract `apply(...)`.
  - `register_defense(*names)`: registry decorator.
  - `get_defense_class(name)`: lookup by key.
  - `list_registered_defenses()`: list keys.
- `registry.py`
  - `_load_builtin_defenses()`: lazy-load defense modules.
  - `build_defense(name, params=None)`: construct defense instance.
- `none.py`
  - `class NoDefense(Defense).apply(...)`: identity pass-through.
- `median_blur.py`
  - `class MedianBlurDefense(Defense)`
    - `__post_init__()`: validates kernel.
    - `apply(...)`: median blur defense.
- `denoise.py`
  - `class DenoiseDefense(Defense).apply(...)`: OpenCV NLM denoise defense.

## `src/lab/models/`

- `yolo_model.py`
  - `class YOLOModel`
    - `__post_init__()`: loads Ultralytics model.
    - `predict(**kwargs)`: runs prediction.
    - `validate(**kwargs)`: runs validation.

## `src/lab/eval/`

- `metrics.py`
  - `_git_metadata()`: reads git commit/branch metadata.
  - `_read_json(path)`: safe JSON load.
  - `_find_label_files(run_dir)`: locate YOLO label text files.
  - `_parse_detection_stats(run_dir)`: compute detection count/confidence stats.
  - `_read_val_metrics(run_dir)`: parse validation metrics JSON.
  - `append_run_metrics(...)`: append run metrics row to CSV.

## `src/lab/runners/`

- `cli.py`
  - `main()`: argparse entrypoint for modular YAML runs.
- `experiment_registry.py`
  - `_parse_scalar(value)`: scalar parser for CLI tokens.
  - `parse_key_value_overrides(tokens)`: parse `key=value` tokens.
  - `_prefixed(overrides, prefix)`: extract namespaced overrides.
  - `_coerce_float_list(value)`: normalize to float list.
  - `_merge_dict(base, extra)`: recursive merge utility.
  - `class ResolvedExperiment`: container with `runner_config` and summary.
  - `class ExperimentRegistry`
    - `from_yaml(path)`: load alias config.
    - `resolve(overrides)`: produce executable runner config.
- `experiment_runner.py`
  - `class ExperimentSpec`: per-experiment spec object.
  - `class ExperimentRunner`
    - `from_yaml(config_path)`: build runner from YAML.
    - `from_dict(config)`: build runner from dict.
    - `_conf_token(conf)`: convert confidence to short token.
    - `_run_name_for(spec, conf)`: render run name template.
    - `_write_val_metrics(run_dir, validation_results)`: write validation summary.
    - `_prepare_source(spec, run_name)`: run attack+defense preprocessing.
    - `run()`: execute all configured runs and append metrics.

## 12) Recommended team workflow

1. Use `.venv`.
2. Run `./.venv/bin/python run_experiment.py dry_run=true`.
3. Run a small experiment (`attack=blur conf=0.25`).
4. Review `metrics_summary.csv`.
5. Iterate on attack/defense and thresholds.
