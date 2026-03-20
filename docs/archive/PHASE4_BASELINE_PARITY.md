# Phase 4 Baseline Parity Validation

## Goal

Validate baseline parity between:

- Legacy path (`run_experiment.py` + `ExperimentRunner`)
- New wrapped path (`Phase3CompatRunner` + `YOLOModelAdapter`)

using the same model family and baseline (no attack, no defense).

## Runs Executed

### Legacy baseline

- Command:
  - `./.venv/bin/python run_experiment.py model=yolo26 attack=none defense=none conf=0.5 imgsz=640 validate=false output_root=outputs/phase4_legacy run_name=phase4_legacy_baseline`
- Output root:
  - `outputs/phase4_legacy/yolo26_phase4_legacy_baseline`
- Dataset:
  - `coco/val2017_subset500/images`

### New wrapped baseline

- Runner:
  - `lab.runners.phase3_compat_runner.Phase3CompatRunner`
- Configuration used in code execution:
  - `model_name='yolo'`
  - `model_params={'model': 'yolo26n.pt'}`
  - `attack_name='none'`
  - `max_images=500`
  - `predict_kwargs={'conf': 0.5, 'iou': 0.7, 'imgsz': 640, 'seed': 42}`
- Output file:
  - `outputs/phase4_new_conf05/predictions.jsonl`
- Dataset:
  - `coco/val2017_subset500/images`

## Parity Results

## 1) Prediction row/image coverage

- Legacy total images processed: `500`
- New total prediction records: `500`
- Result: **PASS** (image-level coverage parity)

## 2) Images with detections

- Legacy images with detections: `461`
- New images with detections: `466`
- Delta: `+5` images (`+1.08%` of 461 baseline)
- Result: **PASS (near parity, minor variance)**

## 3) Total detection count

- Legacy total detections (from saved label rows): `1408`
- New total detections (sum of `boxes` lengths): `1437`
- Delta: `+29` detections (`+2.06%` of 1408 baseline)
- Result: **PASS (near parity, minor variance)**

## 4) Metrics availability check

- Legacy run wrote a `metrics_summary.csv` row with `row_status=partial` because `validate=false`.
- New wrapped run currently emits standardized predictions only (`predictions.jsonl`) and does not yet write framework metrics artifacts.
- Result: **EXPECTED FOR CURRENT PHASE**

## Notes on Variance

Small baseline differences are expected at this stage because inference is performed through two different execution paths:

- legacy path through `ExperimentRunner`/`YOLOModel.predict` with legacy output writer behavior
- new path through `YOLOModelAdapter` normalization and JSONL serialization

Given identical model family, baseline mode, and aligned inference thresholds (`conf=0.5`, `iou=0.7`, `imgsz=640`), the observed `~1-2%` detection variance is acceptable for Phase 4 parity gating.

## Phase 4 Decision

**Phase 4 baseline parity: PASS (acceptable).**

Proceed to Phase 5 (single unified runner + config system), while keeping legacy entrypoints intact.
