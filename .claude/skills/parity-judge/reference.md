# parity-judge reference

## Core decision rule
- Parity is a migration confidence judgment, not a superficial metric diff.
- Comparability preconditions must pass before final parity status can be `pass` or `fail`.

## Comparability checklist
- Experiment intent is equivalent across legacy and framework runs.
- Evaluation scope is equivalent enough for metric comparison.
- Image counts and key config assumptions are compatible.
- Do not compare 50-image runs against 500-image runs without large tolerance or explicit `inconclusive` status.

## Observed mAP50 range (project context)

From cycle_20260329_125124 Phase 4 validation_results:
- Baseline (no attack): 0.600
- Deepfool (worst attack): 0.218
- Defended (deepfool+c_dog): 0.240

This range (~0.15–0.60) provides context for tolerance calibration:
- `map50: 0.02` — tight, appropriate for comparing full-dataset runs of the same attack config
- `map50: 0.05` — loose, appropriate when comparing smoke runs to partial-dataset runs
- Comparing 50-image to 500-image runs: use `inconclusive` unless tolerance is explicitly widened with justification

## Status semantics
- `pass`: comparable and all required deltas are within tolerance.
- `fail`: comparable and one or more required deltas violate tolerance.
- `inconclusive`: comparability or evidence requirements are not satisfied.

## Mismatch categories
- `missing_file`
- `schema_shape`
- `count_mismatch`
- `config_mismatch`

## Notes
- Keep this skill strict and read-only.
- Do not infer mismatch causes without direct evidence from artifact content.
- Checkpoint differences (golden vs finetuned) are a `config_mismatch` if both runs did not use the same `DPC_UNET_CHECKPOINT_PATH`.
