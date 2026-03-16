#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Missing virtualenv python at ${PYTHON_BIN}"
  exit 1
fi

MODE="demo"
PROFILE="week1-demo"
CONFIG_PATH=""
OUTPUT_ROOT=""
INCLUDE_PRESENTATION_PLOTS="true"
SANITY_ATTACK=""

apply_profile_defaults() {
  case "${PROFILE}" in
    week1-demo)
      MODE="demo"
      CONFIG_PATH="${ROOT_DIR}/configs/week1_stabilization_demo_matrix.yaml"
      SANITY_ATTACK="fgsm"
      ;;
    week1-stress)
      MODE="strict"
      CONFIG_PATH="${ROOT_DIR}/configs/week1_stabilization_matrix.yaml"
      SANITY_ATTACK="fgsm"
      ;;
    custom)
      if [[ -z "${SANITY_ATTACK}" ]]; then
        SANITY_ATTACK="fgsm"
      fi
      ;;
    *)
      echo "ERROR: --profile must be one of: week1-demo, week1-stress, custom"
      exit 1
      ;;
  esac
}

apply_profile_defaults
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:-}"
      apply_profile_defaults
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --config)
      CONFIG_PATH="${2:-}"
      shift 2
      ;;
    --sanity-attack)
      SANITY_ATTACK="${2:-}"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="${2:-}"
      shift 2
      ;;
    --skip-presentation-plots)
      INCLUDE_PRESENTATION_PLOTS="false"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--profile week1-demo|week1-stress|custom] [--mode demo|strict] [--config <yaml>] [--sanity-attack <name>] [--output-root <dir>] [--skip-presentation-plots]"
      exit 1
      ;;
  esac
done

if [[ -z "${CONFIG_PATH}" ]]; then
  echo "ERROR: Config path is empty. Set --config or use a known --profile."
  exit 1
fi

if [[ "${MODE}" != "demo" && "${MODE}" != "strict" ]]; then
  echo "ERROR: --mode must be 'demo' or 'strict' (got '${MODE}')"
  exit 1
fi

if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "ERROR: Config not found: ${CONFIG_PATH}"
  exit 1
fi

if [[ -z "${OUTPUT_ROOT}" ]]; then
  STAMP="$(date -u +%Y%m%d_%H%M%S)"
  OUTPUT_ROOT="${ROOT_DIR}/outputs/week1_${STAMP}"
fi

METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"
TABLE_MD="${OUTPUT_ROOT}/experiment_table.md"

echo "Running week1 stabilization matrix (${MODE} mode)"
echo "Profile: ${PROFILE}"
echo "Config: ${CONFIG_PATH}"
echo "Sanity attack target: ${SANITY_ATTACK}"
echo "Output root: ${OUTPUT_ROOT}"
echo "Preflight: checking local environment and assets"
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_environment.py"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/run_framework.py" \
  --config "${CONFIG_PATH}" \
  --output_root "${OUTPUT_ROOT}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_metrics_integrity.py" \
  --csv "${METRICS_CSV}" \
  --attack "${SANITY_ATTACK}"

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/generate_experiment_table.py" \
  --input_csv "${METRICS_CSV}" \
  --output_md "${TABLE_MD}"

if "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_fgsm_sanity.py" \
  --csv "${METRICS_CSV}" \
  --attack "${SANITY_ATTACK}" \
  --profile "${PROFILE}" \
  --use-latest-session \
  --fail-on-all-zero-fgsm; then
  echo "${SANITY_ATTACK} sanity check: PASS"
else
  if [[ "${MODE}" == "strict" ]]; then
    echo "${SANITY_ATTACK} sanity check: FAIL (strict mode abort)"
    exit 1
  fi
  echo "${SANITY_ATTACK} sanity check: FAIL (demo mode continues)"
  echo "NOTE: Present this as a stress-test collapse result and continue to plots."
fi

echo "Generating base plots"
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_results.py" \
  --csv "${METRICS_CSV}"

if [[ "${INCLUDE_PRESENTATION_PLOTS}" == "true" ]]; then
  echo "Generating presentation plots"
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_week1_snapshot.py" \
    --csv "${METRICS_CSV}" \
    --output-dir "${OUTPUT_ROOT}/plots"
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/plot_week1_report_card.py" \
    --csv "${METRICS_CSV}" \
    --variant both
fi

echo "Week1 run complete."
echo "Metrics: ${METRICS_CSV}"
echo "Table: ${TABLE_MD}"
echo "Plots: ${OUTPUT_ROOT}/plots"
ln -sfn "${OUTPUT_ROOT}" "${ROOT_DIR}/outputs/demo-latest"
echo "Alias: ${ROOT_DIR}/outputs/demo-latest -> ${OUTPUT_ROOT}"
echo "All artifacts command:"
echo "  bash ${ROOT_DIR}/scripts/generate_week1_demo_artifacts.sh --csv ${METRICS_CSV}"
