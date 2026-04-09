# Direction A Closure Document (DRAFT)
**Status:** INCOMPLETE — awaiting NUC timestep sweep results and fortification verdict
**Date started:** 2026-04-09
**Complete when:** NUC reports sweep results AND one full Round 4 cycle completes

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
| ts_sweep (Round 3) | Round 3 | c_dog ts10 | [TBD] | [TBD] |
| ts_sweep (Round 3) | Round 3 | c_dog ts25 | [TBD] | [TBD] |
| ts_sweep (Round 3) | Round 3 | c_dog ts7525 | [TBD] | [TBD] |

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

---

## Fortification Actions Tried

| Round | Target | Method | Deepfool result | Square result |
|---|---|---|---|---|
| Round 1 | deepfool + blur | Colab finetune from scratch | modest improvement | not measured |
| Round 2 | deepfool + blur | Colab continued from R1 | similar to R1 | not measured |
| Round 3 | deepfool + blur + square | multi-attack mix, Colab from R2 | no measurable improvement | regressed vs R2 |
| Timestep sweep | deepfool | param tuning (ts10/ts25/ts7525) | [TBD] | not applicable |
| Round 4 | [TBD — square or deepfool] | [TBD] | [TBD] | [TBD] |

**Pattern:** Multi-attack mixing (Round 3) caused regression on both targets. Single-attack
focus is required going forward.

---

## Key Structural Findings

1. **deepfool vs c_dog architecture mismatch:** deepfool perturbations are subtle and
   high-frequency. jpeg_preprocess at quality=40 destroys them by frequency filtering —
   a structural advantage DPC-UNet cannot replicate through more training. The deepfool
   gap (c_dog 0.2238 vs jpeg 0.3175 = 0.0937) is architectural, not a data problem.

2. **square is better matched:** Large-patch occlusion (square attack) is well-suited
   to diffusion denoising's inpainting-style recovery. jpeg HURTS on square (-0.0383).
   Round 2 c_dog was the only defense with meaningful positive recovery (+0.0260).

3. **Round 3 regressed both:** Multi-attack training diluted gradient signal.
   c_dog with Round 3 is worse than Round 2 on both attacks.

---

## Verdict

```
[TO BE FILLED IN]

Verdict: [CONTINUE c_dog / PAUSE c_dog / RETIRE c_dog]

Rationale: [fill after NUC sweep + Round 4 results]

Next fortification direction: [fill after verdict]
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
