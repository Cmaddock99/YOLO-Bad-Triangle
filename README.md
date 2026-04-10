# YOLO-Bad-Triangle

YOLO-Bad-Triangle is a modular adversarial-ML lab for YOLO object detection.
It is built to run repeatable attack and defense experiments, write structured
artifacts, and generate report-ready summaries that a teammate can compare over
time.

The repository is framework-first:

- Canonical single-run entrypoint: `scripts/run_unified.py run-one`
- Canonical sweep entrypoint: `scripts/sweep_and_report.py`
- Closed-loop automation: `scripts/auto_cycle.py --loop`

## What the project does

Each run uses a config-driven pipeline to:

1. load a YOLO model and dataset,
2. optionally apply an attack,
3. optionally apply a defense preprocessing stage,
4. run prediction and optional validation,
5. write structured outputs for analysis and reporting.

The current runner records this exact transform order in every run artifact:

`attack.apply -> defense.preprocess -> model.predict -> defense.postprocess`

Run artifacts also record `semantic_order=attack_then_defense` so reporting can
distinguish this canonical era from older legacy outputs.

## Setup

Fresh-clone note: the repo intentionally does not track local model weights,
COCO images, label folders, or your `.env`. Use
[docs/FRESH_CLONE_SETUP.md](docs/FRESH_CLONE_SETUP.md) for the exact teammate
bootstrap path and expected local file layout.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

The supported local dev/test combo is Python 3.11+ (3.13 on NUC) with
`ultralytics==8.4.36`, `torch==2.6.0`, and `torchvision==0.21.0`. **The project is
transitioning to YOLOv11** — see `PROJECT_STATE.md` for current phase status. No new
model adapter is needed; set `model.params.model: yolo11n.pt` in config and ultralytics
auto-downloads the weights on first run.

> **YOLOv8 Direction A complete.** Analysis results and verdict are archived in
> `docs/analysis/direction_a_closure_20260409.md`. The `dpc_unet_adversarial_finetuned.pt`
> checkpoint is YOLOv8-specific and should not be used for YOLOv11 training.

If you plan to use `c_dog` or `c_dog_ensemble`, set `DPC_UNET_CHECKPOINT_PATH`
in `.env` or your shell. This env var is the source of truth for which
DPC-UNet checkpoint is active:

```bash
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_adversarial_finetuned.pt
```

## Canonical workflow

### 1. Dry-run the config

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --dry-run
```

### 2. Run one smoke experiment

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=smoke_fgsm
```

### 3. Run a sweep

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool \
  --defenses c_dog,median_preprocess \
  --preset full \
  --workers 1 \
  --validation-enabled
```

`--workers auto` uses `os.cpu_count()`, but each worker launches a full YOLO
job. On a single GPU or memory-constrained machine, `--workers 1` is usually
the safer choice.

### 4. List live plugin names

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

### 5. Run the closed-loop cycle

```bash
PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --loop
```

Use the loop only after a smoke run and a regular sweep are working.

## Quality gates

```bash
./.venv/bin/ruff check src tests scripts
./.venv/bin/mypy
./.venv/bin/pytest -q
```

## Outputs

Single-run artifacts land in `outputs/framework_runs/<run_name>/`:

- `metrics.json`
- `predictions.jsonl`
- `run_summary.json`
- `resolved_config.yaml`
- `experiment_summary.json` when `summary.enabled=true`

Sweep and report artifacts land in `outputs/framework_reports/<sweep_id>/`:

- `framework_run_report.md`
- `framework_run_summary.csv`
- `team_summary.json`
- `team_summary.md`
- `summary_<attack>.txt` files

Cycle automation writes additional longitudinal artifacts such as:

- `outputs/cycle_history/*.json`
- `outputs/cycle_report.md`
- `outputs/cycle_report.csv`
- `outputs/dashboard.html`

This repository intentionally versions selected historical report artifacts
under `outputs/` for trend tracking. Raw run directories, lock files, state
files, transfer bundles, and other local-only artifacts should not be tracked.

## Project map

- `src/lab/runners/` - core runner and CLI helpers
- `src/lab/attacks/` - registered attack plugins
- `src/lab/defenses/` - registered defense plugins
- `src/lab/models/` - model adapters
- `src/lab/eval/` - prediction and validation metrics
- `src/lab/reporting/` - comparison, summaries, warnings
- `src/lab/health_checks/` - artifact and schema validation helpers
- `configs/` - shared YAML configs
- `schemas/v1/` - JSON schemas for structured artifacts
- `scripts/` - user-facing orchestration and reporting scripts
- `tests/` - unit and integration coverage

## Registered vs active defenses

The plugin registry includes `c_dog_ensemble`, but the current auto-cycle
catalog excludes it. The active auto-cycle defense set is narrower than the full
registered defense list by design.

## Reporting note

When both authoritative Phase 4 rows and diagnostic smoke rows exist for the
same comparison, reporting and warning generation prefer the authoritative rows.
Diagnostic-only smoke sweeps still produce valid diagnostic summaries; they do
not by themselves imply that validation is missing.

## Documentation

- `PROJECT_STATE.md` - current repo map and canonical paths
- `docs/TEAM_GUIDE.md` - teammate onboarding guide
- `docs/PIPELINE_IN_PLAIN_ENGLISH.md` - plain-language walkthrough
- `docs/LOOP_DESIGN.md` - auto-cycle design and longitudinal workflow
- `docs/ATTACK_TEMPLATE.md` - adding a new attack
- `docs/DEFENSE_TEMPLATE.md` - adding a new defense
- `docs/LOCAL_CONFIG_POLICY.md` - local-vs-shared config rules
