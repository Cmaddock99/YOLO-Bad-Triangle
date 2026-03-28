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
**What:** NUC delegates slow attacks in Phase 4. After cycle 11 finishes, check
`outputs/cycle_state.json` → `delegated_phase4_runs` and run them here.

```bash
# DR Phase 4 (if DR is in top_attacks)
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks dispersion_reduction \
  --defenses c_dog,bit_depth,jpeg_preprocess,median_preprocess \
  --preset full --validation-enabled --workers 1

# eot_pgd Phase 4 (if eot_pgd is in top_attacks)
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks eot_pgd \
  --defenses c_dog,bit_depth,jpeg_preprocess,median_preprocess \
  --preset full --validation-enabled --workers 1 \
  --set attack.params.epsilon=0.25 --set attack.params.eot_samples=8
```

**Why it matters:** Without this, cycle 11's training signal is incomplete — it
won't know how c_dog performs against DR and eot_pgd specifically.

---

### 2. Verify `_write_training_signal` produces a valid signal after cycle 11
**What:** Check `outputs/cycle_training_signal.json` exists after cycle 11
Phase 4 completes. This has NEVER been written in any prior cycle because
c_dog was always excluded from Phase 4.

**Check:** After Phase 4, run:
```bash
cat outputs/cycle_training_signal.json
```
Should contain: `worst_attack`, `worst_attack_params`, `weakest_defense`,
`weakest_defense_recovery`. If missing or empty, debug `_write_training_signal`.

**Why it matters:** This feeds the round 3 training decision. Without it we're
guessing which attack+defense pair to train on.

---

### 3. Re-evaluate `c_dog_ensemble` after cycle 11 Phase 4 results
**What:** `c_dog_ensemble` is commented out of `ALL_DEFENSES` because it was
"underperforming c_dog" — but that comparison was made entirely under the
`normalize=True` bug. Both defenses were broken identically. Now that the bug
is fixed, run a quick A/B with the golden checkpoint:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks deepfool,blur \
  --defenses c_dog,c_dog_ensemble \
  --preset full --validation-enabled --workers 1
```

**Decision criteria:**
- If `c_dog_ensemble` is within 0.01 mAP50 of `c_dog` → re-enable in ALL_DEFENSES
- If `c_dog_ensemble` is clearly better → re-enable and consider making it the default
- If still worse by >0.03 → keep disabled, document result

---

### 4. Update `generate_cycle_report.py` to include c_dog in trend tables
**What:** The cycle report trend tables only show `bit_depth`, `jpeg_preprocess`,
`median_preprocess` columns. c_dog has never appeared in any cycle's
`validation_results`, so the report generator never learned to include it.
After cycle 11 Phase 4, c_dog will have real mAP50 data for the first time.

**Check:** After cycle 11, run:
```bash
python scripts/generate_cycle_report.py
```
Verify c_dog appears as a column in the trend tables. If not, update the
report generator to include it dynamically from whatever defenses appear in
validation results (rather than a hardcoded list).

---

## P2 — Medium Priority

### 5. Round 3 training decision gate
**What:** Hold off on training until cycle 11 Phase 4 results are in. Then apply
this decision tree:

| Condition | Action |
|---|---|
| deepfool+c_dog mAP50 > 0.35 AND blur+c_dog > 0.45 | No training needed — normalize fix sufficient |
| deepfool+c_dog 0.25–0.35 | Consider training; check if c_dog_ensemble bridges gap |
| deepfool+c_dog < 0.25 | Train with feature matching loss (see training spec below) |

**If training IS needed — Round 3 spec:**
- `pixel_weight=0.5, feature_weight=0.50, edge_weight=0.15`
  (current `feature_weight=0.1` in `src/lab/defenses/training/losses.py:32` is too low)
- Layers: `["model.2", "model.4", "model.6"]` (drop model.9 — too coarse for small objects)
- Training resolution: 320×320 patches (matches YOLO's P3/P4 feature map sizes)
- Inference timestep: try 25–35 (less smoothing than default 50)
- Fresh start from golden checkpoint (`--fresh`)
- 60 epochs, LR 2e-5, oversample deepfool_strong:2

**Infrastructure already in place:**
- `src/lab/defenses/training/feature_loss.py` — `YOLOFeatureExtractor` + `yolo_feature_matching_loss`
- `src/lab/defenses/training/losses.py` — `composite_denoising_loss`, just needs weights updated
- `scripts/train_dpc_unet_local.py` — needs wiring to use `YOLOFeatureExtractor` instead of inline det-loss

---

### 6. Add DR adversarial training data once Phase 4 confirms it's a strong attack
**What:** If DR Phase 4 shows it defeats c_dog, add DR to the training data mix.
Currently `outputs/training_data/adversarial/` has: blur, deepfool, deepfool_strong,
eot_pgd, clean. DR should be added if it's confirmed as a strong attack.

```bash
# Generate DR training images (500 at tuned params from cycle 11)
PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py \
  --attacks dispersion_reduction \
  --attack-params epsilon=0.05,steps=50
```

---

### 7. Create `MESSAGES_FOR_NUC_CLAUDE.md` channel
**What:** NUC writes to `MESSAGES_FOR_MAC_CLAUDE.md`; Mac has no corresponding
channel back. When Mac needs to tell NUC something (e.g., "checkpoint deployed,
use adversarial_finetuned.pt now"), there's no mechanism. Create the file at the
repo root so NUC picks it up via git pull.

**Format to use:**
```markdown
# Mac → NUC: Messages

## 2026-MM-DD — [Subject]
**Written by Mac Claude**
[content]
```

---

### 8. Set inference timestep to 35 in c_dog default and re-evaluate
**What:** The current default is `timestep=50.0` in the adapter. Phase 3 tuning
range is 10–90 with step 15, so it tests 35, 50, 65. Watch what cycle 11 Phase 3
tunes c_dog to. If it tunes to 35 or below, change the default:

```python
# src/lab/defenses/preprocess_dpc_unet_adapter.py:104
timestep: float = 35.0  # was 50.0
```

---

### 9. Verify warm-start includes c_dog and DR after cycle 11
**What:** `outputs/cycle_warm_start.json` currently only has:
- attack_params: deepfool, eot_pgd, blur (no DR)
- defense_params: jpeg_preprocess, bit_depth, median_preprocess (no c_dog)

After cycle 11 Phase 3 completes, these should be populated. Verify:
```bash
cat outputs/cycle_warm_start.json
```
If c_dog and DR are missing, check `carry_forward_params()` in auto_cycle.py.

---

## P3 — Low Priority / Nice To Have

### 10. Clean up old checkpoint on NUC
`dpc_unet_adversarial_finetuned.pt` (Mar 23, old/worse) is still on NUC.
If `.env` ever gets reset, it could be picked up again by the fallback logic.
Either delete it or rename to `*.old`.

### 11. Clean up NUC cron jobs
NUC has something firing `auto_cycle.py --loop` at :00 and :30 every hour,
getting rejected with "Another cycle instance is already running." Harmless
but wasteful. Check NUC's crontab: `ssh 10.0.0.113 "crontab -l"`.

### 12. Colab notebook sync
`notebooks/finetune_dpc_unet.ipynb` — confirm it's using the feature matching
loss infrastructure from `src/lab/defenses/training/` rather than the old
inline det-loss approach. If round 3 training is run on Colab rather than Mac,
the notebook needs to match the local training script.

### 13. Add c_dog to cycle history trend analysis
The `outputs/cycle_history/*.json` files contain `validation_results` per cycle.
c_dog will appear for the first time in cycle 11. The cycle report trend tables
show defended mAP50 over time — make sure c_dog gets its own column going
forward so we can track improvement across cycles.

---

## Cycle 11 Checklist (things to do when it finishes)

- [ ] Check `delegated_phase4_runs` in cycle_state.json
- [ ] Run delegated Phase 4 on Mac (DR, eot_pgd)
- [ ] Read `cycle_training_signal.json` — identify worst attack/weakest defense
- [ ] Check c_dog mAP50 in Phase 4 against decision gate (P2 item #5)
- [ ] Run c_dog_ensemble A/B eval (P1 item #3)
- [ ] Check warm-start updated (P2 item #9)
- [ ] Pull NUC commits locally
- [ ] Update this spec with results

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
