#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  echo "Activated virtual environment: .venv"
else
  echo "Virtual environment not found at .venv; using system Python."
fi

echo "Running baseline experiment..."
python run_experiment.py attack=none

echo "Running blur attack..."
python run_experiment.py attack=blur

echo "Running deepfool attack..."
python run_experiment.py attack=deepfool

echo "Running deepfool attack with median defense..."
python run_experiment.py attack=deepfool defense=median

echo "Generating experiment table..."
python scripts/generate_experiment_table.py

echo "Generating visualization plots..."
python scripts/visualize_results.py

echo ""
echo "All experiments completed."
echo "Results available in outputs/."
