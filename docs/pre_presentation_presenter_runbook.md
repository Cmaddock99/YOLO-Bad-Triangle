# Pre-Presentation Operator and Presenter Runbook

This runbook is for the final freeze step after the engineering tickets land. It assumes an artifact-led demo. Heavy workflows are run ahead of time, then copied into fixed paths that do not depend on timestamps or “latest run” behavior.

## Rule Zero

Do not live-run:

- `auto_cycle`
- learned-defense training
- `patch-matrix`

If you show a terminal command live, keep it to a dry-run or tiny smoke-safe path.

## Fixed Freeze Root

All presentation artifacts must be copied into:

```text
outputs/presentation_frozen/
```

Do not point slides at raw timestamped or cycle-ID paths.

## Required Frozen Layout

### 1. Core demo pack

Copy one chosen completed demo bundle into:

```text
outputs/presentation_frozen/core_demo/
```

Required files to exist there:

- `demo_manifest.json`
- `reports/framework_run_summary.csv`
- `reports/framework_run_report.md`
- `reports/dashboard.html`
- `summary/summary.json`
- `summary/summary.md`
- `summary/headline_metrics.csv`
- `summary/per_class_vulnerability.csv`
- `summary/warnings.json`

**Generation command**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/demo/run_demo.py --output-root outputs/demo_presentation
```

**Operator action**

- choose one successful `outputs/demo_presentation/<timestamp>/`
- copy its contents into `outputs/presentation_frozen/core_demo/`

**Claim supported**

- “The end-to-end benchmark pipeline works and produces structured, validated artifacts.”

### 2. Auto-cycle pack

Freeze one completed cycle into:

```text
outputs/presentation_frozen/auto_cycle/
```

Required files:

- `cycle_state.json`
- `cycle_training_signal.json`
- `cycle_report.csv`
- `cycle_report.md`
- `history/selected_cycle.json`
- `reports/framework_run_summary.csv`
- `reports/framework_run_report.md`
- `reports/dashboard.html`
- `summary/summary.json`
- `summary/summary.md`

**Generation command**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/automation/auto_cycle.py --profile yolo11n_lab_v1
```

**Operator action**

- copy `outputs/cycle_state.json`
- copy `outputs/cycle_training_signal.json`
- copy `outputs/cycle_report.csv` and `outputs/cycle_report.md`
- copy the chosen cycle JSON from `outputs/cycle_history/` to `history/selected_cycle.json`
- copy the chosen cycle’s report directory into `reports/`
- copy the chosen cycle’s summary directory into `summary/`

**Claim supported**

- “The repo can automatically rank attacks, rank defenses, tune candidates, and emit a training signal.”

### 3. Training pack

Freeze one successful manual training story into:

```text
outputs/presentation_frozen/training/
```

Required files:

- `training_manifest.json`
- `clean_gate_result.json`
- `attack_gate_result.json`

**Generation command**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/run_training_ritual.py --max-age-hours 1000
```

**Operator action**

- identify the cycle ID referenced by the current signal
- copy the files from `outputs/training_runs/<cycle_id>/`

**Claim supported**

- “The learned preprocessing defense can be retrained and gated against the current checkpoint before manual promotion.”

### 4. Patch pack

Freeze one imported patch evaluation set into:

```text
outputs/presentation_frozen/patch/
```

Required files:

- `reports/framework_run_summary.csv`
- `reports/framework_run_report.md`
- `reports/dashboard.html`
- `runs/` containing the selected patch-matrix run directories

**Generation commands**

```bash
export ADV_PATCH_ARTIFACT_PATH=/absolute/path/to/canonical_patch_artifact
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_checkpoint.pt
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py patch-matrix --matrix-config configs/patch_artifacts.yaml
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_framework_report.py --runs-root outputs/patch_matrix --output-dir outputs/framework_reports/patch_matrix
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_dashboard.py --report-dir outputs/framework_reports/patch_matrix --output outputs/framework_reports/patch_matrix/dashboard.html --no-pages
```

**Operator action**

- copy the selected patch run directories into `outputs/presentation_frozen/patch/runs/`
- copy the patch report outputs into `outputs/presentation_frozen/patch/reports/`

**Claim supported**

- “The repo can benchmark imported patch artifacts across placement modes and defenses.”

## Recommended Live Terminal Segment

Use exactly one safe command if you want a live terminal moment:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --profile yolo11n_lab_v1 --dry-run --set attack.name=fgsm --set defense.name=median_preprocess --set runner.run_name=presentation_walkthrough
```

Why this command:

- it is real
- it is safe
- it shows the public CLI
- it avoids heavy runtime and output surprises

If terminal confidence is low, skip live terminal entirely and show frozen artifacts only.

## Show Order

Use this order in the actual presentation:

1. Architecture slide
   - claim: one unified pipeline handles attacks, defenses, prediction, metrics, and reporting
2. Optional live dry-run command
   - claim: the public CLI surface is real and understandable
3. Core demo pack
   - show `demo_manifest.json`
   - show `reports/dashboard.html`
   - show `summary/summary.md`
4. Auto-cycle pack
   - show `cycle_report.md`
   - show `cycle_training_signal.json`
5. Training pack
   - show `training_manifest.json`
   - show `clean_gate_result.json`
   - show `attack_gate_result.json`
6. Patch pack
   - show `reports/dashboard.html`
   - show one or two run directories under `runs/`
7. Known Limitations slide

## Operator Checklist

- [ ] Freeze one environment after dependency reconciliation.
- [ ] Build all four frozen packs under `outputs/presentation_frozen/`.
- [ ] Confirm every referenced file opens locally.
- [ ] Confirm no slide points at a timestamped raw path.
- [ ] Confirm no live step depends on `latest` directory discovery.
- [ ] Keep one offline backup copy of `outputs/presentation_frozen/` on removable storage or cloud storage.

## Presenter Checklist

- [ ] Do not describe heavy workflows as live.
- [ ] Do not imply profiled learned-defense training is enabled.
- [ ] Explicitly say the training story is a manual/profileless workflow in the current repo policy.
- [ ] Keep one Known Limitations slide.
- [ ] If a live command misbehaves, stop immediately and pivot to frozen artifacts.
