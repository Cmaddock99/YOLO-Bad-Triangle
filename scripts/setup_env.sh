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

"${PYTHON_BIN}" -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo ""
echo "Environment setup complete."
echo "Run a baseline experiment using:"
echo "python run_experiment.py attack=none"
