#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

DATASETS_DIR="datasets"
DATASET_ROOT="${DATASETS_DIR}/coco/val2017_subset500"
IMAGES_DIR="${DATASET_ROOT}/images"
ANNOTATIONS_FILE="${DATASET_ROOT}/annotations.json"

mkdir -p "${DATASETS_DIR}"
echo "Dataset directory created: ${DATASETS_DIR}/"

if [[ -d "${IMAGES_DIR}" && -f "${ANNOTATIONS_FILE}" ]]; then
  echo "Dataset found: ${DATASET_ROOT}/"
  echo "Success: COCO subset dataset is configured."
  exit 0
fi

echo ""
echo "Please place the dataset here:"
echo "${DATASET_ROOT}/"
echo ""
echo "Expected structure:"
echo ""
echo "datasets/"
echo "   coco/"
echo "      val2017_subset500/"
echo "         images/"
echo "         annotations.json"

if [[ ! -d "${IMAGES_DIR}" ]]; then
  echo ""
  echo "Missing: ${IMAGES_DIR}/"
fi

if [[ ! -f "${ANNOTATIONS_FILE}" ]]; then
  echo "Missing: ${ANNOTATIONS_FILE}"
fi

exit 1
