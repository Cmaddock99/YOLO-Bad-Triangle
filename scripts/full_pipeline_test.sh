#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

activate_env_if_available() {
  if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
    return
  fi
  if [[ -f "venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "venv/bin/activate"
  fi
}

run_pipeline() {
  activate_env_if_available

  if ! command -v python >/dev/null 2>&1; then
    return 1
  fi

  python run_experiment.py attack=none || return 1
  python run_experiment.py attack=blur || return 1
  python run_experiment.py attack=deepfool || return 1
  python run_experiment.py attack=deepfool defense=median || return 1

  [[ -d "outputs" ]] || return 1
  [[ -f "outputs/metrics_summary.csv" ]] || return 1
  return 0
}

if run_pipeline; then
  echo "Full BAD Triangle pipeline test successful."
else
  echo "Pipeline test failed."
  exit 1
fi
