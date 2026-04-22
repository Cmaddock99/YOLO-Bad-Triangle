# YOLO-Bad-Triangle

YOLO-Bad-Triangle is a modular adversarial-ML lab for YOLO object detection.
It is built to run repeatable attack and defense experiments, write structured
artifacts, and generate report-ready summaries that you can compare over time.

The repository is framework-first:

- Canonical single-run entrypoint: `scripts/run_unified.py run-one`
- Canonical sweep entrypoint: `scripts/run_unified.py sweep`
- Sweep compatibility backend: `scripts/sweep_and_report.py`
- Optional automation: `scripts/auto_cycle.py --loop`
- Canonical v1 profile: `yolo11n_lab_v1` in `configs/pipeline_profiles.yaml`

Effective layout:

- Core runtime: `scripts/run_unified.py run-one|sweep` with `scripts/sweep_and_report.py` as the compatibility backend
- Optional maintained workflow implementations: `scripts/automation/`, `scripts/training/`, `scripts/reporting/`, `scripts/demo/`
- Root `scripts/*.py` workflow entrypoints remain supported compatibility wrappers
- Old flat adapter paths under `lab.attacks`, `lab.defenses`, and `lab.models` remain supported compatibility shims
- `lab.reporting` umbrella imports remain compatibility-only; new code should prefer `lab.reporting.framework`, `lab.reporting.local`, or `lab.reporting.aggregate`

`YOLO-Bad-Triangle` is the only canonical runtime surface for the attack-defend-fortify
pipeline. The separate `Adversarial_Patch` repository is research/artifact input only;
it is not a second orchestrator and it is not required to execute the v1 pipeline.

This is now a single-maintainer project. Optimize ongoing cleanup for
reproducibility, local operability, and archive clarity. Preserve public CLI
and artifact names unless they are intentionally migrated; legacy names such as
`team_summary.*` remain supported compatibility surfaces.

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
[docs/FRESH_CLONE_SETUP.md](docs/FRESH_CLONE_SETUP.md) for the exact local
bootstrap path and expected local file layout.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

The supported local dev/test combo is Python 3.11+ (3.13 on NUC) with
`ultralytics==8.4.36`, `torch==2.6.0`, and `torchvision==0.21.0`. The canonical
v1 runtime profile is `yolo11n_lab_v1`, which resolves to `yolo11n.pt`,
`configs/coco_subset500.yaml`, and the canonical v1 attack/defense catalogs.

> **YOLOv8 Direction A complete.** Analysis results and verdict are archived in
> `docs/analysis/direction_a_closure_20260409.md`. The `dpc_unet_adversarial_finetuned.pt`
> checkpoint is YOLOv8-specific and should not be used for YOLOv11 training.

If you plan to run manual-only learned defenses such as `c_dog` or `c_dog_ensemble`,
set `DPC_UNET_CHECKPOINT_PATH`
in `.env` or your shell. This env var is the source of truth for which
DPC-UNet checkpoint is active:

```bash
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_adversarial_finetuned.pt
```

## Canonical workflow

### 1. Dry-run the canonical profile

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --profile yolo11n_lab_v1 \
  --dry-run
```

### 2. Run one smoke experiment

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --profile yolo11n_lab_v1 \
  --set attack.name=fgsm \
  --set runner.run_name=smoke_fgsm
```

### 3. Run a sweep

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep \
  --profile yolo11n_lab_v1 \
  --preset full \
  --workers 1 \
  --validation-enabled
```

If you omit `--attacks` and `--defenses` while using `--profile`, the sweep uses the
profile's canonical attack and defense catalogs automatically.

`--workers auto` uses `os.cpu_count()`, but each worker launches a full YOLO
job. On a single GPU or memory-constrained machine, `--workers 1` is usually
the safer choice.

### 4. List live plugin names

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep --list-plugins
```

### 5. Run the closed-loop cycle

```bash
PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py \
  --profile yolo11n_lab_v1 \
  --loop
```

Use the loop only after a smoke run and a regular sweep are working.

## Quality gates

```bash
./.venv/bin/python scripts/ci/run_repo_quality_gate.py --lane ci
./.venv/bin/python scripts/ci/run_repo_standards_audit.py --lane compat
```

`scripts/check_environment.py` remains a separate local-machine prerequisite
check; it is not part of CI parity yet.

Repository quality policy lives in `CODE_QUALITY_STANDARD.md`, and root
`AGENTS.md` provides the short drop-in contract for coding agents.

## Outputs

Single-run artifacts land in `outputs/framework_runs/<run_name>/`:

- `metrics.json`
- `predictions.jsonl`
- `run_summary.json`
- `resolved_config.yaml`
- `experiment_summary.json` when `summary.enabled=true`

Canonical v1 runs also stamp shared provenance into `run_summary.json` and `metrics.json`:

- `pipeline_profile`
- `authoritative_metric`
- `profile_compatibility`

Sweep and report artifacts land in `outputs/framework_reports/<sweep_id>/`:

- `framework_run_report.md`
- `framework_run_summary.csv`
- `team_summary.json`
- `team_summary.md`
- `dashboard.html`
- `summary_<attack>.txt` files

Authoritative canonical sweep outputs are the framework CSV/Markdown report
plus the local dashboard under the explicit report root. `team_summary.*`,
`failure_gallery.html`, and `outputs/dashboard.html` are optional extras.
Defaults still preserve the current behavior; the new CLI flags only make that
boundary explicit as extraction prep.

Cycle automation writes additional longitudinal artifacts such as:

- `outputs/cycle_history/*.json`
- `outputs/cycle_report.md`
- `outputs/cycle_report.csv`
- `outputs/dashboard.html` as a compatibility mirror of the latest generated dashboard

This repository intentionally versions selected historical report artifacts
under `outputs/` for trend tracking. Raw run directories, lock files, state
files, transfer bundles, and other local-only artifacts should not be tracked.

`lab.reporting` umbrella imports remain for compatibility only. New code should
import concrete reporting submodules directly.

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

Remaining root payload outside the core runtime is intentionally classified:

- Optional maintained workflows: root wrapper entrypoints for automation, training, reporting, and demo flows
- Manual utility: `scripts/check_environment.py`

## Canonical vs manual-only defenses

The registry includes more defenses than the canonical v1 profile.
For `yolo11n_lab_v1`:

- Canonical defenses: `bit_depth`, `jpeg_preprocess`, `median_preprocess`
- Manual-only defenses: `c_dog`, `c_dog_ensemble`, `confidence_filter`, `random_resize`

The v1 auto-cycle and ranked reports use only the canonical profile-approved set.

## Reporting note

When both authoritative Phase 4 rows and diagnostic smoke rows exist for the
same comparison, reporting and warning generation prefer the authoritative rows.
Diagnostic-only smoke sweeps still produce valid diagnostic summaries; they do
not by themselves imply that validation is missing.

For `yolo11n_lab_v1`, the authoritative metric remains `mAP50`. `mAP50-95`
is retained as diagnostic output only and a future pivot, not the v1 gate.

## Documentation

- `PROJECT_STATE.md` - current repo map and canonical paths
- `CODE_QUALITY_STANDARD.md` - repo quality bar, review rubric, and audit commands
- `docs/FRESH_CLONE_SETUP.md` - local machine bootstrap and asset checklist
- `docs/LOOP_DESIGN.md` - auto-cycle design and longitudinal workflow
- `docs/ATTACK_TEMPLATE.md` - adding a new attack
- `docs/DEFENSE_TEMPLATE.md` - adding a new defense
- `docs/LOCAL_CONFIG_POLICY.md` - local-vs-shared config rules
