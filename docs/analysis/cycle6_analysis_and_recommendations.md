# Cycle 6 Analysis & Update Recommendations

**Cycle:** `cycle_20260324_094635`
**Analysed:** 2026-03-25
**Author:** NUC Claude

---

## 1. Baseline

| Metric | Value |
|---|---|
| mAP50 | 0.6002 |
| Detections | 1437 |
| avg_conf | 0.765 |
| Precision | 0.713 |
| Recall | 0.537 |

Baseline mAP50 has not moved across all 6 completed cycles. Clean YOLO weights are stable.

---

## 2. Attack Effectiveness (Phase 4, 500 images)

| Attack | mAP50 | vs baseline | Detections | Det drop | avg_conf |
|---|---|---|---|---|---|
| deepfool (eps=0.1, steps=50) | 0.2184 | **-63.6%** | 260 | **-81.9%** | 0.756 |
| eot_pgd (eps=0.25, samples=8) | 0.2529 | -57.9% | 605 | -57.9% | 0.748 |
| blur (kernel=29) | 0.2636 | -56.1% | 540 | -62.4% | 0.735 |

**Deepfool is the most effective attack.** avg_conf is remarkably stable across all conditions (0.73–0.77), meaning attacks work by suppressing detections (recall collapse), not by degrading model confidence on surviving detections.

---

## 3. Defense Recovery (Phase 4, 500 images)

No defense achieves meaningful recovery. Best case across the board:

| Attack | Defense | Defended mAP50 | vs attack | vs baseline |
|---|---|---|---|---|
| deepfool | bit_depth | 0.2276 | +4.2% | -62.1% |
| eot_pgd | bit_depth | 0.2555 | +1.0% | -57.4% |
| blur | bit_depth | 0.2615 | -0.8% | -56.4% |
| deepfool | jpeg_preprocess | 0.1837 | -15.9% | -69.4% |
| deepfool | random_resize | 0.1185 | -45.7% | -80.3% |

The overall training signal recovery is **-0.061** — the cycle's best defense (eot_pgd+jpeg_preprocess) is actually slightly worse than no defense at all.

---

## 4. c_dog / DPC-UNet is Not Competitive

c_dog did not make the top-3 defenses. Smoke-run detection counts vs attack-alone:

| Defense | blur (atk:16) | deepfool (atk:9) | eot_pgd (atk:14) |
|---|---|---|---|
| bit_depth | 17 (+1) | 8 (-1) | 11 (-3) |
| jpeg_preprocess | 17 (+1) | 5 (-4) | 14 (=) |
| **c_dog** | 14 (-2) | 5 (-4) | 11 (-3) |
| **c_dog_ensemble** | 14 (-2) | **3 (-6)** | 6 (-8) |
| median_preprocess | 16 (=) | 6 (-3) | 10 (-4) |

c_dog is consistently middle or below. c_dog_ensemble is worse than single c_dog in nearly every case. The current `dpc_unet_adversarial_finetuned.pt` checkpoint is not competitive with simple bit-depth reduction or JPEG compression.

**This is the core loop-closure failure.** c_dog should be the best defense and it is not even placing in the top 3.

---

## 5. Problems Found

### P1 (High) — DPC-UNet checkpoint not competitive

The closed-loop goal is for c_dog to recover mAP50. It is not. c_dog is losing to bit_depth and jpeg_preprocess by a wide margin, and c_dog_ensemble is actively worse than c_dog. The checkpoint needs retraining with adversarial pairs that match the current worst attack.

**Recommendation:** Export training data targeting deepfool (not eot_pgd — see P2 below) and run a new Colab fine-tuning round. Focus training on detection restoration under deepfool perturbations.

---

### P2 (Medium) — Training signal targets wrong worst-attack

The cycle identified `eot_pgd` as worst attack and `jpeg_preprocess` as weakest defense. However, deepfool has materially lower mAP50 (0.2184 vs 0.2529) and far more severe detection suppression (81.9% vs 57.9% drop). Colab training data exports driven by this signal will be generated against the wrong attack.

**Root cause:** The `worst_attack` selection in `generate_cycle_report.py` or `_write_training_signal()` in `auto_cycle.py` is likely ranking by composite score from the tune phase (8-image smoke runs) rather than mAP50 from phase 4 full-dataset validation. Smoke composite scores are noisy at 8 images and may not agree with full-dataset ground truth.

**Recommendation:** In `_write_training_signal()`, prefer phase 4 mAP50 for worst-attack selection when available, falling back to composite score only when phase 4 data is absent.

---

### P3 (Medium) — CW attack produces zero detection drop

`cw_tune_status.md` shows `initial_drop=0.0000` and `best_score=0.0000`, with zero defense recovery across all defenses. The CW attack is not degrading the model at all.

**Likely causes:**
- CW is designed for classifier logit targets. The adaptation to YOLO detection heads may be targeting the wrong output layer or loss.
- Parameters `c=1.0, max_iter=200, lr=0.01` may be too weak for a detection head with many anchor outputs.
- The attack may be optimising against a single class or bounding box confidence rather than the full detection suppression objective.

**Recommendation:** Before spending more Mac cycles on CW tuning, verify that the attack is actually perturbing images in a way that changes YOLO outputs at all. A simple sanity check: run CW on 1 image, visualise the perturbation magnitude and compare raw YOLO logits pre/post attack.

---

### P4 (Low) — jpeg_attack has zero effect in smoke

`attack_jpeg_attack` produced 21 detections on 8 smoke images — identical to the unattacked baseline (21). The attack is having no effect.

**Recommendation:** Check the jpeg_attack plugin's default quality parameter. If it defaults to a quality level that produces no perceptible compression artefacts, the attack will never score above baseline. The quality should start low enough to be adversarial on first use.

---

### P5 (Low) — jpeg_preprocess inconsistency between smoke and full-dataset

jpeg_preprocess ranked top-3 in phase 2 (smoke, 8 images) but degrades performance at full scale vs two of three attacks (deepfool: -15.9%, eot_pgd: -9.7% vs attack-alone). This smoke→full inconsistency could cause future cycles to waste phase 3 tuning iterations on a defense that does not actually help.

**Recommendation:** Consider requiring a minimum smoke sample size of 16–32 images for phase 2 defense ranking, or adding a brief pre-phase-4 validation gate (e.g. 50 images) to catch this before committing a defense to phase 3 tuning.

---

## 6. Warm-Start Params Carried into Cycle 8

These are the tuned params being used as starting points for cycle 8 (`cycle_20260325_223851`):

```
deepfool:       epsilon=0.1, steps=50
eot_pgd:        epsilon=0.25, eot_samples=8
blur:           kernel_size=29
jpeg_preprocess: quality=60
bit_depth:       bits=5
```

Note: these were tuned under the composite scoring metric, not raw mAP50. First-cycle convergence may take extra iterations.

---

## 7. Priority Order for Mac

1. **Retrain DPC-UNet against deepfool** — export training data with `--from-signal` after fixing the training signal to target deepfool (P2), then Colab fine-tune.
2. **Debug CW attack** — zero initial drop is a blocker; fix or remove from Mac's cycle until resolved (P3).
3. **Verify jpeg_attack plugin** — quick parameter audit (P4).
