# Stage 2 Cleanup Report

Date: 2026-03-18

## Scope

Executed Stage 2 cleanup after soak validation evidence from:

- framework stability matrix (`docs/STABILITY_MATRIX_REPORT.md`)
- framework coverage proof (`docs/FRAMEWORK_COVERAGE_PROOF.md`)
- full regression pass

## Obsolete Internals Removed

- `src/lab/runners/phase3_compat_runner.py`
- `configs/lab_framework_phase3_compat.yaml`
- `configs/lab_framework_skeleton.yaml`

Rationale: these were migration scaffolding artifacts from earlier phases and no longer part of canonical operation.

## Safety Validation After Deletion

- Framework smoke run:
  - `src/lab/runners/run_experiment.py` completed successfully after cleanup.
- Full regression:
  - `python -m unittest discover -s tests -p "test_*.py"` passed (`42` tests).
- Diagnostics:
  - No linter issues on changed files.

## Canonical Operational Path

Framework-first command:

- `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --config configs/default.yaml`

Compatibility entrypoints (`run_experiment.py`, `run_experiment_api.py`, `scripts/run_framework.py`) remain available but now emit deprecation notices.

## Decision

Stage 2 cleanup status: **PASS**

## Soak Batch Update

Framework-only soak runs executed under `outputs/soak_framework`:

- `soak_baseline` (`attack=none`, `defense=none`)
- `soak_pgd` (`attack=pgd`, `defense=none`)
- `soak_deepfool_preprocess_median` (`attack=deepfool`, `defense=preprocess_median_blur`)
- Existing soak run retained: `soak_fgsm_conf_filter` (`attack=fgsm`, `defense=confidence_filter`)

Observed invariants for the three new runs:

- `input_image_count=12` and `processed_image_count=12`
- `failed_image_writes=0`
- `skipped_unreadable_images=0`
- Required framework artifacts present for each run:
  - `predictions.jsonl`
  - `metrics.json`
  - `run_summary.json`
  - `resolved_config.yaml`

Generated soak report artifacts:

- `outputs/soak_framework/report/framework_run_summary.csv`
- `outputs/soak_framework/report/framework_run_report.md`
