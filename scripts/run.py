set -euo pipefail

# --- Config ---
PY=./.venv/bin/python
export PYTHONPATH=src
TS=$(date -u +%Y%m%dT%H%M%SZ)
RUNS_ROOT="outputs/framework_runs/sweep_${TS}"
REPORT_ROOT="outputs/framework_reports/sweep_${TS}"
MAX_IMAGES=8
SEED=42

# Attacks discovered from your current framework plugins
ATTACKS=(bim blur deepfool fgsm gaussian_blur ifgsm pgd)

echo "Runs root:    ${RUNS_ROOT}"
echo "Reports root: ${REPORT_ROOT}"
mkdir -p "${RUNS_ROOT}" "${REPORT_ROOT}"

# 1) Baseline run
BASELINE_RUN="baseline_none"
$PY src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set runner.output_root="${RUNS_ROOT}" \
  --set runner.run_name="${BASELINE_RUN}" \
  --set runner.seed="${SEED}" \
  --set runner.max_images="${MAX_IMAGES}" \
  --set attack.name=none \
  --set defense.name=none \
  --set validation.enabled=false \
  --set summary.enabled=false

# 2) Attack sweep
for ATTACK in "${ATTACKS[@]}"; do
  RUN_NAME="attack_${ATTACK}"
  echo "Running attack: ${ATTACK}"
  $PY src/lab/runners/run_experiment.py \
    --config configs/lab_framework_phase5.yaml \
    --set runner.output_root="${RUNS_ROOT}" \
    --set runner.run_name="${RUN_NAME}" \
    --set runner.seed="${SEED}" \
    --set runner.max_images="${MAX_IMAGES}" \
    --set attack.name="${ATTACK}" \
    --set defense.name=none \
    --set validation.enabled=false \
    --set summary.enabled=false

  # 3) Per-attack human-readable summary
  $PY scripts/print_summary.py \
    --baseline "${RUNS_ROOT}/${BASELINE_RUN}" \
    --attack "${RUNS_ROOT}/${RUN_NAME}" \
    > "${REPORT_ROOT}/summary_${ATTACK}.txt"
done

# 4) Consolidated framework report (CSV + Markdown)
$PY scripts/generate_framework_report.py \
  --runs-root "${RUNS_ROOT}" \
  --output-dir "${REPORT_ROOT}"

echo ""
echo "Done."
echo "Per-attack summaries: ${REPORT_ROOT}/summary_*.txt"
echo "Aggregate CSV:        ${REPORT_ROOT}/framework_run_summary.csv"
echo "Aggregate Markdown:   ${REPORT_ROOT}/framework_run_report.md"
