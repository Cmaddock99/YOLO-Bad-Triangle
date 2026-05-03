# Repo Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the most internally coherent final repo state possible: one canonical auto-cycle from current code, one authoritative imported-patch evaluation, and only then an optional training story.

**Architecture:** Do not anchor final completeness on the mixed historical artifacts currently in `outputs/`. Instead, create one fresh canonical `auto_cycle` from current code and let that cycle become the source of truth for `cycle_state.json`, `cycle_training_signal.json`, raw runs, reports, summaries, and any downstream training attempt. Use historical `cycle_20260330_115004` only as the fallback evidence base if the fresh cycle run is blocked.

**Tech Stack:** Python 3.11, repo CLI wrappers under `scripts/`, `outputs/` artifact tree, JSON/CSV/Markdown/HTML reporting, local model weights and COCO subset data.

---

### Task 1: Lock the Canonical Cycle Strategy

**Files:**
- Read: `outputs/cycle_state.json`
- Read: `outputs/cycle_training_signal.json`
- Read: `outputs/cycle_history/cycle_20260330_115004.json`
- Read: `outputs/training_runs/cycle_20260406_054944/training_manifest.json`

- [ ] **Step 1: Confirm the current root-level artifacts are inconsistent**

Run:

```bash
sed -n '1,80p' outputs/cycle_state.json
sed -n '1,80p' outputs/cycle_training_signal.json
sed -n '1,80p' outputs/training_runs/cycle_20260406_054944/training_manifest.json
```

Expected:
- `cycle_state.json` points to an older cycle
- `cycle_training_signal.json` points to `cycle_20260406_054944`
- the existing training manifest is failed or incomplete

- [ ] **Step 2: Record the canonical strategy**

Decision:

```text
Primary path: run one fresh final auto_cycle from current code and use that new cycle as the canonical repo-complete baseline.
Fallback path: if fresh auto_cycle blocks, use cycle_20260330_115004 as the best existing local evidence cycle.
```

Expected: no one on the team treats `cycle_20260330_115004`, `cycle_20260406_054944`, and the current root-level automation files as one coherent story.

### Task 2: Generate One Fresh Canonical Auto-Cycle

**Files:**
- Read/Write: `outputs/cycle_state.json`
- Read/Write: `outputs/cycle_training_signal.json`
- Read/Write: `outputs/cycle_history/`
- Read/Write: `outputs/framework_runs/`
- Read/Write: `outputs/framework_reports/`

- [ ] **Step 1: Snapshot the current root-level automation artifacts before rerunning**

Run:

```bash
mkdir -p outputs/pre_completion_snapshot
cp outputs/cycle_state.json outputs/pre_completion_snapshot/cycle_state.before.json
cp outputs/cycle_training_signal.json outputs/pre_completion_snapshot/cycle_training_signal.before.json
cp outputs/cycle_report.csv outputs/pre_completion_snapshot/cycle_report.before.csv
cp outputs/cycle_report.md outputs/pre_completion_snapshot/cycle_report.before.md
```

Expected: you can recover the current root-level files if needed.

- [ ] **Step 2: Run the canonical auto-cycle**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/automation/auto_cycle.py --profile yolo11n_lab_v1
```

Expected:
- a new cycle ID appears in `outputs/cycle_state.json`
- a new `outputs/cycle_history/cycle_<new_id>.json` is written
- a new `outputs/framework_runs/cycle_<new_id>/` directory exists
- `outputs/cycle_training_signal.json` points to the same `<new_id>`

- [ ] **Step 3: Verify the new canonical cycle is locally complete**

Run:

```bash
NEW_CYCLE_ID=$(python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path("outputs/cycle_state.json").read_text())
print(payload["cycle_id"])
PY
)
echo "$NEW_CYCLE_ID"
find "outputs/framework_runs/$NEW_CYCLE_ID" -maxdepth 1 -type d | sort | sed -n '1,120p'
test -f "outputs/cycle_history/${NEW_CYCLE_ID}.json" && echo history_ok
```

Expected:
- one cycle ID is printed
- raw runs exist under `outputs/framework_runs/<new_id>/`
- the matching history JSON exists

- [ ] **Step 4: Regenerate cycle-level reports from the new raw runs**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/generate_cycle_report.py
PYTHONPATH=src ./.venv/bin/python scripts/generate_framework_report.py --runs-root "outputs/framework_runs/$NEW_CYCLE_ID" --output-dir "outputs/framework_reports/$NEW_CYCLE_ID"
PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py --report-dir "outputs/framework_reports/$NEW_CYCLE_ID" --output "outputs/framework_reports/$NEW_CYCLE_ID/dashboard.html" --no-pages
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_auto_summary.py --runs-root "outputs/framework_runs/$NEW_CYCLE_ID" --output-dir "outputs/summaries/$NEW_CYCLE_ID"
```

Expected:
- `framework_run_summary.csv`
- `framework_run_report.md`
- `dashboard.html`
- `summary.json`
- `summary.md`
- `headline_metrics.csv`
- `per_class_vulnerability.csv`
- `warnings.json`

### Task 3: Make Imported Patch Evaluation Authoritative

**Files:**
- Read: `configs/patch_artifacts.yaml`
- Read/Write: `outputs/patch_matrix/`
- Read/Write: `outputs/framework_reports/patch_matrix/`

- [ ] **Step 1: Confirm the current patch report is proxy-only**

Run:

```bash
sed -n '1,120p' configs/patch_artifacts.yaml
rg -n ",missing," outputs/framework_reports/patch_matrix/framework_run_summary.csv
```

Expected:
- `validation.enabled=true` is absent from the patch config flow
- current patch rows show `validation_status=missing`

- [ ] **Step 2: Run patch-matrix again with validation enabled**

Run:

```bash
export ADV_PATCH_ARTIFACT_PATH=/absolute/path/to/canonical_patch_artifact
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_checkpoint.pt
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py patch-matrix --matrix-config configs/patch_artifacts.yaml --set validation.enabled=true
```

Expected:
- fresh patch runs are written under `outputs/patch_matrix/`
- validation-enabled metrics are generated inside the run artifacts

- [ ] **Step 3: Regenerate patch reports from the new runs**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/generate_framework_report.py --runs-root outputs/patch_matrix --output-dir outputs/framework_reports/patch_matrix
PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py --report-dir outputs/framework_reports/patch_matrix --output outputs/framework_reports/patch_matrix/dashboard.html --no-pages
```

Expected: the patch report bundle is rebuilt from the new validation-enabled run set.

- [ ] **Step 4: Verify patch rows now contain authoritative metrics**

Run:

```bash
rg -n ",complete," outputs/framework_reports/patch_matrix/framework_run_summary.csv
```

Expected: at least the key patch rows have `validation_status=complete`, with non-empty validation metrics available for presentation and repo-completeness claims.

### Task 4: Refresh the Frozen Presentation Tree From the Canonical Artifacts

**Files:**
- Read/Write: `outputs/presentation_frozen/`

- [ ] **Step 1: Rebuild the frozen auto-cycle pack from the new canonical cycle**

Run:

```bash
NEW_CYCLE_ID=$(python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path("outputs/cycle_state.json").read_text())
print(payload["cycle_id"])
PY
)
rm -rf outputs/presentation_frozen/auto_cycle
mkdir -p outputs/presentation_frozen/auto_cycle/history outputs/presentation_frozen/auto_cycle/reports outputs/presentation_frozen/auto_cycle/summary
cp outputs/cycle_state.json outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_training_signal.json outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_report.csv outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_report.md outputs/presentation_frozen/auto_cycle/
cp "outputs/cycle_history/${NEW_CYCLE_ID}.json" outputs/presentation_frozen/auto_cycle/history/selected_cycle.json
rsync -a "outputs/framework_reports/${NEW_CYCLE_ID}/" outputs/presentation_frozen/auto_cycle/reports/
rsync -a "outputs/summaries/${NEW_CYCLE_ID}/" outputs/presentation_frozen/auto_cycle/summary/
```

Expected: the frozen auto-cycle pack now uses one cycle ID everywhere.

- [ ] **Step 2: Rebuild the frozen patch pack from the authoritative patch rerun**

Run:

```bash
rm -rf outputs/presentation_frozen/patch
mkdir -p outputs/presentation_frozen/patch/reports outputs/presentation_frozen/patch/runs
rsync -a outputs/framework_reports/patch_matrix/ outputs/presentation_frozen/patch/reports/
rsync -a outputs/patch_matrix/ outputs/presentation_frozen/patch/runs/
```

Expected: the frozen patch pack reflects the validation-enabled patch rerun.

### Task 5: Attempt Training Last, Only After the Canonical Cycle and Patch Work Are Clean

**Files:**
- Read/Write: `outputs/training_exports/`
- Read/Write: `outputs/training_runs/`
- Read/Write: `outputs/checkpoints/`

- [ ] **Step 1: Export training data from the current canonical signal**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/export_training_data.py --from-signal --signal-path outputs/cycle_training_signal.json
```

Expected: a new training export zip is created for the current cycle signal.

- [ ] **Step 2: Run signal-driven training**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/train_from_signal.py --signal-path outputs/cycle_training_signal.json
```

Expected: candidate checkpoint and training-run artifacts are created for the current signal cycle.

- [ ] **Step 3: Run the ritual wrapper**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/run_training_ritual.py --max-age-hours 1000
```

Expected: the wrapper prints a final verdict for the current signal cycle.

- [ ] **Step 4: Accept training only if the gating artifacts are complete**

Run:

```bash
CURRENT_SIGNAL_CYCLE=$(python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path("outputs/cycle_training_signal.json").read_text())
print(payload["cycle_id"])
PY
)
find "outputs/training_runs/$CURRENT_SIGNAL_CYCLE" -maxdepth 1 -type f | sort
```

Expected:
- `training_manifest.json`
- `clean_gate_result.json`
- `attack_gate_result.json`

If any of these are missing, training stays a limitation and does not block the rest of repo completion.
