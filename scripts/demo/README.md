# Demo Scripts Package

This folder bundles the full week1 demo workflow into one command surface.

Canonical runtime entrypoints remain framework-first:
- `./.venv/bin/python scripts/run_unified.py run-one --config configs/lab_framework_phase5.yaml`
- `./.venv/bin/python run_experiment.py attack=fgsm conf=0.25`

## Document metadata

- `validated_at_utc`: `2026-03-19T17:55:15Z`
- `validated_against_commit`: `4a11a17`

## Quick start (recommended)

From repo root:

- `bash scripts/demo/set_demo_reference.sh`
- `bash scripts/demo/run_demo_package.sh fast --profile week1-demo --output-root outputs/demo-reference`

This runs:

1. preflight environment checks,
2. deterministic artifact rebuild from the chosen output root,
3. integrity and FGSM sanity gates,
4. a concise interpretation summary.

## Actions

- `preflight`: check environment only.
- `live-demo`: run full compute pipeline in demo mode.
- `live-strict`: run full compute pipeline in strict mode.
- `artifacts`: regenerate all plots/tables from existing CSV.
- `gates`: run integrity/sanity checks against existing CSV.
- `summary`: print concise interpretation from CSV.
- `fast`: preflight + artifacts + gates + summary (no compute rerun).
- `full-demo`: preflight + live-demo + artifacts + gates + summary.

## Usage

- `bash scripts/demo/run_demo_package.sh help`
- `bash scripts/demo/run_demo_package.sh <action> [--profile <name>] [--output-root <dir>] [--config <yaml>] [--sanity-attack <name>] [--framework-runs-root <dir>]`

Defaults:

- `--profile`: `demo`
- `--output-root`: `outputs/demo-reference`
- `--config`: profile-derived unless explicitly provided
- `--sanity-attack`: profile-derived (`fgsm` by default)
- `--framework-runs-root`: optional source for framework runs used to auto-build legacy-compatible CSV if `metrics_summary.csv` is missing

## Profile guidance

- `demo` (alias: `week1-demo`):
  - Recommended default for demo rehearsals and presentation flows.
  - Uses `configs/lab_framework_phase5.yaml`.
- `strict` (aliases: `week1-stress`, `custom`):
  - Higher-stress profile with stricter expectations.
  - Uses `configs/lab_framework_phase5.yaml`.
- `fast-demo`:
  - Uses demo matrix defaults with warning-tolerant gate semantics.
  - Intended for rapid package checks where compute reruns are skipped.

### Demo Profile Behavior

`run_demo_package.sh` gate behavior is controlled by `configs/runtime_profiles.yaml`.

- In `strict`, incomplete FGSM sweeps and baseline==FGSM results are failures.
- In `demo` / `fast-demo`, the same conditions are emitted as warnings and the package continues.

These warnings are acceptable in demo mode because the primary objective is preserving observability (artifacts + summary continuity) during rehearsal and handoff flows; strict mode remains the enforcement path for reliability-sensitive runs.

## Common pitfall

`fast` and `artifacts` actions assume expected attack rows exist in the selected CSV.  
If you use `--profile custom` with a non-FGSM dataset, snapshot/report-card generation can fail due to missing baseline/FGSM rows.  
Use `--profile week1-demo` unless you intentionally prepared a custom-compatible CSV.

When running against framework-only outputs, the package now tries to build `metrics_summary.csv` from framework run folders automatically.  
Use `--framework-runs-root` if your framework runs are not under `<output-root>/framework_runs`.

## Interpretation helper directly

- `./.venv/bin/python scripts/demo/summary_interpretation.py --csv outputs/demo-reference/metrics_summary.csv`
