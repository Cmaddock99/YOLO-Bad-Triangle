# Presentation Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze one truthful, reproducible presentation story around the repo's strongest working paths, and cut or repair any story that still lacks real artifacts.

**Architecture:** Treat this as artifact hardening, not feature work. Reuse the current green codebase and existing scripts, regenerate missing report artifacts where needed, and copy only verified evidence into `outputs/presentation_frozen/`.

**Tech Stack:** Python 3.11, pytest, repo CLI wrappers under `scripts/`, filesystem artifact checks, markdown/html reports.

---

### Task 1: Freeze the Core Demo Pack

**Files:**
- Read: `docs/pre_presentation_presenter_runbook.md`
- Read: `outputs/demo_audit/20260501T044919Z/`
- Create: `outputs/presentation_frozen/core_demo/`

- [ ] **Step 1: Verify the audited demo bundle is complete**

Run:

```bash
find outputs/demo_audit/20260501T044919Z -type f | sort
```

Expected: `demo_manifest.json`, `reports/framework_run_summary.csv`, `reports/framework_run_report.md`, `reports/dashboard.html`, `summary/summary.json`, `summary/summary.md`, `summary/headline_metrics.csv`, `summary/per_class_vulnerability.csv`, and `summary/warnings.json`.

- [ ] **Step 2: Create the frozen core demo directory**

Run:

```bash
mkdir -p outputs/presentation_frozen/core_demo
```

Expected: `outputs/presentation_frozen/core_demo/` exists.

- [ ] **Step 3: Copy the verified demo bundle into the frozen path**

Run:

```bash
cp -R outputs/demo_audit/20260501T044919Z/. outputs/presentation_frozen/core_demo/
```

Expected: the frozen core demo pack contains the same reports, runs, and summary artifacts as the audited bundle.

- [ ] **Step 4: Sanity-check the frozen demo pack**

Run:

```bash
find outputs/presentation_frozen/core_demo -type f | sort
```

Expected: the required files from the runbook are present and open locally.

### Task 2: Rebuild and Freeze the Auto-Cycle Pack

**Files:**
- Read: `outputs/cycle_state.json`
- Read: `outputs/cycle_training_signal.json`
- Read: `outputs/cycle_history/cycle_20260407_193440.json`
- Read/Write: `outputs/framework_reports/cycle_20260407_193440/`
- Read/Write: `outputs/summaries/cycle_20260407_193440/`
- Create: `outputs/presentation_frozen/auto_cycle/`

- [ ] **Step 1: Regenerate the longitudinal cycle markdown**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_cycle_report.py
```

Expected: both `outputs/cycle_report.csv` and `outputs/cycle_report.md` exist.

- [ ] **Step 2: Regenerate the cycle framework comparison markdown**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_framework_report.py --runs-root outputs/framework_runs/cycle_20260407_193440 --output-dir outputs/framework_reports/cycle_20260407_193440
```

Expected: `outputs/framework_reports/cycle_20260407_193440/framework_run_report.md` exists.

- [ ] **Step 3: Regenerate the cycle dashboard**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_dashboard.py --report-dir outputs/framework_reports/cycle_20260407_193440 --output outputs/framework_reports/cycle_20260407_193440/dashboard.html --no-pages
```

Expected: `outputs/framework_reports/cycle_20260407_193440/dashboard.html` exists.

- [ ] **Step 4: Regenerate the cycle auto-summary bundle**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_auto_summary.py --runs-root outputs/framework_runs/cycle_20260407_193440 --output-dir outputs/summaries/cycle_20260407_193440
```

Expected: `summary.json`, `summary.md`, `headline_metrics.csv`, `per_class_vulnerability.csv`, and `warnings.json` exist under `outputs/summaries/cycle_20260407_193440/`.

- [ ] **Step 5: Freeze the rebuilt auto-cycle pack**

Run:

```bash
mkdir -p outputs/presentation_frozen/auto_cycle/history
mkdir -p outputs/presentation_frozen/auto_cycle/reports
mkdir -p outputs/presentation_frozen/auto_cycle/summary
cp outputs/cycle_state.json outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_training_signal.json outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_report.csv outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_report.md outputs/presentation_frozen/auto_cycle/
cp outputs/cycle_history/cycle_20260407_193440.json outputs/presentation_frozen/auto_cycle/history/selected_cycle.json
cp -R outputs/framework_reports/cycle_20260407_193440/. outputs/presentation_frozen/auto_cycle/reports/
cp -R outputs/summaries/cycle_20260407_193440/. outputs/presentation_frozen/auto_cycle/summary/
```

Expected: the frozen auto-cycle pack matches the runbook's required file layout.

### Task 3: Make a Hard Go/No-Go Decision on the Training Story

**Files:**
- Read: `configs/pipeline_profiles.yaml`
- Read: `docs/pre_presentation_messaging_notes.md`
- Read/Write: `outputs/training_runs/<cycle_id>/`

- [ ] **Step 1: Keep the policy framing accurate**

Run:

```bash
rg -n "trainable: false|manual/profileless workflow" configs/pipeline_profiles.yaml docs/pre_presentation_messaging_notes.md docs/pre_presentation_presenter_runbook.md
```

Expected: the repo still states that learned-defense training is outside the canonical `yolo11n_lab_v1` profile flow.

- [ ] **Step 2: Run the manual training chain only if you want a training slide**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/export_training_data.py --from-signal --signal-path outputs/cycle_training_signal.json
PYTHONPATH=src ./.venv/bin/python scripts/training/train_from_signal.py --signal-path outputs/cycle_training_signal.json
PYTHONPATH=src ./.venv/bin/python scripts/training/run_training_ritual.py --max-age-hours 1000
```

Expected: a real `outputs/training_runs/<cycle_id>/training_manifest.json` plus `clean_gate_result.json` and `attack_gate_result.json`.

- [ ] **Step 3: Cut the training slide if the gates are still absent**

Run:

```bash
find outputs/training_runs -maxdepth 2 -type f | sort
```

Expected: if only `training_manifest.json` exists or `final_verdict` is still `run_failed`, remove the training story from the presentation instead of defending it live.

### Task 4: Either Upgrade the Patch Story to Authoritative Metrics or Present It as Plumbing Only

**Files:**
- Read: `configs/patch_artifacts.yaml`
- Read/Write: `outputs/patch_matrix/`
- Read/Write: `outputs/framework_reports/patch_matrix/`
- Create: `outputs/presentation_frozen/patch/`

- [ ] **Step 1: Confirm why the current patch report is proxy-only**

Run:

```bash
sed -n '1,200p' configs/patch_artifacts.yaml
```

Expected: `runner.max_images=8` is present and there is no `validation.enabled=true` override, which explains the current `validation_status=missing` rows.

- [ ] **Step 2: If you need authoritative patch metrics, rerun patch-matrix with validation enabled**

Run:

```bash
export ADV_PATCH_ARTIFACT_PATH=/absolute/path/to/canonical_patch_artifact
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_checkpoint.pt
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py patch-matrix --matrix-config configs/patch_artifacts.yaml --set validation.enabled=true
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_framework_report.py --runs-root outputs/patch_matrix --output-dir outputs/framework_reports/patch_matrix
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_dashboard.py --report-dir outputs/framework_reports/patch_matrix --output outputs/framework_reports/patch_matrix/dashboard.html --no-pages
```

Expected: `outputs/framework_reports/patch_matrix/framework_run_summary.csv` contains non-empty validation fields for the selected runs.

- [ ] **Step 3: Downgrade the patch claim if validation is still missing**

Run:

```bash
rg -n ",missing," outputs/framework_reports/patch_matrix/framework_run_summary.csv
```

Expected: if the report is still mostly `validation_status=missing`, present patch results only as imported-artifact ingestion and placement-mode comparison, not as a quantitative defense ranking.

### Task 5: Build the Final Freeze and Rehearse the Story You Can Defend

**Files:**
- Read: `docs/pre_presentation_presenter_runbook.md`
- Read: `docs/pre_presentation_messaging_notes.md`
- Read/Write: `outputs/presentation_frozen/`

- [ ] **Step 1: Verify the frozen root exists and is populated**

Run:

```bash
find outputs/presentation_frozen -maxdepth 3 -type f | sort
```

Expected: frozen `core_demo`, `auto_cycle`, and any optional `training` or `patch` packs exist with the exact files referenced in the runbook.

- [ ] **Step 2: Rehearse the one safe live command**

Run:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --profile yolo11n_lab_v1 --dry-run --set attack.name=fgsm --set defense.name=median_preprocess --set runner.run_name=presentation_walkthrough
```

Expected: dry-run prints the resolved config cleanly and exits zero.

- [ ] **Step 3: Rehearse the spoken limitations**

Run:

```bash
sed -n '1,220p' docs/pre_presentation_messaging_notes.md
```

Expected: you can say, without improvising, that the demo is artifact-led, the training story is manual/profileless, and any patch metrics are only as strong as the validation evidence you actually froze.
