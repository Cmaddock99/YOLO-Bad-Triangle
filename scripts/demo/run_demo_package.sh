#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Missing virtualenv python at ${PYTHON_BIN}"
  exit 1
fi

ACTION="${1:-help}"
shift || true

OUTPUT_ROOT="${ROOT_DIR}/outputs/demo-reference"
OUTPUT_ROOT_EXPLICIT="false"
PROFILE="demo"
CONFIG_PATH=""
SANITY_ATTACK=""
FRAMEWORK_RUNS_ROOT=""

apply_profile_defaults() {
  case "${PROFILE}" in
    demo|week1-demo|fast-demo|strict|week1-stress)
      CONFIG_PATH="${ROOT_DIR}/configs/lab_framework_phase5.yaml"
      SANITY_ATTACK="fgsm"
      ;;
    custom)
      if [[ -z "${SANITY_ATTACK}" ]]; then
        SANITY_ATTACK="fgsm"
      fi
      ;;
    *)
      echo "ERROR: --profile must be one of: strict, demo, fast-demo, week1-demo, week1-stress, custom"
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
    --output-root)
      OUTPUT_ROOT="${2:-}"
      OUTPUT_ROOT_EXPLICIT="true"
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
    --framework-runs-root)
      FRAMEWORK_RUNS_ROOT="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"

resolve_framework_runs_root() {
  if [[ -n "${FRAMEWORK_RUNS_ROOT}" ]]; then
    return
  fi
  if [[ -d "${OUTPUT_ROOT}/framework_runs" ]]; then
    FRAMEWORK_RUNS_ROOT="${OUTPUT_ROOT}/framework_runs"
    return
  fi
  FRAMEWORK_RUNS_ROOT="${OUTPUT_ROOT}"
}

required_attack_rows_for_profile() {
  case "${PROFILE}" in
    strict|week1-stress|custom)
      echo "2"
      ;;
    *)
      echo "1"
      ;;
  esac
}

ensure_legacy_csv_from_framework_if_needed() {
  if [[ -f "${METRICS_CSV}" ]]; then
    return
  fi
  resolve_framework_runs_root
  if [[ ! -d "${FRAMEWORK_RUNS_ROOT}" ]]; then
    return
  fi
  echo "metrics_summary.csv not found; building legacy-compatible artifacts from framework runs"
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/generate_legacy_compat_artifacts.py" \
    --runs-root "${FRAMEWORK_RUNS_ROOT}" \
    --output-root "${OUTPUT_ROOT}"
}

resolve_default_output_root() {
  if [[ "${OUTPUT_ROOT_EXPLICIT}" == "true" ]]; then
    return
  fi
  if [[ -f "${OUTPUT_ROOT}/metrics_summary.csv" ]]; then
    return
  fi
  if [[ -L "${ROOT_DIR}/outputs/demo-latest" ]] || [[ -d "${ROOT_DIR}/outputs/demo-latest" ]]; then
    OUTPUT_ROOT="${ROOT_DIR}/outputs/demo-latest"
    return
  fi
  local latest
  latest="$(ls -dt "${ROOT_DIR}"/outputs/week1_* 2>/dev/null | head -n 1 || true)"
  if [[ -n "${latest}" ]]; then
    OUTPUT_ROOT="${latest}"
  fi
}

print_usage() {
  cat <<EOF
Usage:
  bash scripts/demo/run_demo_package.sh <action> [--profile <name>] [--output-root <dir>] [--config <yaml>] [--sanity-attack <name>] [--framework-runs-root <dir>]

Actions:
  preflight    Run environment checks only.
  live-demo    Run full week1 demo mode pipeline (compute).
  live-strict  Run full week1 strict mode pipeline (compute).
  artifacts    Rebuild all plots/tables from existing CSV.
  gates        Run integrity + FGSM sanity gates on existing CSV.
  summary      Print concise interpretation summary from CSV.
  fast         preflight + artifacts + gates + summary (no model rerun).
  full-demo    preflight + live-demo + artifacts + gates + summary.
  help         Show this message.
EOF
}

run_preflight() {
  echo "== Preflight =="
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_environment.py"
  local required_rows
  required_rows="$(required_attack_rows_for_profile)"
  if [[ -f "${METRICS_CSV}" ]]; then
    "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_profile_preflight.py" \
      --profile "${PROFILE}" \
      --config "${CONFIG_PATH}" \
      --attack "${SANITY_ATTACK}" \
      --required-attack-rows "${required_rows}" \
      --csv "${METRICS_CSV}"
  else
    "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_profile_preflight.py" \
      --profile "${PROFILE}" \
      --config "${CONFIG_PATH}" \
      --attack "${SANITY_ATTACK}" \
      --required-attack-rows "${required_rows}"
  fi
}

run_live_demo() {
  echo "== Live demo run =="
  bash "${ROOT_DIR}/scripts/run_week1_stabilization.sh" \
    --profile "${PROFILE}" \
    --mode demo \
    --config "${CONFIG_PATH}" \
    --sanity-attack "${SANITY_ATTACK}" \
    --output-root "${OUTPUT_ROOT}"
}

run_live_strict() {
  echo "== Live strict run =="
  bash "${ROOT_DIR}/scripts/run_week1_stabilization.sh" \
    --profile "${PROFILE}" \
    --mode strict \
    --config "${CONFIG_PATH}" \
    --sanity-attack "${SANITY_ATTACK}" \
    --output-root "${OUTPUT_ROOT}"
}

run_artifacts() {
  echo "== Artifact rebuild =="
  ensure_legacy_csv_from_framework_if_needed
  bash "${ROOT_DIR}/scripts/generate_week1_demo_artifacts.sh" \
    --output-root "${OUTPUT_ROOT}"
}

run_gates() {
  echo "== Gate checks =="
  echo "Profile: ${PROFILE}"
  echo "Sanity attack target: ${SANITY_ATTACK}"
  ensure_legacy_csv_from_framework_if_needed
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_metrics_integrity.py" \
    --csv "${METRICS_CSV}" \
    --attack "${SANITY_ATTACK}" \
    --profile "${PROFILE}"

  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_fgsm_sanity.py" \
    --csv "${METRICS_CSV}" \
    --attack "${SANITY_ATTACK}" \
    --profile "${PROFILE}" \
    --use-latest-session

  if "${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_fgsm_sanity.py" \
    --csv "${METRICS_CSV}" \
    --attack "${SANITY_ATTACK}" \
    --profile "${PROFILE}" \
    --use-latest-session \
    --fail-on-all-zero-fgsm; then
    echo "Strict ${SANITY_ATTACK} collapse gate: PASS"
  else
    echo "Strict ${SANITY_ATTACK} collapse gate: FAIL (expected on current stress-test behavior)"
  fi
}

run_summary() {
  echo "== Interpretation summary =="
  ensure_legacy_csv_from_framework_if_needed
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/demo/summary_interpretation.py" \
    --csv "${METRICS_CSV}"
}

resolve_default_output_root
METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"

case "${ACTION}" in
  preflight)
    run_preflight
    ;;
  live-demo)
    run_live_demo
    ;;
  live-strict)
    run_live_strict
    ;;
  artifacts)
    run_artifacts
    ;;
  gates)
    run_gates
    ;;
  summary)
    run_summary
    ;;
  fast)
    resolve_default_output_root
    METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"
    run_preflight
    run_artifacts
    run_gates
    run_summary
    ;;
  full-demo)
    resolve_default_output_root
    METRICS_CSV="${OUTPUT_ROOT}/metrics_summary.csv"
    run_preflight
    run_live_demo
    run_artifacts
    run_gates
    run_summary
    ;;
  help|--help|-h)
    print_usage
    ;;
  *)
    echo "Unknown action: ${ACTION}"
    print_usage
    exit 1
    ;;
esac
