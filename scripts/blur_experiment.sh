#!/usr/bin/env bash
set -euo pipefail

# === Configuration (UNSPECIFIED paths should be replaced) ===
MODEL_PATH="yolov8n.pt"             # Path to YOLOv8 model (UNSPECIFIED)
DATA_YAML="DATA_YAML="coco/val2017_subset500/subset.yaml"            # Path to data YAML (UNSPECIFIED)
IMG_SIZE=640                                     # Image size
IOU=0.50                                         # IoU threshold
SEED=0                                           # RNG seed

# Default lists (can override via -t and -a)
DEFAULT_THRESHOLDS="0.25,0.50,0.75"
DEFAULT_ATTACKS="none,blur"

# Activate virtualenv (adjust the path to your venv)
# source /path/to/venv/bin/activate

# Check that YOLO CLI is installed
if ! command -v yolo &> /dev/null; then
  echo "Error: Ultralytics YOLO CLI ('yolo') not found. Install via 'pip install ultralytics'."
  exit 1
fi

# Parse command-line options for thresholds and attacks
THRESHOLDS="$DEFAULT_THRESHOLDS"
ATTACKS="$DEFAULT_ATTACKS"
while getopts ":t:a:" opt; do
  case ${opt} in
    t ) THRESHOLDS="$OPTARG" ;;
    a ) ATTACKS="$OPTARG" ;;
    \? ) echo "Usage: $0 [-t thresh_list] [-a attack_list]"; exit 1 ;;
  esac
done
IFS=',' read -r -a TH_ARRAY <<< "$THRESHOLDS"
IFS=',' read -r -a ATTACK_ARRAY <<< "$ATTACKS"

# Ensure results directory exists
mkdir -p results

# Function to run YOLO val/predict and parse metrics
run_experiment() {
  local run_name="$1"         # e.g. baseline__conf025__iou050__img640__seed0
  local source_dir="$2"       # e.g. "" for baseline (use DATA_YAML), or "attacks/blur/images"
  local conf="$3"             
  local attack_name="$4"      # e.g. none or blur

  echo -e "\n*** Running $run_name (conf=$conf, attack=$attack_name) ***\n"

  # 1. Validation (produces metrics and JSON)
  #    We use 'yolo val' with save_json, save_txt, save_conf【15†L290-L295】【15†L232-L236】.
  if [ "$attack_name" = "none" ]; then
    yolo val \
      model="$MODEL_PATH" \
      data="$DATA_YAML" \
      imgsz=$IMG_SIZE \
      conf="$conf" \
      iou=$IOU \
      seed=$SEED \
      save_json=True \
      save_txt=True \
      save_conf=True \
      project=results \
      name="$run_name" \
      exist_ok=True
  else
    # For attacked images, one could create a temp YAML or use the dataset with perturbed images.
    # Here we skip 'yolo val' for attack, or assume DATA_YAML works with images replaced.
    echo "(Skipping val for attack runs; parsing predict output only.)"
  fi

  # 2. Prediction (inference on images)
  #    We use 'yolo predict' with save, save_txt, save_conf【7†L540-L543】【7†L635-L639】.
  if [ "$attack_name" = "none" ]; then
    # Baseline predict on original images
    yolo predict \
      model="$MODEL_PATH" \
      source="$(grep 'path:' "$DATA_YAML" | sed 's/path: //')" \
      imgsz=$IMG_SIZE \
      conf="$conf" \
      iou=$IOU \
      seed=$SEED \
      save=True \
      save_txt=True \
      save_conf=True \
      project=results \
      name="$run_name" \
      exist_ok=True
  else
    # Predict on attacked images
    yolo predict \
      model="$MODEL_PATH" \
      source="$source_dir" \
      imgsz=$IMG_SIZE \
      conf="$conf" \
      iou=$IOU \
      seed=$SEED \
      save=True \
      save_txt=True \
      save_conf=True \
      project=results \
      name="$run_name" \
      exist_ok=True
  fi

  # 3. Parse outputs and append metrics to CSV
  python3 parse_yolo_metrics.py --run_name "$run_name" --attack "$attack_name" --conf "$conf"
}

# Main loop: iterate thresholds and attacks
for conf in "${TH_ARRAY[@]}"; do
  # Normalize conf string (e.g. 0.25 -> 025) for naming
  conf_str=$(echo "$conf" | awk -F. '{printf "%03d", $2*100}')
  # Baseline run (no attack)
  run_name="baseline__conf${conf_str}__iou050__img${IMG_SIZE}__seed${SEED}"
  run_experiment "$run_name" "" "$conf" "none"

  # Attack runs (e.g. blur)
  for att in "${ATTACK_ARRAY[@]}"; do
    if [ "$att" != "none" ]; then
      run_name="attack_${att}__conf${conf_str}__iou050__img${IMG_SIZE}__seed${SEED}"
      run_experiment "$run_name" "attacks/${att}/images" "$conf" "$att"
    fi
  done
done

