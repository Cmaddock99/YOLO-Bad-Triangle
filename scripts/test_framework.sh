#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="python"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: Python is required but was not found." >&2
  exit 1
fi

"${PYTHON_BIN}" run_experiment.py attack=none
"${PYTHON_BIN}" run_experiment.py attack=blur
"${PYTHON_BIN}" run_experiment.py attack=deepfool defense=median

if [[ ! -d "outputs" ]]; then
  echo "Error: outputs/ directory not found." >&2
  exit 1
fi

if [[ ! -f "outputs/metrics_summary.csv" ]]; then
  echo "Error: outputs/metrics_summary.csv not found." >&2
  exit 1
fi

echo "Framework test successful."
echo "Experiments completed."
echo "Results saved to outputs/."
