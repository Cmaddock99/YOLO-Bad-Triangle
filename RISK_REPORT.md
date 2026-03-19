# RISK_REPORT.md

## Purpose

This report identifies refactor risks for the current adversarial ML pipeline and classifies each area using the required migration tags.

## Risk Matrix (By Area)

| Area | Current Files | Risk | Why It Matters | Migration Guidance |
|---|---|---|---|---|
| Legacy week1/demo operator flow | `scripts/run_week1_stabilization.sh`, `scripts/demo/run_demo_package.sh`, `scripts/generate_week1_demo_artifacts.sh` | 🔥 DO NOT TOUCH | This is the team-facing operational/demo path; changing behavior here can break reproducible demo execution and artifacts. | Keep behavior and command surface stable until full parity is validated on new runner. |
| Legacy core runner | `src/lab/runners/experiment_runner.py` | 🔥 DO NOT TOUCH | Central production pipeline with attack/defense transforms, validation dataset prep, predict/validate orchestration, and CSV metrics append. | Wrap and mirror behavior first; avoid invasive rewrites before side-by-side parity passes. |
| Legacy metrics CSV contract | `src/lab/eval/metrics.py`, `outputs/metrics_summary.csv` schema consumers | 🔥 DO NOT TOUCH | Existing scripts/checks/docs assume specific CSV fields and status semantics. | Preserve CSV generation while introducing parallel JSON metrics in framework path. |
| Multiple runner entrypoints | `run_experiment.py`, `run_experiment_api.py`, `scripts/run_framework.py`, `src/lab/runners/run_experiment.py` | ⚠️ FRAGILE | Overlapping CLIs can drift and produce different defaults/semantics. | Introduce single canonical runner gradually; keep compatibility wrappers. |
| Dual config schemas | `configs/experiment_lab.yaml` + matrix configs vs `configs/lab_framework_phase5.yaml` | ⚠️ FRAGILE | Semantically similar concepts but incompatible structure (`data.image_dir` vs `data.source_dir`, etc.). | Define strict schema boundary and migration bridge; never mix command/schema families. |
| Framework plugin bootstrap imports | `src/lab/models/registry.py`, `src/lab/attacks/framework_registry.py`, `src/lab/defenses/framework_registry.py` | ⚠️ FRAGILE | New plugin files do nothing unless hardcoded imports are updated. | Add explicit discovery/bootstrap strategy and tests for plugin visibility. |
| Gradient attacks coupling to YOLO internals | `src/lab/attacks/fgsm.py`, `src/lab/attacks/pgd.py`, `src/lab/attacks/eot_pgd.py`, `src/lab/attacks/deepfool.py` | ⚠️ FRAGILE | Uses internals/assumptions that may break with Ultralytics updates. | Preserve working paths; document limits; isolate model-dependent logic behind adapters. |
| Attack model injection by signature inspection | `src/lab/runners/experiment_runner.py` | ⚠️ FRAGILE | Runtime behavior changes based on function signature shape (`model` arg and `**kwargs`). | Replace with explicit capability/interface flags in later phase, after parity freeze. |
| Validation metrics optional/disabled defaults | `configs/experiment_lab.yaml`, `src/lab/runners/experiment_runner.py`, `src/lab/runners/run_experiment.py` | ⚠️ FRAGILE | Missing validation can silently produce partial rows or status `missing`. | Enforce explicit validation intent in new runner and surface status loudly. |
| Plot CSV auto-detection order | `scripts/plot_results.py` | ⚠️ FRAGILE | Chooses `results/metrics_summary.csv` before `outputs/metrics_summary.csv`; stale data risk. | Keep behavior for compatibility now; later enforce explicit `--csv` in automation. |
| Framework metric sanitization | `src/lab/eval/framework_metrics.py` | 🧱 SAFE TO MIGRATE | Isolated and additive; improves reliability of non-finite metric handling. | Extend this pattern to legacy compatibility layer without breaking CSV contract. |
| Prediction schema and JSONL writer | `src/lab/eval/prediction_schema.py`, `src/lab/eval/prediction_io.py` | 🧱 SAFE TO MIGRATE | Additive normalized interfaces; no legacy behavior overwrite. | Continue using as canonical internal schema for new path. |
| Documentation drift | `docs/*.md` | 🧼 CLEANUP LATER | Some docs are historical snapshots and may lag current runner decisions. | Update after runner unification and output schema freeze. |
| Stale framework scaffold configs | `configs/lab_framework_skeleton.yaml`, `configs/lab_framework_phase3_compat.yaml` | 🧼 CLEANUP LATER | Useful for historical phases but can confuse users as runnable configs. | Keep during migration; mark archival/deprecated once canonical framework config set is stable. |

## Detailed Findings By Requested Category

## Code Duplication

- Duplicate runner surfaces exist across 4 CLI entrypoints plus 2 runner classes.
- Legacy and framework registries duplicate alias/registration concerns.
- Metrics are computed in two parallel systems (legacy CSV and framework JSON) with partially overlapping logic.

## Multiple Runners

- `ExperimentRunner` remains operational backbone for week1/demo and matrix pipelines.
- `UnifiedExperimentRunner` is active for framework artifacts but not yet the single canonical entrypoint.
- `Phase3CompatRunner` exists as migration scaffolding.

## Config Inconsistencies

- Legacy matrix schema uses `model.path`, `data_yaml`, `image_dir`, `experiments[]`.
- Framework schema uses `model.name/params`, `data.source_dir`, `attack/defense/predict/validation`.
- Alias handling differs by CLI path (`run_experiment.py` resolver adds friendly alias maps; API path builds config directly).

## Refactor Breakpoints (High Impact)

- Any change to output naming/paths in legacy scripts can break week1/runbook docs and demo package assumptions.
- Any change to `metrics_summary.csv` columns/semantics can break:
  - sanity checks (`check_metrics_integrity.py`, `check_fgsm_sanity.py`)
  - plotting scripts and report table generation
- Any change to run-name safety/output-root containment logic may reopen path traversal or stale-row issues.

## Metrics Silent-Failure Risk Zones

- Validation may be disabled (intentionally or by default), leading to partial metric records.
- Malformed label rows can null out confidence stats with warnings, not hard failures.
- Unified runner can capture validation exceptions as `status=error` while still writing outputs; downstream consumers must inspect status.
- Plotting scripts may generate no-data visual placeholders that can look superficially successful.

## Practical Guardrails (Audit Recommendation)

1. Keep legacy CSV + plotting + sanity checks untouched until framework parity is repeatedly validated.
2. Require explicit status checks (`row_status`, validation status) in CI/demo gates.
3. Avoid migrating week1/demo shell orchestration until unified runner supports the same artifacts and checks.
4. Maintain a compatibility matrix: command -> allowed config schema(s) to prevent mixed-path failures.
