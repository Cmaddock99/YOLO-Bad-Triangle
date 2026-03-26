# Cycle 7 Complete + Cycle 8 In-Progress: Status & Recommendations

**Cycle 7:** `cycle_20260325_223851` — complete
**Cycle 8:** `cycle_20260326_080833` — phase 4 in progress (validate_atk_deepfool running, ~13s/img)
**Written:** 2026-03-26

---

## 1. Cycle 7 Phase 4 Results vs Cycle 6

| Attack + Defense | Cycle 6 mAP50 | Cycle 7 mAP50 | Change |
|---|---|---|---|
| blur + bit_depth | 0.2615 | 0.2615 | — |
| blur + jpeg_preprocess | 0.2603 | 0.2603 | — |
| blur + median_preprocess | n/a | 0.2492 | new (worse than bit_depth) |
| deepfool + bit_depth | 0.2276 | 0.2276 | — |
| deepfool + jpeg_preprocess | 0.1837 | 0.1837 | — |
| deepfool + median_preprocess | n/a | 0.1215 | new (worst in table) |
| eot_pgd + bit_depth | 0.2555 | **skipped** | eot_pgd now SLOW_ATTACKS |
| eot_pgd + jpeg_preprocess | 0.2284 | **skipped** | eot_pgd now SLOW_ATTACKS |

**Best defended mAP50: 0.2615 (blur+bit_depth) — identical to cycle 6. No improvement.**

---

## 2. The Plateau Is Confirmed

Two consecutive full cycles with the same best result. The system has converged with the current checkpoint. Key indicators:

- **Attack tuning converged at warm-start in iteration 1** for all three attacks in cycle 8 — the param space is exhausted at these values.
- **c_dog absent from top-3 defenses in both cycles 6 and 7.** The DPC-UNet checkpoint is not competitive with simple signal processing.
- **Training signal recovery is negative** in both cycles (cycle 6: -0.061, cycle 7: -0.134). The best defenses make things slightly worse than no defense.
- **Baseline mAP50 unmoved at 0.6002 for 7 cycles.** Expected — YOLO weights unchanged — but confirms clean model is stable.

Running more cycles without retraining DPC-UNet will not produce new signal.

---

## 3. Recommendations

### R1 (Urgent) — Pause the loop after cycle 8, retrain first

The loop is burning CPU cycles with zero new learning. Cycle 8 phase 4 is currently running and will take several hours. Let it complete, then:

```bash
touch /home/lurch/YOLO-Bad-Triangle/outputs/.cycle.pause
```

Do not start cycle 9 until the Mac has delivered a retrained checkpoint. The data needed for retraining is already available — see R2.

---

### R2 — Export training data targeting deepfool now

Cycle 7's training signal correctly identified deepfool as worst attack (recovery -0.134). This is the right target. Run the export immediately:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --from-signal
```

This will pull from `outputs/cycle_training_signal.json` and export deepfool adversarial pairs for Colab.

---

### R3 — Expand the attack param space before cycle 9

All three attack tuners converged at warm-start values in a single iteration for cycle 8. The current search ranges are exhausted. Suggested expansions:

**deepfool** (current: epsilon in [0.025, 0.2], steps in [30, 70]):
- Add epsilon values: 0.005, 0.01 — test whether lighter perturbations are harder to defend
- Add higher steps: 100, 150 — full convergence may not be reached at 50

**eot_pgd** (currently SLOW_ATTACKS, skipped on NUC):
- Expand eot_samples up to 16 — more ensemble diversity may improve attack strength
- Try lower epsilon (0.125) with higher samples — different point on the tradeoff curve

**blur** (current: kernel_size in [21, 33]):
- kernel_size=29 is already near the top of the range; add 35, 41
- A new parameter worth exploring: sigma (if Gaussian blur) — currently may be fixed

---

### R4 — Add eot_pgd back to phase 4 on Mac

Since eot_pgd was added to SLOW_ATTACKS, cycle 7's trend table has a gap — no eot_pgd phase 4 data. The Mac should be running the eot_pgd validate runs that NUC skips. Currently the Mac's CW tuning is consuming that capacity but producing no signal (zero drop). Redirecting Mac's phase 4 budget to eot_pgd validation would fill the gap.

---

### R5 — Investigate jpeg_attack zero-effect (unchanged from cycle 6 rec)

Still producing 21 detections on smoke (= baseline). Has been in ALL_ATTACKS for both cycles 6 and 7 with no characterize signal. Either the default quality is too mild or the plugin is broken. Quick check:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=jpeg_attack \
  --set runner.max_images=4 \
  --set runner.run_name=debug_jpeg_attack
```

If detections == baseline after 4 images, the plugin is non-functional.

---

### R6 — Remove c_dog_ensemble from the defence catalogue (consider)

c_dog_ensemble has underperformed single c_dog in every smoke run it has appeared in (2 cycles, all 3 attacks). Until the base checkpoint improves, running c_dog_ensemble wastes phase 2 matrix slots and phase 3 tuning time. Consider removing it from ALL_DEFENSES until c_dog itself is competitive.

---

## 4. Cycle 8 Expected Outcome

Based on phases 1–3 being identical to cycle 7:
- Top attacks: deepfool, eot_pgd, blur (same params)
- Top defenses: jpeg_preprocess, bit_depth, median_preprocess (same params)
- Phase 4 best defended mAP50: expected ~0.2615 (blur+bit_depth), no improvement

Phase 4 ETA: deepfool at ~13s/img × 500 images ≈ 1.8h remaining for that run alone, then blur combos. Full phase 4 completion likely late tonight.

---

## 5. Mac Priority List (updated)

| Priority | Action |
|---|---|
| 1 | Run `export_training_data.py --from-signal` (deepfool pairs) |
| 2 | Colab retraining run with deepfool adversarial data |
| 3 | A/B eval new checkpoint vs golden before deploying |
| 4 | Fix or remove CW attack — zero drop is a blocker, not a slow attack |
| 5 | Run eot_pgd phase 4 validation (NUC is skipping these) |
| 6 | Check jpeg_attack plugin default params |
