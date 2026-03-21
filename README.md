# YOLO-Bad-Triangle

Adversarial robustness experimentation framework for YOLO object detection. Run attacks, apply defenses, and measure recovery — all from a single sweep command.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

## Quickstart

**Smoke test (8 images):**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=smoke_fgsm
```

**Full sweep with parallel workers:**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool \
  --defenses c_dog,median_preprocess \
  --preset full \
  --workers auto \
  --validation-enabled
```

**See all available attacks and defenses:**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

**Run tests:**
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

## Sweep flags

| Flag | Description |
|---|---|
| `--attacks all` | Every registered attack plugin |
| `--defenses all` | Every registered defense plugin |
| `--workers N` / `--workers auto` | Parallel experiments |
| `--preset smoke` / `--preset full` | 8 images vs all 500 |
| `--validation-enabled` | Compute mAP50 after each run |
| `--resume` | Skip runs that already completed |
| `--skip-errors` | Continue on failure, report at end |

`--workers auto` picks `os.cpu_count()` parallel subprocesses. Each worker runs a full YOLO job; on **one GPU** that often reduces throughput or causes OOM, so use `--workers 1` unless you have enough devices or CPU-only runs.

## Outputs

Each run writes to `outputs/framework_runs/<run_name>/`:

```
metrics.json        # mAP50, avg confidence, detection counts
predictions.jsonl   # per-image predictions
run_summary.json    # run metadata (attack, defense, model, config)
```

Reports land in `outputs/framework_reports/<sweep_id>/`:

```
framework_run_report.md     # attack effectiveness + defense recovery table
framework_run_summary.csv   # same data as CSV
team_summary.json / .md     # high-level summary
```

## Attacks

| Name | Type |
|---|---|
| `fgsm` | Gradient — fast, single-step |
| `pgd` / `bim` / `ifgsm` | Gradient — iterative, stronger |
| `deepfool` | Gradient — minimal-perturbation |
| `blur` / `gaussian_blur` | Non-gradient — image degradation |

## Defenses

| Name | Description |
|---|---|
| `median_preprocess` | Median blur — fast, removes pixel-level noise |
| `c_dog` | DPC-UNet neural denoiser — strong against structured attacks |
| `c_dog_ensemble` | Median blur → DPC-UNet → sharpening — strongest overall |
| `confidence_filter` | Drop detections below a confidence threshold |

`c_dog` and `c_dog_ensemble` require a checkpoint. Set once in `.env` (already configured):
```bash
DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt
```

## Architecture

```
scripts/run_unified.py          ← canonical entry point
scripts/sweep_and_report.py     ← sweep orchestrator
  └── src/lab/runners/run_experiment.py  ← UnifiedExperimentRunner
        ├── attack plugin       (src/lab/attacks/)
        ├── defense plugin      (src/lab/defenses/)
        ├── YOLO model          (src/lab/models/)
        └── eval + reporting    (src/lab/eval/, src/lab/reporting/)
```

Config: `configs/default.yaml`. Override anything with `--set key=value` (dotted paths).

## Colab (GPU)

Open `colab_sweep.ipynb` in Google Colab, switch runtime to T4 GPU, then run all cells. Downloads repo, dataset, and weights automatically. Before committing notebook changes from Colab, clear outputs (or strip cells) so git diffs stay small.

## Docs

- `docs/PIPELINE_IN_PLAIN_ENGLISH.md` — how it all fits together
- `docs/ATTACK_TEMPLATE.md` — adding a new attack
- `docs/DEFENSE_TEMPLATE.md` — adding a new defense
- `docs/TEAM_GUIDE.md` — onboarding guide
