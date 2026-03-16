#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Missing virtualenv python at ${PYTHON_BIN}"
  exit 1
fi

CSV_PATH=""
OUTPUT_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv)
      CSV_PATH="${2:-}"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--csv <metrics_summary.csv> | --output-root <outputs/week1_...>]"
      exit 1
      ;;
  esac
done

if [[ -n "${CSV_PATH}" && -n "${OUTPUT_ROOT}" ]]; then
  echo "ERROR: Provide only one of --csv or --output-root."
  exit 1
fi

if [[ -n "${OUTPUT_ROOT}" ]]; then
  CSV_PATH="${OUTPUT_ROOT}/metrics_summary.csv"
fi

if [[ -z "${CSV_PATH}" ]]; then
  echo "ERROR: You must provide --csv or --output-root."
  exit 1
fi

if [[ ! -f "${CSV_PATH}" ]]; then
  echo "ERROR: metrics_summary.csv not found: ${CSV_PATH}"
  exit 1
fi

PLOTS_DIR="$(cd "$(dirname "${CSV_PATH}")" && pwd)/plots"

echo "Generating deterministic week1 demo artifacts"
echo "CSV: ${CSV_PATH}"
echo "Plots dir: ${PLOTS_DIR}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_results.py" \
  --csv "${CSV_PATH}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_week1_snapshot.py" \
  --csv "${CSV_PATH}" \
  --output-dir "${PLOTS_DIR}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_week1_report_card.py" \
  --csv "${CSV_PATH}" \
  --variant both

echo "Done."
echo "Generated:"
echo "  ${PLOTS_DIR}/map50-by-attack.png"
echo "  ${PLOTS_DIR}/precision-recall-by-attack.png"
echo "  ${PLOTS_DIR}/baseline-vs-fgsm-metrics.png"
echo "  ${PLOTS_DIR}/fgsm-epsilon-trend.png"
echo "  ${PLOTS_DIR}/robustness-report-card.png"
echo "  ${PLOTS_DIR}/robustness-report-card-by-epsilon.png"
