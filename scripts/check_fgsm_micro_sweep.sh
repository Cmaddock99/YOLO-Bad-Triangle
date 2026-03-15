#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PY="./.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "ERROR: .venv python not found at $PY"
  exit 1
fi

CONF="0.25"
SEED="42"

# Fine-grained epsilons near collapse threshold
EPS_LIST=("0.00025" "0.0005" "0.001" "0.0015" "0.002")

echo "== FGSM micro sweep =="
echo "conf=$CONF seed=$SEED"

# Baseline reference
"$PY" run_experiment.py conf="$CONF" seed="$SEED" run_name=baseline_fgsm_micro validate=true

# FGSM micro runs
for EPS in "${EPS_LIST[@]}"; do
  RUN_TAG="${EPS//./p}"                 # e.g. 0.0015 -> 0p0015
  RUN_NAME="fgsm_micro_e${RUN_TAG}"
  echo
  echo "Running $RUN_NAME (epsilon=$EPS)"
  "$PY" run_experiment.py \
    attack=fgsm \
    attack.epsilon="$EPS" \
    conf="$CONF" \
    seed="$SEED" \
    run_name="$RUN_NAME" \
    validate=true
done

echo
echo "== Micro sweep summary =="
"$PY" - <<'PY'
import csv
from pathlib import Path

csv_path = Path("outputs/metrics_summary.csv")
rows = list(csv.DictReader(csv_path.open()))

targets = [
    ("baseline", "yolo8_baseline_fgsm_micro"),
    ("e0.00025", "yolo8_fgsm_micro_e0p00025"),
    ("e0.0005",  "yolo8_fgsm_micro_e0p0005"),
    ("e0.001",   "yolo8_fgsm_micro_e0p001"),
    ("e0.0015",  "yolo8_fgsm_micro_e0p0015"),
    ("e0.002",   "yolo8_fgsm_micro_e0p002"),
]

latest = {}
for label, run_name in targets:
    m = [r for r in rows if r["run_name"] == run_name]
    latest[label] = m[-1] if m else None

def f(v):
    try:
        return float(v)
    except Exception:
        return float("nan")

print(f"{'run':<10} {'mAP50':>10} {'mAP50-95':>10} {'precision':>10} {'recall':>10} {'tot_det':>9} {'avg_conf':>10}")
print("-" * 78)

for label, _ in targets:
    r = latest[label]
    if r is None:
        print(f"{label:<10} {'MISSING':>10}")
        continue
    print(
        f"{label:<10} "
        f"{f(r.get('mAP50')):10.4f} "
        f"{f(r.get('mAP50-95')):10.4f} "
        f"{f(r.get('precision')):10.4f} "
        f"{f(r.get('recall')):10.4f} "
        f"{r.get('total_detections',''):>9} "
        f"{f(r.get('avg_conf')):10.4f}"
    )

print("\nDone. Use this to find the first epsilon where mAP drops sharply.")
PY
