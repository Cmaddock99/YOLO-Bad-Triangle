# Direction A: Square Pivot Contingency Plan
**Date:** 2026-04-09
**Status:** CONTINGENCY — activate only if NUC timestep sweep returns best mAP50 < 0.24 on deepfool
**Trigger:** Deepfool gap to jpeg (0.0937) confirmed architectural; timestep tuning cannot close it

---

## Why We're Here

deepfool is the worst validated attack (63.6% damage, reduces 0.6002 → 0.2184 mAP50).
jpeg_preprocess dominates deepfool at 0.3175 because deepfool's perturbations live in
high-frequency space — jpeg compression destroys them by design. DPC-UNet's broad
diffusion denoising cannot replicate frequency-selective behavior through more training.
The timestep sweep confirmed no path forward.

Square is the second-worst validated attack (39.5% damage, 0.6002 → 0.3630). The key
difference: jpeg_preprocess HURTS on square (-0.0383 recovery), meaning the classical
baseline is weaker and c_dog has less competition. Round 2 demonstrated that DPC-UNet's
inpainting-style denoising is structurally well-matched to large-patch occlusion attacks.

---

## Square Attack Evidence (Phase 4 authoritative, verified)

| Cycle | Checkpoint | sq undefended | c_dog | bit_depth | jpeg | median |
|---|---|---|---|---|---|---|
| c11 (cycle_20260331_131443) | Round 2 | 0.3630 | **0.3890** | 0.3863 | — | 0.3336 |
| c12 (cycle_20260402_133001) | Round 2 | 0.3630 | 0.3624 | 0.3499 | 0.3247 | — |
| c13–c15 (avg, Round 3) | Round 3 | 0.3630 | 0.3503 | — | 0.3247 | 0.2768 |

**Recovery vs undefended (sq undefended = 0.3630):**

| Cycle | c_dog | bit_depth | jpeg | median |
|---|---|---|---|---|
| c11 (Round 2) | **+0.0260** | +0.0233 | — | -0.0294 |
| c12 (Round 2) | -0.0006 | -0.0131 | -0.0383 | — |
| c13–c15 (Round 3) | -0.0127 | — | -0.0383 | -0.0862 |

**Honest read:**
- Round 2 c_dog was the only defense to produce meaningful positive recovery on square (+0.0260 in c11)
- Round 3 regressed c_dog on square to -0.0127 — a known consequence of multi-attack dilution
- jpeg and median actively worsen square performance; bit_depth marginally hurts
- c_dog is the only defense architecture suited to square's large-patch occlusion structure
- The Round 3 regression is the problem to fix, not the architecture

---

## The Comparison Baseline for Square

For square, the strongest classical baseline is **bit_depth** (not jpeg).
Last verified bit_depth vs square values: 0.3863 (c11, Round 2), 0.3499 (c12, Round 2).

Note: bit_depth was demoted from `top_defenses` in cycles 13–15, so there is no recent
Phase 4 comparison value. It must be explicitly re-included in the next Phase 4 cycle
to establish the current baseline before declaring a c_dog win.

---

## Root Cause of Round 3 Regression

Round 3 trained on: deepfool + blur + square simultaneously (square_retention preset).
With composite loss (pixel=1.0, edge=0.15, feature=0.30) and finite model capacity,
gradients from three attack types partially cancel. The A/B after Round 3 showed
±0.003 delta on deepfool — within noise. Square also regressed.

Round 3 demonstrates that multi-attack mixing is actively harmful. The fix is
single-attack focused training.

---

## Retraining Plan: Round 4, Square-Only

### Export step
Target: `validate_atk_square` images from `cycle_20260331_131443` (500 images, complete
Phase 4, most recent cycle with full bit_depth comparison data).

```bash
# Update cycle_training_signal.json to target square:
# worst_attack: square
# worst_attack_params: {attack.params.eps: 0.3, attack.params.n_queries: 450}
# Then export:
python scripts/export_training_data.py
```

### Training parameters
- **Attack:** square only — no deepfool, no blur
- **Resume from:** current `dpc_unet_adversarial_finetuned.pt` (Round 3 checkpoint)
  Do not restart from Round 2. Build forward.
- **Loss weights:** pixel=1.0, edge=0.15, feature=0.30 (unchanged)
- **LR:** 2e-5, **epochs:** 40, **batch:** 16 (unchanged)
- **Notebook:** `notebooks/finetune_dpc_unet.ipynb` — change attack list to square only

### Deployment gate
- Clean A/B: 500 images, c_dog only, no attack
- Gate: delta_mAP50 >= -0.005
- If PASS: replace checkpoint, update `.env`
- If FAIL: do not deploy

### Validation after deployment
Run full Phase 4 cycle with bit_depth explicitly re-included in `top_defenses` or
run a direct comparison:

```bash
# Direct comparison run (bit_depth vs square, 500 images):
python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=square \
  --set attack.params.eps=0.3 \
  --set attack.params.n_queries=450 \
  --set defense.name=bit_depth \
  --set runner.run_name=sq_pivot_val__square__bit_depth \
  --set runner.output_root=outputs/framework_runs/sq_pivot_val \
  --set runner.max_images=0 \
  --set validation.enabled=true
```

---

## Success Criteria

Direction A square pivot is a **positive result** when all hold:

- c_dog recovery on square > 0 (minimum: stop hurting)
- c_dog > bit_depth on square by > +0.005 mAP50
- Result repeats across two independent authoritative Phase 4 validations
- Clean A/B within gate (delta >= -0.005)

## Failure Criteria

Direction A square pivot is a **negative result** when:

- Two square-focused retraining rounds still show c_dog negative or flat recovery
- OR c_dog only improves square at the cost of clean regression

**Verdict at failure: RETIRE c_dog as primary fortification path.**
Record the result, write the closure doc, and consider alternative architectures
or accept jpeg+bit_depth as the production defense stack.

---

## Next Step After Activating This Contingency

A new NUC execution spec will be written covering:

1. Update `cycle_training_signal.json` to target square attack
2. Export square training data via `scripts/export_training_data.py`
3. Run Colab Round 4 (square-only) and deploy if clean gate passes
4. Run full 500-image Phase 4 validation cycle with bit_depth re-included
5. Compare c_dog vs bit_depth on square — apply success/failure criteria above

---

## What This Contingency Does NOT Address

- deepfool fortification (concluded: architectural ceiling reached)
- c_dog_ensemble re-evaluation
- eot_pgd or DR Phase 4 coverage
- Changes to runner, reporting, or schema layers
