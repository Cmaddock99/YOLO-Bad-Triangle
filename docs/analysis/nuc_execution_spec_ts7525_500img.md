# NUC Execution Spec: ts7525 500-image Validation
**Date:** 2026-04-09
**Status:** READY — feed to NUC Claude
**Depends on:** Bug fix applied (duplicate `passes` kwarg in preprocess_dpc_unet_adapter.py — in current commit on fix/auditor-followup). NUC must `git pull` before running.

---

## Context

The timestep sweep returned three results on 100-image diagnostic runs:

| Variant | mAP50 | Recovery |
|---|---|---|
| ts10 (single-pass, timestep=10) | 0.2676 | +0.0492 |
| ts25 (single-pass, timestep=25) | 0.2679 | +0.0495 |
| ts7525 (multi-pass: 75→25) | **0.2929** | **+0.0745** |
| jpeg reference | 0.3175 | +0.0992 |
| median reference | 0.3656 | +0.1472 |

ts7525 crosses the 0.27 decision gate, requiring full 500-image Phase 4 validation
before the verdict is written. Single-pass variants are flat and do not cross the gate.

---

## What To Do

### Step 0: Git pull

```bash
cd /path/to/YOLO-Bad-Triangle
git pull
```

Verify the bug fix is present:
```bash
grep "stats\[.passes.\] = 1" src/lab/defenses/preprocess_dpc_unet_adapter.py
```
Should return a match. If not, stop and report.

---

### Step 1: Run 500-image ts7525 validation

```bash
set -a && source .env && set +a && export PYTHONPATH=src && \
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set attack.params.epsilon=0.1 \
  --set attack.params.steps=50 \
  --set defense.name=c_dog \
  --set "defense.params.timestep_schedule=75,25" \
  --set defense.params.sharpen_alpha=0.55 \
  --set runner.run_name=ts7525_val_500img__deepfool__c_dog \
  --set runner.output_root=outputs/framework_runs/ts7525_val_500img_20260409 \
  --set runner.max_images=0 \
  --set validation.enabled=true
```

Expected runtime: similar to a standard Phase 4 validate run (~500 images, multi-pass c_dog).

---

### Step 2: Verify artifacts

```bash
ls outputs/framework_runs/ts7525_val_500img_20260409/ts7525_val_500img__deepfool__c_dog/
```

Required: `metrics.json`, `run_summary.json`, `predictions.jsonl`

If any are missing: stop and report. Do not read partial results.

---

### Step 3: Extract and report mAP50

```bash
python3 -c "
import json
with open('outputs/framework_runs/ts7525_val_500img_20260409/ts7525_val_500img__deepfool__c_dog/metrics.json') as f:
    m = json.load(f)
map50 = m['mAP50']
recovery = map50 - 0.2184
gap_to_jpeg = map50 - 0.3175
gap_to_median = map50 - 0.3656
print(f'mAP50:       {map50:.4f}')
print(f'Recovery:    {recovery:+.4f}  (vs deepfool undefended 0.2184)')
print(f'Gap to jpeg: {gap_to_jpeg:+.4f}  (jpeg=0.3175)')
print(f'Gap to med:  {gap_to_median:+.4f}  (median=0.3656)')
"
```

Report all four numbers back to Mac.

---

## What NOT To Do

- Do not start any training or checkpoint modification
- Do not run a full auto_cycle
- Do not modify cycle_training_signal.json
- Do not swap the checkpoint in .env
- Do not run ts10 or ts25 again — single-pass variants are concluded

---

## Decision Gate (Mac will apply after result)

- mAP50 ≥ 0.29 → ts7525 confirmed; verdict drafted (c_dog third on deepfool; square pivot activated)
- mAP50 < 0.27 → 100-image result was noise; deepfool ceiling confirmed; same verdict outcome
- Either case: Mac writes the verdict, no further deepfool training needed
