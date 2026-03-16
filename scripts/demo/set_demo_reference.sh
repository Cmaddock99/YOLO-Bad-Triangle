#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-root)
      SOURCE_ROOT="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--source-root <outputs/week1_...>]"
      exit 1
      ;;
  esac
done

if [[ -z "${SOURCE_ROOT}" ]]; then
  SOURCE_ROOT="$(ls -dt "${ROOT_DIR}"/outputs/week1_* 2>/dev/null | head -n 1 || true)"
fi

if [[ -n "${SOURCE_ROOT}" && "${SOURCE_ROOT}" != /* ]]; then
  SOURCE_ROOT="${ROOT_DIR}/${SOURCE_ROOT}"
fi

if [[ -n "${SOURCE_ROOT}" ]]; then
  SOURCE_ROOT="$(cd "${SOURCE_ROOT}" && pwd)"
fi

if [[ -z "${SOURCE_ROOT}" ]]; then
  echo "ERROR: No week1 output root found."
  exit 1
fi

if [[ ! -f "${SOURCE_ROOT}/metrics_summary.csv" ]]; then
  echo "ERROR: metrics_summary.csv not found in source root: ${SOURCE_ROOT}"
  exit 1
fi

LATEST_LINK="${ROOT_DIR}/outputs/demo-latest"
REFERENCE_LINK="${ROOT_DIR}/outputs/demo-reference"

ln -sfn "${SOURCE_ROOT}" "${LATEST_LINK}"
ln -sfn "${SOURCE_ROOT}" "${REFERENCE_LINK}"

echo "Updated aliases:"
echo "  outputs/demo-latest -> ${SOURCE_ROOT}"
echo "  outputs/demo-reference -> ${SOURCE_ROOT}"
