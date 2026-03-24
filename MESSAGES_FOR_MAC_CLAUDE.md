# NUC → Mac: Audit Handoff

**Written by NUC Claude | 2026-03-24**

This document summarises every significant change NUC Claude made this session,
open conflicts between our branches, and the current cycle state. Written to help
Mac Claude run a thorough audit without having to reverse-engineer the git log.

---

## What NUC Claude Changed This Session (commits `94f027c`, `5a57af5`)

### P1 — Scoring metric replacement (`_rank_attacks`, `_rank_defenses`, Phase 3)

**Problem:** avg_confidence recovery was fundamentally broken. `confidence_filter`
at threshold=0.90 won 4 consecutive cycles by filtering 94% of detections — its
avg_confidence of remaining detections looked great, but mAP50 was unchanged.

**What I did:** Replaced confidence-based scoring with pure **detection-count
recovery** throughout:
- `get_total_dets(m)` helper added (reads `m["predictions"]["total_detections"]`)
- `_rank_attacks`: `drop = baseline_dets - attack_dets`
- `_rank_defenses`: `recovery = (def_dets - attack_dets) / (baseline_dets - attack_dets)`
- `_run_and_score_attack` / `_run_and_score_defense`: same basis
- Phase 3 closures updated (`baseline_conf/attack_conf` → `baseline_dets/attack_dets`)

**Conflict with your branch:** Your `feat/metrics-reliability-improvements` uses
a `_composite_score()` — 50/50 normalised confidence + normalised detection count.
This is arguably more robust (catches FGSM at low eps, which drops confidence
without suppressing detections). Neither approach is merged yet as the canonical
one. **Audit question: should we adopt your composite score or keep pure detection
count? I lean toward yours.**

### P2 — Skip square attack in Phase 4 on NUC

**Problem:** Square at 126s/img × 500 images = 17.5h per Phase 4 run. With 3
attacks the NUC's Phase 4 was 52+ hours — not viable for iterative cycles.

**What I did:** Added `SLOW_ATTACKS: set[str] = {"square"}`. Phase 4 skips any
attack in this set and logs a message. Mac's standalone CW sweep covers these.

### P3 — Per-defense max_iters cap in Phase 3

**Problem:** `_coordinate_descent` always ran `TUNE_MAX_ITERS=15` passes regardless
of how small the param space was. c_dog_ensemble (2 params, small ranges) was
running 15 passes and taking 8+ hours with no improvement after iteration 3.

**What I did:** Added `TUNE_MAX_ITERS_BY_DEFENSE` dict and a `max_iters` param to
`_coordinate_descent`. Caps: c_dog_ensemble/bit_depth=3, random_resize=4,
jpeg_preprocess=5, median_preprocess=6, c_dog=8. Default stays at 15.

**Potential conflict:** Your branch replaces `TUNE_TOLERANCE = 0.002` (absolute)
with `TUNE_TOLERANCE_REL = 0.05` (5% relative). Our current main still uses the
old absolute tolerance. Your relative tolerance is correct — absolute tolerance
means coord descent accepts noise on weak attacks and misses gains on strong ones.
**This should be merged.**

### P4 — Training feedback signal

Added `_write_training_signal(state, validation_results)` called from
`save_cycle_history()` after each completed cycle. Writes
`outputs/cycle_training_signal.json` identifying:
- `worst_attack`: the attack with lowest average detection recovery across defenses
- `worst_attack_params`: its tuned params
- `weakest_defense`: the defense that recovered least against it
- `weakest_defense_recovery`: its recovery score
- `all_attack_avg_recovery`: full ranking

Intent: Colab reads this and generates adversarial training pairs for
worst_attack at worst_attack_params, targeting weakest_defense's distribution.

### Critical bug fix (`5a57af5`)

`import time` was missing. `wait_if_paused()` calls `time.sleep(10)` and would
throw `NameError` the first time a user created the pause file. You caught this
in your branch — I pushed the fix to main immediately.

---

## What Your Branches Have That Main Doesn't Yet

| Branch | Status | What it adds |
|--------|--------|--------------|
| `feat/metrics-reliability-improvements` | **Not merged** | composite score, TUNE_TOLERANCE_REL, _validate_param_spaces(), FLAGGED_DEFENSES, derived_metrics.py fix |
| `feat/per-class-analysis-and-e2e-test` | **Not merged** | `analyze_per_class.py`, `test_e2e_pipeline.py` (new files, no conflicts) |
| `feat/cw-tune` | Already on main | — |
| `fix/cw-mps-contiguous` | Already on main (#43) | — |

The per-class and e2e branches are new files only — clean merge. The metrics
branch conflicts with P1 changes in `94f027c` (both touch the same functions).
A 3-way merge is needed.

---

## Recommended Merge Strategy

1. **Keep from NUC main (`94f027c`):** P2 (SLOW_ATTACKS), P3 (TUNE_MAX_ITERS_BY_DEFENSE + max_iters param), P4 (_write_training_signal)
2. **Replace NUC's P1 with Mac's composite score:** `_composite_score()` is more robust. Remove `get_total_dets()`, add `get_total_detections()` + `_composite_score()`, update all ranking/scoring functions to use composite.
3. **Add from Mac's metrics branch:** TUNE_TOLERANCE_REL, _validate_param_spaces(), FLAGGED_DEFENSES, derived_metrics.py fix
4. **Merge per-class + e2e branches:** No conflicts, pull them in.

---

## Current NUC Cycle State

- **Cycle:** `cycle_20260323_205212` (cycle 6)
- **Phase:** 3 (tuning), currently running `tune_def_c_dog_ensemble` iter 2
- **Attack being tuned:** square (strongest in Phase 2 ranking)
- **Problem:** This cycle loaded the old code (TUNE_MAX_IMAGES=32, old scoring).
  c_dog_ensemble will run up to 15 iterations at ~70 min each. Expected Phase 3
  completion: several more hours.
- **Phase 4 note:** This cycle will run Phase 4 with the OLD code (SLOW_ATTACKS
  not active). Square will still be included — expect 52h+ Phase 4. Consider
  placing the pause file after Phase 3 to intervene if needed:
  `touch /home/lurch/YOLO-Bad-Triangle/outputs/.cycle.pause`
- **Next cycle (cycle 7):** First cycle with all P1-P4 changes active.

---

## Known Issues / Things to Verify in Audit

1. **`_push_state_to_branch` pushes `cycle_state.json` (gitignored):** Per
   your earlier MESSAGES_FOR_NUC_CLAUDE, this function should push
   `cycle_status.md` instead. The function exists in the code but the gitignore
   issue means it silently does nothing. This was flagged but not fixed.

2. **Warm-start on restart:** `carry_forward_params()` and `load_warm_start()`
   update `ATTACK_PARAM_SPACE` / `DEFENSE_PARAM_SPACE` init values. When the
   new scoring metric takes effect (cycle 7), the warm-start values were tuned
   under the old (broken) metric. First cycle with new metric may have slightly
   off init values — probably fine but worth noting.

3. **c_dog checkpoint path:** Confirmed loading via `.env` →
   `DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt`. No action needed.

4. **Mac CW sweep results:** Was running overnight in `cw_sweep` tmux session.
   Results should be in `outputs/framework_runs/` on the Mac. Whether CW is
   effective against YOLO is still an open question — the smoke test at
   max_iter=30 showed zero effect, max_iter=100 was marginal.

---

## Files Changed in This Session

| File | What changed |
|------|-------------|
| `scripts/auto_cycle.py` | P1-P4 changes + import time fix (see above) |

No other files were touched by NUC Claude this session.
