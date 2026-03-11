#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${ROOT_DIR}/configs/baseline_blur_compat.yaml"

python3 "${ROOT_DIR}/scripts/run_framework.py" --config "${CONFIG_PATH}" "$@"

