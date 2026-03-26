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

- `outputs/framework_runs/<run_name>/metrics.json` — detection counts, avg confidence, mAP50
- `outputs/framework_runs/<run_name>/predictions.jsonl` — per-image predictions
- `outputs/framework_runs/<run_name>/run_summary.json` — run metadata (attack, defense, config)

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

- Add new attacks in `src/lab/attacks/` (follow `docs/ATTACK_TEMPLATE.md`)
- Add new defenses in `src/lab/defenses/` (follow `docs/DEFENSE_TEMPLATE.md`)
- Experiment orchestration is in `src/lab/runners/run_experiment.py`
- Metrics parsing is in `src/lab/eval/`
- Report generation is in `src/lab/reporting/`

## Typical "add a new method" workflow

1. Copy the attack or defense template file in this repo.
2. Create your module under `src/lab/attacks/` or `src/lab/defenses/`.
3. Register it with `@register_attack_plugin(...)` or `@register_defense_plugin(...)`.
4. Reference it with `--set attack.name=your_name` or `--set defense.name=your_name`.
5. Run a smoke test:
   ```bash
   PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
     --config configs/default.yaml \
     --set attack.name=your_name \
     --set runner.max_images=4
   ```

## How to think about results

- If confidence stats change but mAP50 does not, the model is still robust.
- If both degrade, the attack is hurting real detection quality.
- If defense recovers mAP50, the defense is helping.

That is the entire loop: change attack/defense, rerun, inspect outputs, iterate. For
automated iterative cycles with warm-start and training feedback, see `docs/LOOP_DESIGN.md`.
