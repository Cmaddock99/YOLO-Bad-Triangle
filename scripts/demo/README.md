# Demo Scripts Package

This folder bundles the full week1 demo workflow into one command surface.

## Quick start (recommended)

From repo root:

- `bash scripts/demo/set_demo_reference.sh`
- `bash scripts/demo/run_demo_package.sh fast --output-root outputs/demo-reference`

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
- `bash scripts/demo/run_demo_package.sh <action> [--output-root <dir>] [--config <yaml>]`

Defaults:

- `--output-root`: `outputs/demo-reference`
- `--config`: `configs/week1_stabilization_demo_matrix.yaml`

## Interpretation helper directly

- `./.venv/bin/python scripts/demo/summary_interpretation.py --csv outputs/demo-reference/metrics_summary.csv`
