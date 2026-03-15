#!/usr/bin/env bash
set -euo pipefail

# Run from repo root.
cd "$(dirname "$0")/.."

# Ensure venv python is used.
PY="./.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "ERROR: .venv not found. Create/activate it first."
  exit 1
fi

# Common settings
CONF="0.25"
SEED="42"
OUT="outputs"

echo "== Running baseline + FGSM sweep checks =="
"$PY" run_experiment.py conf="$CONF" seed="$SEED" run_name=baseline_fgsm_ref validate=true
"$PY" run_experiment.py attack=fgsm attack.epsilon=0.002 conf="$CONF" seed="$SEED" run_name=fgsm_e002 validate=true
"$PY" run_experiment.py attack=fgsm attack.epsilon=0.004 conf="$CONF" seed="$SEED" run_name=fgsm_e004 validate=true
"$PY" run_experiment.py attack=fgsm attack.epsilon=0.008 conf="$CONF" seed="$SEED" run_name=fgsm_e008 validate=true

echo
echo "== Latest metrics trend (baseline, e002, e004, e008) =="

"$PY" - <<'PY'
import csv
from pathlib import Path

csv_path = Path("outputs/metrics_summary.csv")
targets = [
    ("baseline", "yolo8_baseline_fgsm_ref"),
    ("e002", "yolo8_fgsm_e002"),
    ("e004", "yolo8_fgsm_e004"),
    ("e008", "yolo8_fgsm_e008"),
]

rows = list(csv.DictReader(csv_path.open()))
latest = {}
for label, run_name in targets:
    matches = [r for r in rows if r["run_name"] == run_name]
    if not matches:
        latest[label] = None
    else:
        latest[label] = matches[-1]  # latest occurrence

def f(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

print(f"{'run':<10} {'mAP50':>10} {'mAP50-95':>10} {'precision':>10} {'recall':>10} {'total_det':>10}")
print("-" * 70)

order = ["baseline", "e002", "e004", "e008"]
map50_values = []

for key in order:
    row = latest[key]
    if row is None:
        print(f"{key:<10} {'MISSING':>10}")
        map50_values.append(float("nan"))
        continue
    m50 = f(row.get("mAP50"))
    m95 = f(row.get("mAP50-95"))
    p = f(row.get("precision"))
    r = f(row.get("recall"))
    td = row.get("total_detections", "")
    map50_values.append(m50)
    print(f"{key:<10} {m50:10.4f} {m95:10.4f} {p:10.4f} {r:10.4f} {td:>10}")

# Monotonic non-increasing check: baseline >= e002 >= e004 >= e008
ok = all(
    map50_values[i] >= map50_values[i+1]
    for i in range(len(map50_values)-1)
    if map50_values[i] == map50_values[i] and map50_values[i+1] == map50_values[i+1]  # not NaN
)

print()
print("mAP50 monotonic check (baseline >= e002 >= e004 >= e008):", "PASS" if ok else "FAIL")
PY

