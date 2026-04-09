# NUC Execution Spec: Direction A, Moves 1–3
**Date:** 2026-04-09
**For:** NUC Claude execution
**Repo:** `/home/lurch/YOLO-Bad-Triangle/`
**Status:** Ready to execute

---

## Do Not Skip This Section

This spec is self-contained. You do not need conversation history.
Read all of it before running anything.

### Project context (brief)

YOLO-Bad-Triangle runs an attack-defend-fortify triad on a YOLO object detection model.
The current fortification question (Direction A): is c_dog (DPC-UNet neural defense)
worth continuing relative to classical defenses on the worst validated attack?

Worst attack: deepfool (63.6% mAP50 damage, reduces baseline 0.6002 → 0.2184)
Strongest classical baseline: jpeg_preprocess at 0.3175 mAP50 on deepfool
Current c_dog (Round 3, timestep=25.0): 0.2238 mAP50 on deepfool
Gap to close: 0.0937

### Phase 0 audit findings (already complete, do not redo)

- Cycles 13–15 ran fresh Phase 4 inference — confirmed via timestamps. Not stale cache.
- Results identical across cycles 13–15 because pipeline is deterministic (same checkpoint,
  same attack params, same 500 images). This is expected behavior, not a bug.
- Checkpoint modified 2026-04-04 18:29:41 (Round 3). Cycles 13–15 all used Round 3.
- run_summary.json is MISSING from validate_deepfool_c_dog in cycles 12–15.
  Root cause: atomic write fix (commit acbb1a5) landed 2026-04-08; NUC may not have
  pulled it. Old code wrote metrics.json and run_summary.json non-atomically — a
  kill or crash between the two writes leaves metrics.json present but run_summary.json absent.

---

## Move 1: Fix Provenance (run_summary.json)

### Step 1.1 — Check what commit the NUC is on

```bash
cd /home/lurch/YOLO-Bad-Triangle
git log -1 --oneline src/lab/runners/run_experiment.py
```

If the commit hash is NOT `acbb1a5` or later, proceed to Step 1.2.
If it IS `acbb1a5` or later, skip to Step 1.3.

### Step 1.2 — Pull the fix

```bash
git pull origin main
```

Verify the pull succeeded and the new commit is present:

```bash
git log -1 --oneline src/lab/runners/run_experiment.py
```

Expected: shows `acbb1a5` or a newer commit with a message about atomic writes.

### Step 1.3 — Verify artifact contract on existing cycles

Check whether run_summary.json is present in validate_deepfool_c_dog for recent cycles.
This is a read-only audit — do not delete or re-run anything here.

```bash
for c in cycle_20260402_133001 cycle_20260404_003651 cycle_20260405_073545 cycle_20260406_054944; do
  d="outputs/framework_runs/$c/validate_deepfool_c_dog"
  m=$([ -f "$d/metrics.json" ] && echo "YES" || echo "NO")
  s=$([ -f "$d/run_summary.json" ] && echo "YES" || echo "NO")
  p=$([ -f "$d/predictions.jsonl" ] && echo "YES" || echo "NO")
  echo "$c: metrics=$m  run_summary=$s  predictions=$p"
done
```

**If run_summary.json is missing from these old cycle runs:** that is a historical artifact
of the pre-fix code. Do NOT attempt to regenerate or backfill them. Note it and move on.
New runs (from Move 2 onward) will write run_summary.json correctly with the patched code.

### Step 1.4 — Confirm checkpoint identity

```bash
sha256sum dpc_unet_adversarial_finetuned.pt
```

Expected SHA256: `138bc8a69c88001db7611e972bb0aa52c9151ef7cbd65ec23d3a8d854c07baef`

If SHA does not match: STOP. Do not run the sweep. Report the mismatch before proceeding.

### Move 1 exit condition

- NUC is on commit acbb1a5 or later ✅
- Checkpoint SHA confirmed ✅
- Historical missing run_summary.json noted but not backfilled ✅

---

## Move 2: Deepfool Timestep Sweep

### Context

Current c_dog @ timestep=25.0 gives 0.2238 mAP50 on deepfool.
jpeg_preprocess gives 0.3175. Gap = 0.0937.

Before spending Colab GPU on retraining, test whether the timestep parameter alone
can meaningfully close this gap. Three variants:

- **ts10**: timestep=10.0 — lighter denoising (deepfool perturbations are subtle/high-frequency)
- **ts25**: timestep=25.0 — current baseline (also confirms run_summary.json now written correctly)
- **ts7525**: timestep_schedule="75,25" — aggressive two-pass

Using 100 images for sweep speed. If a variant shows meaningful improvement,
follow up with full 500-image validation before making any decisions.

### Output directory

All sweep runs land in: `outputs/framework_runs/ts_sweep_20260409/`
This keeps them clearly separate from cycle runs.

### Commands (run sequentially — wait for each to complete before starting the next)

```bash
cd /home/lurch/YOLO-Bad-Triangle
export PYTHONPATH=src

# Variant 1: timestep=10.0
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set attack.params.epsilon=0.1 \
  --set attack.params.steps=50 \
  --set defense.name=c_dog \
  --set defense.params.timestep=10.0 \
  --set defense.params.sharpen_alpha=0.55 \
  --set runner.run_name=ts_sweep__deepfool__c_dog__ts10 \
  --set runner.output_root=outputs/framework_runs/ts_sweep_20260409 \
  --set runner.max_images=100 \
  --set validation.enabled=true

# Variant 2: timestep=25.0 (baseline confirmation)
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set attack.params.epsilon=0.1 \
  --set attack.params.steps=50 \
  --set defense.name=c_dog \
  --set defense.params.timestep=25.0 \
  --set defense.params.sharpen_alpha=0.55 \
  --set runner.run_name=ts_sweep__deepfool__c_dog__ts25 \
  --set runner.output_root=outputs/framework_runs/ts_sweep_20260409 \
  --set runner.max_images=100 \
  --set validation.enabled=true

# Variant 3: schedule="75,25" (aggressive two-pass)
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set attack.params.epsilon=0.1 \
  --set attack.params.steps=50 \
  --set defense.name=c_dog \
  --set defense.params.timestep_schedule="75,25" \
  --set defense.params.sharpen_alpha=0.55 \
  --set runner.run_name=ts_sweep__deepfool__c_dog__ts7525 \
  --set runner.output_root=outputs/framework_runs/ts_sweep_20260409 \
  --set runner.max_images=100 \
  --set validation.enabled=true
```

### After all three complete: read results

```bash
for variant in ts10 ts25 ts7525; do
  f="outputs/framework_runs/ts_sweep_20260409/ts_sweep__deepfool__c_dog__${variant}/metrics.json"
  if [ -f "$f" ]; then
    echo -n "  $variant: mAP50="
    python3 -c "import json; d=json.load(open('$f')); print(d.get('mAP50','MISSING'))"
  else
    echo "  $variant: metrics.json NOT FOUND"
  fi
done
```

Also confirm run_summary.json was written for each (validates Move 1 fix):

```bash
for variant in ts10 ts25 ts7525; do
  d="outputs/framework_runs/ts_sweep_20260409/ts_sweep__deepfool__c_dog__${variant}"
  s=$([ -f "$d/run_summary.json" ] && echo "YES" || echo "NO")
  echo "  $variant: run_summary=$s"
done
```

### Move 2 exit condition

All three variants have:
- metrics.json present ✅
- run_summary.json present ✅ (confirms Move 1 fix is working)
- mAP50 value recorded ✅

---

## Move 3: Read Results and Make the Phase 2 Decision

### Decision logic

After reading mAP50 from the three variants, apply this decision table:

**Reference values:**
- Deepfool undefended: 0.2184
- Current c_dog baseline (ts25, authoritative 500-image): 0.2238
- jpeg_preprocess: 0.3175
- Noise floor at 100 images: ±0.005 (expect more variance than 500-image runs)

**Decision table:**

| Best variant mAP50 (100 img) | Interpretation | Next action |
|---|---|---|
| < 0.24 | Timestep tuning cannot close the gap. Architecture mismatch with deepfool's frequency signature confirmed. | Redirect Direction A fortification to square attack. Document in DIRECTION_A_SPEC.md. |
| 0.24 – 0.27 | Marginal improvement. May be worth a single deepfool-only retraining round with the best timestep fixed. | Proceed to Round 4 Colab retraining. Note best timestep in spec. |
| > 0.27 | Meaningful improvement found. Must validate at full 500 images before deciding. | Run full 500-image validation (command below), then update spec. |

Do not over-interpret differences < 0.01 between variants at 100 images — that is within noise.
The ts25 variant gives a 100-image anchor to compare against the 500-image baseline of 0.2238.

### Full 500-image validation (only if a variant scores > 0.27 at 100 images)

Replace `runner.max_images=100` with `runner.max_images=0` and rerun the winning variant:

```bash
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set attack.params.epsilon=0.1 \
  --set attack.params.steps=50 \
  --set defense.name=c_dog \
  --set defense.params.timestep=<WINNING_VALUE> \
  --set defense.params.sharpen_alpha=0.55 \
  --set runner.run_name=ts_sweep__deepfool__c_dog__WINNER_full500 \
  --set runner.output_root=outputs/framework_runs/ts_sweep_20260409 \
  --set runner.max_images=0 \
  --set validation.enabled=true
```

(Replace `defense.params.timestep=<WINNING_VALUE>` with either a single timestep value
or `defense.params.timestep_schedule="75,25"` as appropriate for the winning variant.)

### Update docs/DIRECTION_A_SPEC.md

After reaching a decision, append a new section to `docs/DIRECTION_A_SPEC.md`.
Do not remove or modify existing content — only append.

Add at the bottom:

```markdown
## Phase 0–2 Execution Results (2026-04-09)

### Timestep Sweep Results (100 images, deepfool epsilon=0.1 steps=50)

| Variant | timestep / schedule | mAP50 (100 img) | run_summary present |
|---|---|---|---|
| ts10 | timestep=10.0 | [VALUE] | [YES/NO] |
| ts25 | timestep=25.0 | [VALUE] | [YES/NO] |
| ts7525 | schedule="75,25" | [VALUE] | [YES/NO] |

Reference: c_dog baseline (500 img) = 0.2238 | jpeg baseline = 0.3175

### Phase 2 Decision

Best variant: [ts10 / ts25 / ts7525 / none — no improvement]
Best mAP50 at 100 images: [VALUE]
Gap to jpeg remaining: [VALUE]

Decision: [one of the following]
- REDIRECT TO SQUARE — timestep tuning shows no improvement; deepfool gap is architectural
- PROCEED TO ROUND 4 RETRAINING — marginal improvement found; retrain with timestep=[VALUE]
- FULL 500 VALIDATION NEEDED — strong improvement found; see ts_sweep__deepfool__c_dog__WINNER_full500

Next action: [description]
```

---

## Reporting

When all three moves are complete, output the following summary:

```
MOVE 1 STATUS: [PASS / FAIL]
  NUC commit (run_experiment.py): [hash]
  Checkpoint SHA match: [YES / NO / MISMATCH: actual sha]
  Historical run_summary.json missing in cycles 12-15: [noted and not backfilled]

MOVE 2 RESULTS:
  ts10  (timestep=10.0):   mAP50=[value]  run_summary=[YES/NO]
  ts25  (timestep=25.0):   mAP50=[value]  run_summary=[YES/NO]
  ts7525 (sched=75,25):    mAP50=[value]  run_summary=[YES/NO]

MOVE 3 DECISION:
  Best variant: [ts10 / ts25 / ts7525 / none]
  Gap to jpeg remaining: [value]
  Decision: [redirect to square / proceed to Round 4 retraining / full 500 needed]
  DIRECTION_A_SPEC.md updated: [YES / NO — reason]
```

---

## What Not To Do

- Do not run a full 4-phase auto_cycle during this spec execution
- Do not modify `outputs/cycle_training_signal.json`
- Do not deploy or swap the checkpoint
- Do not delete existing cycle run directories or artifacts
- Do not run Colab retraining — that is a subsequent step, not part of this spec
- If any command exits with a non-zero exit code: stop, report the full error output, do not continue to the next step
