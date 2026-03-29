# Improvement Backlog & Spec Sheet

Living document. Updated as cycle data comes in and issues are resolved.
Last updated: 2026-03-28

---

## Priority Legend
- **P0** — blocking or will corrupt results; fix before next cycle
- **P1** — high value, do soon (before or right after cycle 11 Phase 4)
- **P2** — medium priority, do when cycle is running
- **P3** — low priority / nice to have

---

## P0 — Blocking / Must Fix

_Nothing currently blocking. All P0 items resolved this session:_
- ~~normalize=True bug~~ — fixed (`normalize: bool = False` in adapter)
- ~~git_pull --ff-only silent failure~~ — fixed (merge strategy)
- ~~PINNED_DEFENSES missing on NUC~~ — fixed (in code + synced)
- ~~Orphaned eot_pgd sweep process hogging NUC CPU~~ — killed

---

## P1 — High Priority (Do Soon)

### 1. Run DR + eot_pgd Phase 4 on Mac after cycle 11 completes
**Status: IN PROGRESS — Mac delegated Phase 4 running (PID 9466, `/tmp/run_delegated_phase4.sh`)**

8 runs queued, running sequentially (~2s/img on MPS vs 60s NUC CPU = 30× speedup):
- `validate_atk_dispersion_reduction` ← run 1, in progress
- `validate_atk_square` ← queued
- `validate_dispersion_reduction_c_dog` ← CRITICAL: will answer training gate
- `validate_dispersion_reduction_bit_depth` ← queued
- `validate_dispersion_reduction_jpeg_preprocess` ← queued
- `validate_square_c_dog` ← CRITICAL: square vs c_dog first ever reading
- `validate_square_bit_depth` ← queued
- `validate_square_jpeg_preprocess` ← queued

Log: `outputs/delegated_phase4.log`. ETA ~3 hours from start (started 2026-03-28 afternoon).

---

### 2. Verify `_write_training_signal` produces a valid signal after cycle 11
**Status: DONE ✅**

`outputs/cycle_training_signal.json` confirmed written with real mAP50 data:
```json
{
  "worst_attack": "deepfool",
  "worst_attack_params": {"attack.params.epsilon": 0.1, "attack.params.steps": 50},
  "weakest_defense": "jpeg_preprocess",
  "weakest_defense_recovery": -0.1365,
  "all_attack_avg_recovery": {"deepfool": -0.0224}
}
```
NOTE: Signal is incomplete until Mac delegated Phase 4 finishes (DR+square not yet in signal).

---

### 3. Re-evaluate `c_dog_ensemble` after cycle 11 Phase 4 results
**Status: PENDING — waiting for Mac delegated Phase 4 to finish first**

The old "c_dog_ensemble underperforms c_dog" conclusion was made entirely under the `normalize=True`
bug. Both were broken identically. Now that normalize is fixed AND c_dog defaults are updated
(timestep=25.0, sharpen_alpha=0.55), this comparison is invalid and must be re-run.

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks deepfool,blur \
  --defenses c_dog,c_dog_ensemble \
  --preset full --validation-enabled --workers 1
```

Decision criteria:
- Within 0.01 mAP50 of c_dog → re-enable in ALL_DEFENSES
- Clearly better → re-enable, consider making default
- Still worse by >0.03 → keep disabled, document result

NOTE: `c_dog_ensemble` currently uses `timestep_schedule="50"`. It should also be evaluated at
`timestep_schedule="25"` or `"50,25"` (multipass) now that 25 is the confirmed optimal for detection.

---

### 4. Update `generate_cycle_report.py` to include c_dog in trend tables
**Status: PENDING — verify after Mac delegated Phase 4 completes**

```bash
python scripts/generate_cycle_report.py
```
Verify c_dog appears as a column in the trend tables. If not, update the report generator to
include it dynamically from whatever defenses appear in validation results (rather than hardcoded list).

---

### 5. Fix training signal filter — signal should target trainable defenses only
**Status: NEW — identified 2026-03-28, not yet fixed**

**The bug:** `_write_training_signal()` in `scripts/auto_cycle.py` picks `jpeg_preprocess` as the
weakest defense (recovery = -0.137). But DPC-UNet training cannot improve JPEG compression — only
`c_dog` and `c_dog_ensemble` are trainable defenses.

**Effect:** Round 3 training spec says "train on deepfool+jpeg_preprocess" which is meaningless.
We should train on the weakest DPC-UNet variant, not the weakest defense overall.

**Fix:** Before selecting `weakest_defense`, filter `defense_results` to only include defenses in
`{"c_dog", "c_dog_ensemble"}`. If none of those are in Phase 4 results, fall back to current logic.

**Location:** `scripts/auto_cycle.py` → `_write_training_signal()` method.

---

## P2 — Medium Priority

### 6. Round 3 training decision gate
**Status: DEFERRED — awaiting DR+square vs c_dog results from Mac delegated Phase 4**

Apply this decision tree once delegated Phase 4 results are in:

| Condition | Action |
|---|---|
| DR+c_dog mAP50 > 0.35 AND deepfool+c_dog > 0.25 | No training needed — normalize fix sufficient |
| deepfool+c_dog 0.25–0.35 | Consider training; check if c_dog_ensemble bridges gap |
| deepfool+c_dog < 0.25 | Train with feature matching loss (see training spec below) |
| DR defeats c_dog by large margin | Training IS needed; add DR pairs to training data |

**If training IS needed — Round 3 spec:**
- `pixel_weight=0.5, feature_weight=0.50, edge_weight=0.15`
  (current `feature_weight=0.30` in `src/lab/defenses/training/losses.py` — updated from 0.1)
- Layers: `["model.2", "model.4", "model.6"]` (C2f backbone blocks; drop model.9 — too coarse)
- Training resolution: 320×320 patches (matches YOLO P3/P4 feature map sizes)
- Inference timestep: 25 (confirmed cycle 11)
- Fresh start from golden checkpoint (`--fresh`)
- 60 epochs, LR 2e-5, oversample deepfool_strong:2

**Infrastructure already in place:**
- `src/lab/defenses/training/feature_loss.py` — `YOLOFeatureExtractor` + `yolo_feature_matching_loss`
- `src/lab/defenses/training/losses.py` — `composite_denoising_loss`, feature_weight updated to 0.30
- `scripts/train_dpc_unet_local.py` — needs wiring to use `YOLOFeatureExtractor` instead of det-loss

---

### 7. Add DR adversarial training data once Phase 4 confirms it's a strong attack
**Status: PENDING — awaiting Phase 4 DR+c_dog result**

If DR Phase 4 shows it defeats c_dog, add DR to the training data mix:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py \
  --attacks dispersion_reduction \
  --attack-params epsilon=0.05,steps=50
```

Current `outputs/training_data/adversarial/` has: blur, deepfool, deepfool_strong, eot_pgd, clean.

**Scientific note on DR vs DPC-UNet:** DR is a feature-space attack (minimizes variance of YOLO
backbone activations). DPC-UNet is a pixel-space purifier. The key question from Phase 4 is:
_can pixel-level denoising undo feature-level adversarial perturbations?_

If DR defeats c_dog: the perturbations are in mid-frequency (feature-aligned patterns), not just
high-frequency noise. DPC-UNet operating frequency is wrong. Adding DR training examples forces
the model to learn mid-frequency artifact removal — which may also improve deepfool performance.

If DR does NOT defeat c_dog: pixel denoising generalizes to feature attacks. This would mean
the timestep=25 + sharpen_alpha=0.55 config is handling structured perturbations well.

---

### 8. Add TUNE_MAX_ITERS_BY_ATTACK to cap Phase 3 tuning iterations for slow attacks
**Status: NEW — identified 2026-03-28, not yet implemented**

**Problem:** Phase 3 currently runs coord descent for `square` and `dispersion_reduction` with the
default iteration count. `square` attack is very slow even at 8-12 images because it runs 500+
iterations per image by default. Phase 3 for cycle 11 took 20+ hours largely due to square.

**Fix:** Add `TUNE_MAX_ITERS_BY_ATTACK` dict (analogous to `TUNE_MAX_IMAGES_BY_ATTACK`) that caps
the number of Phase 3 coord descent iterations for slow attacks:

```python
TUNE_MAX_ITERS_BY_ATTACK: dict[str, int] = {
    "square": 3,
    "dispersion_reduction": 5,
}
```

This would reduce square Phase 3 from ~18 hours to ~1-2 hours while still finding rough optima.

**Location:** `scripts/auto_cycle.py` → Phase 3 coord descent loop.

---

### 9. Auto-append cycle results to SPEC.md from `save_cycle_history()`
**Status: NEW — identified 2026-03-28, not yet implemented**

Currently SPEC.md is updated manually. Both Mac and NUC Claude should append cycle summaries
automatically after Phase 4 completes.

**Spec:** Add `_append_cycle_to_spec()` helper in `auto_cycle.py`, called from
`save_cycle_history()` after Phase 4. Should append:
- Cycle ID + date
- Top 3 attacks with Phase 1 scores
- Top 3 defenses with Phase 4 mAP50
- Training signal (worst_attack + weakest_defense)
- Any delegated runs status

NUC should only APPEND new cycle sections. Never edit existing SPEC.md content.
This prevents merge conflicts: NUC appends, Mac appends, git merges with -X ours on conflicts.

---

### 10. Automated Mac delegated Phase 4 trigger
**Status: NEW — currently requires manual Mac Claude intervention**

Currently Mac Claude must notice `delegated_phase4_runs` in `cycle_state.json` and manually
kick off the runs. This is error-prone and requires the conversation to be active.

**Options (lowest to highest complexity):**
1. **Cron on Mac**: Every hour, check `cycle_state.json` for pending delegated runs, auto-start.
   Simple but requires careful locking to avoid double-runs.
2. **File watcher**: Mac watches `outputs/cycle_state.json` for changes. When
   `delegated_phase4_runs` appears with incomplete items, starts the script.
3. **NUC ssh trigger**: After NUC writes delegated runs list, it SSHs to Mac to trigger.

Option 1 is the simplest and most reliable. Shell script:
```bash
# Check if delegated runs are pending and not running
if jq -e '.delegated_phase4_runs | length > 0' outputs/cycle_state.json > /dev/null 2>&1; then
  if ! pgrep -f "run_delegated_phase4" > /dev/null; then
    nohup bash /tmp/run_delegated_phase4.sh >> outputs/delegated_phase4.log 2>&1 &
  fi
fi
```

---

## P3 — Low Priority / Nice To Have

### 11. Clean up old checkpoint on NUC
`dpc_unet_adversarial_finetuned.pt` (Mar 23, old/worse) is still on NUC.
If `.env` ever gets reset, it could be picked up again by the fallback logic.
Either delete it or rename to `*.old`.

### 12. Clean up NUC cron jobs
NUC has something firing `auto_cycle.py --loop` at :00 and :30 every hour,
getting rejected with "Another cycle instance is already running." Harmless
but wasteful. Check NUC's crontab: `ssh 10.0.0.113 "crontab -l"`.

### 13. Colab notebook sync
`notebooks/finetune_dpc_unet.ipynb` — confirm it's using the feature matching
loss infrastructure from `src/lab/defenses/training/` rather than the old
inline det-loss approach. If round 3 training is run on Colab rather than Mac,
the notebook needs to match the local training script.

### 14. Add c_dog to cycle history trend analysis
The `outputs/cycle_history/*.json` files contain `validation_results` per cycle.
c_dog will appear for the first time in cycle 11. The cycle report trend tables
show defended mAP50 over time — make sure c_dog gets its own column going
forward so we can track improvement across cycles.

### 15. Test c_dog_ensemble at timestep_schedule="25" or "50,25" multipass
The ensemble currently uses `timestep_schedule="50"`. Cycle 11 confirmed single-pass
t=25 beats t=50 for detection. Evaluate ensemble at:
- `timestep_schedule="25"` (single-pass, same as c_dog)
- `timestep_schedule="50,25"` (coarse denoising first, then fine-detail recovery)

Multi-pass "50,25" is theoretically optimal: first pass at t=50 removes large adversarial
structure; second at t=25 recovers fine detail without over-smoothing.

### 16. Verify sharpen_alpha=0.55 is correctly tuned (not a grid artifact)
Phase 3 tuning range is 0.0–0.8 with step 0.25, which tests: 0.0, 0.25, 0.5, 0.75.
The reported optimum is 0.55 — which is NOT in that grid. Either:
1. The step size is finer than documented, OR
2. The optimizer interpolated, OR
3. This is a Phase 3 coord descent step from 0.5 to nearby values

Verify Phase 3 tested this correctly. If the grid doesn't include 0.55, fine-scan
0.45–0.65 with step 0.05 to confirm the optimum.

### 17. YOLO layer selection for feature matching (round 3)
When round 3 training runs, the feature extractor targets `["model.2", "model.4", "model.6"]`.
These are C2f backbone blocks at 3 scales. Consider testing `model.8` (the P5 neck connection)
for large-object detection since COCO val2017 has large vehicles. P5 features carry coarse
structure that matters for bounding box localization on large objects.

---

## Scientific Hypotheses & Reasoning

### Why timestep=25 beats timestep=50 for detection
DiffPure literature (Nie 2022, Yoon 2021): lower timestep = less forward diffusion = less
information destroyed = better high-frequency preservation. For detection (vs classification),
preserving edges matters more than removing all noise. t=50 over-smooths; t=25 removes only
the sharpest adversarial perturbations while keeping the edge gradients YOLO needs.

### sharpen_alpha mechanism
After denoising at t=25 (light denoising), output has slightly blurred edges. sharpen_alpha=0.55
applies unsharp masking: `output = denoised + 0.55 * (denoised - gaussian_blur(denoised))`.
This modestly enhances edges without amplifying residual noise. Directly recovers the edge
gradients YOLO uses for boundary localization and anchor matching.

### Why feature matching loss beats detector loss for purifier training
- Detection loss (`box+cls+dfl`) measures average prediction error over all anchors — already near
  the "clean baseline" value (~6-7) so gradient is ~12% over 90 epochs. The loss plateau is not
  a training signal.
- Feature matching measures L1 between YOLO backbone intermediate features on purified vs clean —
  directly measures whether the purified image "looks the same" to YOLO internally. Has clear
  gradient from 0 toward full feature alignment. Correlates with mAP50 more directly.
- Evidence: round 2 det-loss training showed det loss 6.6→6.2 over 90 epochs (barely moved).
  Feature matching starts at ~0.3-0.5 and should trend toward ~0.1 = meaningful gradient.

### Why DR might or might not defeat c_dog
**IF DR defeats c_dog:** Adversarial perturbations are in mid-frequency (feature-aligned patterns),
not just high-frequency noise. DPC-UNet's denoising operates primarily on high-frequency artifacts.
Training with DR adversarial examples would force mid-frequency artifact learning.

**IF DR does NOT defeat c_dog:** Pixel denoising generalizes to feature attacks — the t=25 +
sharpen_alpha=0.55 config handles structured perturbations well because DR must perturb pixels
to affect features. The denoiser removes those pixel perturbations before they propagate.

---

## Pending Decisions (waiting on data)

| Decision | Waiting For | Gate |
|---|---|---|
| Round 3 training needed? | DR+c_dog & square+c_dog Phase 4 results | See P2 #6 |
| Re-enable c_dog_ensemble? | A/B eval after Phase 4 completes | See P1 #3 |
| Add DR to training data? | Phase 4 DR+c_dog confirms defeat | See P2 #7 |
| Feature matching or det-loss for round 3? | Training gate decision | Feature matching preferred |
| c_dog_ensemble timestep update? | A/B eval result | Test "25" and "50,25" |

---

## Cycle 12 Watch Points

- Does c_dog stay top defense? (cycle 11 established it for deepfool — must confirm it holds)
- Does DR rank top-3 again? (cycle 11 debut — could be noise, need second data point)
- Does warm_start correctly seed c_dog at timestep=25, sharpen_alpha=0.55? (first cycle with new defaults)
- Does Phase 3 re-tune c_dog to same params? (would confirm Phase 3 convergence to stable optimum)
- Does Phase 4 generate valid training signal for second time? (verify pattern, especially with DR data)
- Does Phase 3 for square/DR take less time than cycle 11? (confirm TUNE_MAX_IMAGES_BY_ATTACK working)

---

## Cycle 11 Checklist (things to do when it finishes)

- [x] Check `delegated_phase4_runs` in cycle_state.json
- [ ] Run delegated Phase 4 on Mac (DR, square) — **IN PROGRESS on Mac**
- [x] Read `cycle_training_signal.json` — deepfool/jpeg_preprocess identified
- [x] Check c_dog mAP50 in Phase 4 against decision gate
- [ ] Run c_dog_ensemble A/B eval (P1 item #3) — pending Mac delegated Phase 4 first
- [x] Check warm-start updated — yes, c_dog and DR now included
- [x] Pull NUC commits locally
- [x] Update this spec with results — see Cycle 11 Results below

---

## Reference Numbers (from 500-image evals with normalize fix)

| Config | mAP50 | Status |
|---|---:|---|
| Clean baseline | 0.598 | — |
| deepfool (ε=0.1) undefended | 0.219 | attack |
| blur (k=29) undefended | 0.263 | attack |
| deepfool + c_dog (normalize FIXED) | **0.244** | ✅ beats undefended |
| blur + c_dog (normalize FIXED) | **0.521** | ✅ beats undefended |
| deepfool + c_dog (old normalize bug) | 0.128 | ❌ was the problem |
| blur + c_dog (old normalize bug) | 0.176 | ❌ was the problem |

---

## Cycle 11 Results (cycle_20260328_092542, completed 2026-03-29)

**Top attacks:** square, deepfool, dispersion_reduction (DR debuted top-3)
**Top defenses:** c_dog ✅, bit_depth, jpeg_preprocess (median dropped out)

**Phase 4 mAP50 — NUC-run (deepfool only; square+DR delegated to Mac):**

| Attack | Defense | mAP50 | vs Undefended | vs Baseline |
|---|---|---:|---:|---:|
| — | none | 0.6002 | — | — |
| deepfool | none | 0.2184 | — | -0.382 |
| deepfool | c_dog | **0.2403** | **+0.022 ✅** | -0.360 |
| deepfool | bit_depth | 0.2229 | +0.005 | -0.377 |
| deepfool | jpeg_preprocess | 0.1663 | **-0.052 ❌** | -0.434 |

**c_dog is now best defense against deepfool for the first time ever.**

**Phase 3 tuned c_dog params (updated as new defaults):**
- `timestep`: 50.0 → **25.0** (confirmed literature 25–35 range for detection)
- `sharpen_alpha`: 0.0 → **0.55**

**Training signal** (`outputs/cycle_training_signal.json`):
- worst_attack: deepfool (only NUC-run attack with mAP50)
- weakest_defense: jpeg_preprocess (recovery = -0.137 — actively hurts)
- deepfool avg recovery across defenses: -0.022 (jpeg dragging it negative)
- NOTE: signal incomplete until Mac delegated Phase 4 (DR+square) finishes
- ⚠️ Signal filter bug: jpeg identified as weakest but is not a trainable defense (see P1 #5)

**Training gate assessment (preliminary, DR+square pending):**
- deepfool+c_dog mAP50: 0.2403 → recovery = 5.8% of lost mAP50
- Gate: <0.25 → "train" category (0.2403 < 0.25)
- BUT: normalize fix alone gave real positive recovery where there was none before
- Decision deferred until DR+square vs c_dog results available

**Mac delegated Phase 4 (IN PROGRESS):**
- validate_atk_dispersion_reduction ← run 1, in progress (~180/500 at last check)
- validate_atk_square ← queued
- validate_dispersion_reduction_c_dog ← CRITICAL, queued
- validate_dispersion_reduction_bit_depth ← queued
- validate_dispersion_reduction_jpeg_preprocess ← queued
- validate_square_c_dog ← CRITICAL, queued
- validate_square_bit_depth ← queued
- validate_square_jpeg_preprocess ← queued

**Items completed as a result of cycle 11:**
- [x] c_dog defaults updated: timestep=25.0, sharpen_alpha=0.55
- [x] Training signal bug confirmed fixed (was "no baseline detections" for 7+ cycles)
- [x] DR confirmed as a real top-3 attack on first outing
- [x] normalize=True bug fixed (was compressing output to ~74% pixel range)
- [x] git_pull --ff-only silent failure fixed (now --no-rebase -X ours)
- [x] MESSAGES_FOR_NUC_CLAUDE.md channel created
- [x] CompositeLossWeights.feature_weight updated 0.1 → 0.30
- [x] CHARACTERIZE_MAX_IMAGES_BY_ATTACK added (square=8, eot_pgd=12, dr=12)
- [x] DR attack integrated into ALL_ATTACKS, SLOW_ATTACKS, ATTACK_PARAM_SPACE

---

## NUC Protocol Notes

**For NUC Claude reading this:**
- Only APPEND new cycle result sections to this file. Never edit existing content.
- After each Phase 4, add a "Cycle N Results" section at the bottom following the cycle 11 format.
- Check P1 items — if any can be resolved during a cycle run, do so.
- Reference `MESSAGES_FOR_NUC_CLAUDE.md` at repo root for Mac→NUC coordination.
- Reference `MESSAGES_FOR_MAC_CLAUDE.md` for NUC→Mac coordination.
