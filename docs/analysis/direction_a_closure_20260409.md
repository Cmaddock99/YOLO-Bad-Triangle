# Direction A Closure Document (DRAFT)
**Status:** COMPLETE — verdict written 2026-04-09
**Date started:** 2026-04-09
**Scope:** YOLOv8 only. All values are YOLOv8-specific and do not transfer to future model versions.

---

## Project Goal

YOLO-Bad-Triangle runs the attack-defend-fortify triad on a YOLO object detection model:

1. **Attack** — find and characterize adversarial perturbations that degrade detection
2. **Defend** — apply preprocessing or learned defenses to recover performance
3. **Fortify** — improve the defended stack based on measured results, iteratively

---

## Direction A Question

Is c_dog (DPC-UNet neural defense) worth continuing as a fortification path, relative
to classical defenses, on the worst validated attacks?

---

## Authoritative Evidence (Phase 4 only, verified from cycle_history/)

Recovery = defended mAP50 − undefended mAP50 for that attack.
Checkpoint round determined by file modification timestamp (Round 3 deployed 2026-04-04 18:29).

### Deepfool attack (undefended: 0.2184, baseline: 0.6002)

| Cycle | Checkpoint | Defense | mAP50 | Recovery |
|---|---|---|---|---|
| c11 (cycle_20260331_131443) | Round 2 | none | 0.2184 | — |
| c11 (cycle_20260331_131443) | Round 2 | c_dog | 0.2403 | +0.0219 |
| c11 (cycle_20260331_131443) | Round 2 | bit_depth | 0.2229 | +0.0045 |
| c12 (cycle_20260402_133001) | Round 2 | c_dog | 0.2065 | -0.0119 |
| c12 (cycle_20260402_133001) | Round 2 | bit_depth | 0.2290 | +0.0106 |
| c12 (cycle_20260402_133001) | Round 2 | jpeg | **0.3175** | **+0.0992** |
| c13–c15 (avg, Round 3) | Round 3 | c_dog | 0.2238 | +0.0054 |
| c13–c15 (avg, Round 3) | Round 3 | jpeg | **0.3175** | **+0.0992** |
| c13–c15 (avg, Round 3) | Round 3 | median | 0.3656 | +0.1472 |
| ts_sweep (Round 3) | Round 3 | c_dog ts10 | 0.2676 | +0.0492 |
| ts_sweep (Round 3) | Round 3 | c_dog ts25 | 0.2679 | +0.0495 |
| ts_sweep (Round 3) | Round 3 | c_dog ts7525 | 0.2929 | +0.0745 |

### Square attack (undefended: 0.3630, baseline: 0.6002)

| Cycle | Checkpoint | Defense | mAP50 | Recovery |
|---|---|---|---|---|
| c11 (cycle_20260331_131443) | Round 2 | none | 0.3630 | — |
| c11 (cycle_20260331_131443) | Round 2 | c_dog | **0.3890** | **+0.0260** |
| c11 (cycle_20260331_131443) | Round 2 | bit_depth | 0.3863 | +0.0233 |
| c11 (cycle_20260331_131443) | Round 2 | median | 0.3336 | -0.0294 |
| c12 (cycle_20260402_133001) | Round 2 | c_dog | 0.3624 | -0.0006 |
| c12 (cycle_20260402_133001) | Round 2 | bit_depth | 0.3499 | -0.0131 |
| c12 (cycle_20260402_133001) | Round 2 | jpeg | 0.3247 | -0.0383 |
| c13–c15 (avg, Round 3) | Round 3 | c_dog | 0.3503 | -0.0127 |
| c13–c15 (avg, Round 3) | Round 3 | jpeg | 0.3247 | -0.0383 |
| c13–c15 (avg, Round 3) | Round 3 | median | 0.2768 | -0.0862 |

### Anomaly notes

- c11 and c12 both used Round 2 checkpoint but show different c_dog results on deepfool
  (0.2403 vs 0.2065). deepfool has no fixed seed — measurement variance is the likely cause.
- c13–c15 Phase 4 results are identical. Confirmed fresh (timestamps verified). Deterministic
  pipeline with same Round 3 checkpoint, same attack params, same 500-image COCO subset.
- run_summary.json missing from c12–c15 validate_deepfool_c_dog artifacts. Root cause:
  pre-atomic-write code (fixed in commit acbb1a5, 2026-04-08). Historical; not backfilled.
- ts7525 sweep run failed on first attempt with TypeError (duplicate `passes` kwarg:
  `passes=passes_meta` explicit + `**stats` containing `passes` from multipass wrapper).
  Fixed: removed explicit kwarg, injected `stats["passes"]=1` for single-pass path.
  Single-pass ts10/ts25 results unaffected. Fix applied in commits a9e5334 (Mac) / fca5603 (NUC).
- 100-image ts7525 diagnostic (0.2929) did not hold at 500 images (0.2600). Delta of 0.033
  exceeds ±0.005 noise floor — the 100-image sample over-estimated improvement. Gate decisions
  should always use 500-image results as authoritative.

---

## Fortification Actions Tried

| Round | Target | Method | Deepfool result | Square result |
|---|---|---|---|---|
| Round 1 | deepfool + blur | Colab finetune from scratch | modest improvement | not measured |
| Round 2 | deepfool + blur | Colab continued from R1 | similar to R1 | not measured |
| Round 3 | deepfool + blur + square | multi-attack mix, Colab from R2 | no measurable improvement | regressed vs R2 |
| Timestep sweep | deepfool | param tuning (ts10/ts25/ts7525) | ts7525 best: 0.2929 (+0.0745); single-pass variants flat at ~0.268 | not applicable |
| 500-img ts7525 validation | deepfool | full-scale confirm of ts7525 result | 0.2600 (+0.0362 vs R3 c_dog) | not applicable |
| Round 4 | deepfool-only, ts7525 schedule | deepfool-focused Colab retrain from R3 checkpoint | [TBD — pending YOLOv11 timing decision] | [TBD] |

**Pattern:** Multi-attack mixing (Round 3) caused regression on both targets. Single-attack
focus is required going forward.

---

## Key Structural Findings

1. **deepfool vs c_dog — gap reduced but not closed:** Single-pass c_dog (ts25) reaches
   0.2238–0.2679, leaving a 0.0937–0.0496 gap to jpeg. Multi-pass ts7525 reaches 0.2929
   (gap to jpeg: 0.0246) — the coarse→fine schedule partially handles high-frequency
   perturbations. This disproves a pure "architectural ceiling" claim: scheduling is the
   variable. However, c_dog ts7525 remains third on deepfool behind median (0.3656) and
   jpeg (0.3175) on 100-image diagnostic runs. 500-image validation determines whether
   0.2929 holds at full scale before any verdict is written.

2. **square is better matched:** Large-patch occlusion (square attack) is well-suited
   to diffusion denoising's inpainting-style recovery. jpeg HURTS on square (-0.0383).
   Round 2 c_dog was the only defense with meaningful positive recovery (+0.0260).

3. **Round 3 regressed both:** Multi-attack training diluted gradient signal.
   c_dog with Round 3 is worse than Round 2 on both attacks.

---

## Verdict

```
Verdict: PAUSE c_dog (YOLOv8 scope closed)

Rationale:

deepfool — ceiling confirmed. With optimal multi-pass schedule (ts7525),
c_dog reaches 0.2600 on 500 images. The strongest classical baseline on
deepfool is median_preprocess at 0.3656 — a gap of 0.1056. That gap is not
closable in one or two rounds. The success criterion (c_dog > best classical
by +0.005 in 2 consecutive Phase 4 cycles) cannot be met on deepfool with
the current architecture and YOLOv8 as the detector. Not RETIRE: the
scheduling finding (ts7525 +0.0362 improvement with no retraining) shows
the architecture is not exhausted — it is mismatched to deepfool's
high-frequency perturbation structure regardless of schedule.

square — genuine positive signal, not pursued. Round 2 c_dog was the only
defense with meaningful positive recovery on square (+0.0260). Round 3
regressed due to multi-attack training dilution — a known-fixable problem.
The architecture is well-suited to large-patch occlusion. However, with
YOLOv8 being superseded, training c_dog further on YOLOv8 square pairs is
compute that will not transfer. The square finding is archived here as a
positive result: pursue c_dog square-focused training on the next model
version from Phase 1.

Not RETIRE: c_dog (DPC-UNet) showed genuine recovery on square (Round 2),
identified a structural scheduling improvement on deepfool (ts7525), and
its image-level denoising is architecture-sound. The YOLOv8 experiment is
closed; the fortification hypothesis carries forward to the next model.

Next fortification direction:
  1. Establish clean YOLOv11 baseline (no attack, no defense, 500 images)
  2. Re-characterize attacks on YOLOv11 from Phase 1 (attack params are
     model-specific and do not transfer)
  3. Restart c_dog fortification on YOLOv11 with square-only training focus
     from the start — do not resume YOLOv8 checkpoint for training
  4. Re-evaluate deepfool on YOLOv11 after characterization — the damage
     profile and gradient structure may differ significantly
```

---

## Evidence Integrity Notes

- All Phase 4 values sourced from `outputs/cycle_history/*.json` validation_results
- c13–c15 values labeled "avg" but are identical (deterministic pipeline confirmed)
- Checkpoint assignment by file timestamp: Round 3 deployed 2026-04-04 18:29:41
  - c11 (finished 2026-04-01): Round 2
  - c12 Phase 4 (metrics written 2026-04-04 00:25): Round 2
  - c13 Phase 4 (metrics written 2026-04-05 01:26): Round 3
  - c14, c15: Round 3
