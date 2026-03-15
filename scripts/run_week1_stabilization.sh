#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Missing virtualenv python at ${PYTHON_BIN}"
  exit 1
fi

STAMP="$(date -u +%Y%m%d_%H%M%S)"
OUTPUT_ROOT="${ROOT_DIR}/outputs/week1_${STAMP}"
CONFIG_PATH="${ROOT_DIR}/configs/week1_stabilization_matrix.yaml"
METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"
TABLE_MD="${OUTPUT_ROOT}/experiment_table.md"

echo "Running week1 stabilization matrix"
echo "Config: ${CONFIG_PATH}"
echo "Output root: ${OUTPUT_ROOT}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/run_framework.py" \
  --config "${CONFIG_PATH}" \
  --output_root "${OUTPUT_ROOT}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_metrics_integrity.py" \
  --csv "${METRICS_CSV}" \
  --attack fgsm

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_fgsm_sanity.py" \
  --csv "${METRICS_CSV}" \
  --attack fgsm \
  --use-latest-session \
  --fail-on-all-zero-fgsm

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/generate_experiment_table.py" \
  --input_csv "${METRICS_CSV}" \
  --output_md "${TABLE_MD}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_results.py" \
  --csv "${METRICS_CSV}"

echo "Week1 run complete."
echo "Metrics: ${METRICS_CSV}"
echo "Table: ${TABLE_MD}"
echo "Plots: ${OUTPUT_ROOT}/plots"
