# The Pipeline in Plain English

This file explains how this project works without heavy jargon.

## Big picture

You are testing this question:

**"How much do different attacks hurt YOLO, and how much do defenses help recover performance?"**

Each experiment run does the same sequence:

1. Start from a folder of source images.
2. Apply an attack (or do nothing).
3. Apply a defense (or do nothing).
4. Run YOLO prediction on the final images.
5. Run YOLO validation to get quality metrics (precision/recall/mAP).
6. Append one row to `metrics_summary.csv`.
7. Plot results from that CSV.

## What gets saved

For each run, you get:

- Predictions and label text files in `results/<run_name>/...`
- Intermediate attacked/defended images in `results/_intermediates/<run_name>/...`
- Validation summary in `results/<run_name>/val/metrics.json`
- A CSV row in `results/metrics_summary.csv`

## Why two types of metrics exist

The CSV has two metric groups:

- **Confidence stats** (`avg_conf`, `median_conf`, `p25_conf`, `p75_conf`):
  - Computed from prediction label files.
  - Tell you how confident detections were.

- **Validation quality stats** (`precision`, `recall`, `mAP50`, `mAP50-95`):
  - Computed from YOLO validation output.
  - Tell you true detection quality against labels.

If validation is missing or disabled, those final four fields can be empty.

## Where to edit behavior

- Add new attacks in `src/lab/attacks/`
- Add new defenses in `src/lab/defenses/`
- Experiment orchestration is in `src/lab/runners/experiment_runner.py`
- CSV writing is in `src/lab/eval/metrics.py`
- Plotting is in `scripts/plot_results.py`

## Typical "add a new method" workflow

1. Copy the attack or defense template file in this repo.
2. Create your module under `src/lab/attacks/` or `src/lab/defenses/`.
3. Register it with `@register_attack(...)` or `@register_defense(...)`.
4. Reference it in experiment YAML via `attack`/`defense` and params.
5. Run:
   - `source .venv/bin/activate`
   - `python scripts/run_experiment.py`
   - `tail -n 1 results/metrics_summary.csv`
   - `python scripts/plot_results.py`

## How to think about results

- If confidence stats change but validation metrics do not, the model is still robust.
- If both degrade, the attack is likely hurting real detection quality.
- If defense recovers validation metrics, the defense is helping.

That is the entire loop: change attack/defense, rerun, inspect CSV + plots, iterate.
