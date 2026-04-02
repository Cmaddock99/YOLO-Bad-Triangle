# The Pipeline in Plain English

This file explains the current experiment flow without heavy jargon.

## Big picture

The lab is trying to answer a simple question:

**How much does YOLO performance change under different attacks, and what happens when we add a defense?**

## What one run does

A single run currently goes through these steps:

1. Start from a folder of images.
2. Optionally apply an attack.
3. Optionally preprocess the attacked image with a defense.
4. Run YOLO prediction on the resulting image.
5. Optionally run validation to get mAP, precision, and recall.
6. Write structured output files for analysis.

The current implementation order is:

`attack.apply -> defense.preprocess -> model.predict -> defense.postprocess`

That means the repo's current "defended" runs really are "apply the attack, then
measure whether the defense recovers some of the loss." Run artifacts also
store a plain-English marker: `semantic_order=attack_then_defense`.

## What gets saved

For each run:

- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/run_summary.json`
- `outputs/framework_runs/<run_name>/resolved_config.yaml`

For each sweep:

- `outputs/framework_reports/<sweep_id>/framework_run_report.md`
- `outputs/framework_reports/<sweep_id>/framework_run_summary.csv`
- `outputs/framework_reports/<sweep_id>/team_summary.json`
- `outputs/framework_reports/<sweep_id>/team_summary.md`

## Why there are two metric families

### Prediction metrics

These come from the predictions themselves:

- image count
- images with detections
- total detections
- average confidence

They are fast and useful for smoke runs and tuning loops.

### Validation metrics

These come from a validation pass against labels:

- precision
- recall
- mAP50
- mAP50-95

These are the stronger numbers for final comparison.

## Where to change behavior

- Add attacks in `src/lab/attacks/`
- Add defenses in `src/lab/defenses/`
- Change run orchestration in `src/lab/runners/run_experiment.py`
- Change reporting in `src/lab/reporting/`
- Change validation and metric logic in `src/lab/eval/`

## Typical workflow

1. Dry-run a config.
2. Run one smoke experiment.
3. Run a sweep.
4. Read the report artifacts.
5. If needed, use `scripts/auto_cycle.py --loop` for iterative tuning.

That is the current loop. The canonical commands are documented in the root
`README.md`.
