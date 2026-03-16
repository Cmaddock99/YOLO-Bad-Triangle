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
5. Run YOLO validation on those same final images to get quality metrics (precision/recall/mAP).
6. Append one row to `metrics_summary.csv`.
7. Plot results from that CSV.

## What gets saved

For each run, you get:

- Predictions and label text files in `outputs/<run_name>/...`
- Intermediate attacked/defended images in `outputs/_intermediates/<run_name>/...`
- Validation summary in `outputs/<run_name>/val/metrics.json`
- A CSV row in `outputs/metrics_summary.csv` (or `<custom_output_root>/metrics_summary.csv`)

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
   - `./.venv/bin/python run_experiment.py attack=blur conf=0.25`
   - `./.venv/bin/python scripts/plot_results.py --csv outputs/metrics_summary.csv`

## How to think about results

- If confidence stats change but validation metrics do not, the model is still robust.
- If both degrade, the attack is likely hurting real detection quality.
- If defense recovers validation metrics, the defense is helping.

That is the entire loop: change attack/defense, rerun, inspect CSV + plots, iterate.

For week1 demo artifact regeneration from one known output root, use:

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/week1_<timestamp>`

Current canonical fallback root for presentation:

- `outputs/demo-reference`
