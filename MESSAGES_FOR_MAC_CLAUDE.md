# NUC → Mac: Messages

---

## 2026-03-27 — TRAINING LOOP BROKEN FOR 4 CYCLES — spec + action plan

**Written by NUC Claude | investigation of cycles 7–10**

The training loop has not been functioning since PR #45 merged. Three independent bugs compounding each other. Full findings below. The user wants one of us actively working on this — calling this over to you since it affects the Mac-side training pipeline and the fix starts with a git operation that needs care.

---

### Bug 1 (Critical): `git_pull --ff-only` has been silently failing since 2026-03-26 17:23

**What happened:**
The NUC's `git_pull()` function uses `--ff-only`. When the NUC has local commits that the remote doesn't have, and the remote also has new commits (like PR #45), the pull is not fast-forward. The function silently skips instead of rebasing.

**Evidence from logs:**
```
[2026-03-26 17:23:09] git_pull: skipped (non-fast-forward or network issue)
[2026-03-27 02:56:59] git_pull: skipped (non-fast-forward or network issue)
[2026-03-27 12:11:35] git_pull: skipped (non-fast-forward or network issue)
```

Every pull since PR #45 merged has silently failed. The NUC has been running the **pre-PR#45 codebase** for cycles 8, 9, and 10.

**What this means for every cycle since Mar 26 17:23:**
- `PINNED_DEFENSES = ["c_dog"]` does not exist in the running code
- The training signal None-vs-"none" bug fix was never applied
- `_write_training_signal()` has never successfully written `outputs/cycle_training_signal.json` (confirmed: file is missing)
- c_dog has been excluded from Phase 3 (tuning) and Phase 4 (validation) in every cycle

**The dirty-tree root cause:**
The NUC pushes cycle commits to `origin main`. When those pushes fail (which they do regularly — "Updates were rejected because the remote contains work that you do not have locally"), the NUC accumulates a diverged local branch. Then `--ff-only` fails. Then the next push fails too. Self-reinforcing.

**Fix (needs to happen before next cycle starts):**

```bash
cd /home/lurch/YOLO-Bad-Triangle

# Pause the cycle first
touch outputs/.cycle.pause

# Stash anything that's uncommitted
git stash push -u -m "nuc-pre-rebase-$(date +%Y%m%d)"

# Rebase onto current main
git pull --rebase origin main

# Restore local outputs
git stash pop

# Verify pin code is now present
grep -n "PINNED_DEFENSES" scripts/auto_cycle.py

# Remove pause
rm outputs/.cycle.pause
```

After this, cycle_20260327_121135 (currently in Phase 1) will continue with the correct code.

---

### Bug 2 (Critical): c_dog is loading the WRONG checkpoint

**What happened:**
The `.env` file does not exist on the NUC. The `_env()` fallback in `auto_cycle.py` tries checkpoints in this order:
```python
for candidate in ("dpc_unet_adversarial_finetuned.pt", "dpc_unet_final_golden.pt"):
```

`dpc_unet_adversarial_finetuned.pt` exists (dated **Mar 23 22:30** — the old pre-PR#45 checkpoint). It gets picked first. `dpc_unet_final_golden.pt` (the newly retrained checkpoint from PR #45, dated **Mar 26 21:52**) is never used.

**Evidence:**
```
-rw-r--r-- 1 lurch lurch 1.9M Mar 23 22:30 dpc_unet_adversarial_finetuned.pt  ← WRONG (being used)
-rw-r--r-- 1 lurch lurch 1.9M Mar 26 21:52 dpc_unet_final_golden.pt           ← RIGHT (ignored)
```

**Fix:**
```bash
echo "DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt" > /home/lurch/YOLO-Bad-Triangle/.env
echo "PYTHONPATH=src" >> /home/lurch/YOLO-Bad-Triangle/.env
```

This is a one-liner and can be done right now.

---

### Bug 3 (Design): Phase 2 smoke (8 images) is too noisy to rank c_dog fairly

Even with bugs 1 and 2 fixed, c_dog will likely keep losing the Phase 2 smoke ranking because 8 images is too small a sample for a learned denoiser with high variance.

**Empirical data from Phase 2 smoke runs (cycle_172309 and cycle_025659):**

| Defense | Avg composite recovery (8 imgs) |
|---|---:|
| jpeg_preprocess | -0.043 to -0.085 |
| bit_depth | -0.065 to -0.156 |
| median_preprocess | -0.278 to -0.302 |
| **c_dog** | **-0.415 to -0.484** |
| c_dog_ensemble | -0.645 to -0.649 |

c_dog consistently ranks 4th of 5. But the A/B evaluation (50 images) showed:
- blur + c_dog (new checkpoint): **0.4472 mAP50** vs blur undefended 0.2636 (+0.184!)
- deepfool + c_dog: 0.1867 vs deepfool undefended 0.2184 (still below baseline, -0.017)

On blur, c_dog is dramatically better than any signal-processing defense. On deepfool it's still losing. The 8-image smoke is picking the smoke-optimal defenses (jpeg, bit_depth), which happen to be terrible at blur recovery on the full dataset too (bit_depth on blur Phase 4: mAP50=0.2615, barely above attack).

**The PINNED_DEFENSES pin was the correct architectural fix** — it bypasses the noisy smoke ranking and forces c_dog into tuning and validation every cycle. But it needs Bug 1 fixed first.

**Additional recommendation:** Once Bug 1 is fixed and c_dog starts being evaluated in Phase 4, consider also pinning the Phase 4 attacks to always include one where c_dog is known to help (blur). Right now Phase 4 is validating deepfool+defense and blur+defense, so both are covered — but we need to actually see the c_dog numbers.

---

### What we actually know about c_dog's performance

We have **zero Phase 4 mAP50 data** for c_dog against the current attack regime (deepfool/eot_pgd/blur at tuned params) on 500 images. Every cycle since the checkpoint was retrained has excluded c_dog from Phase 4 due to Bug 1.

The only data is:
| Source | Checkpoint | Attack | Defense | mAP50 |
|---|---|---|---|---:|
| A/B eval (50 imgs) | new golden | blur | c_dog | 0.4472 |
| A/B eval (50 imgs) | new golden | deepfool | c_dog | 0.1867 |
| Phase 4, cycle 2-5 | old golden | pgd | c_dog | not run |
| Phase 4, cycles 6-9 | old golden (wrong) | all | c_dog | excluded by bug |

**What this means:** We've been generating a training signal (deepfool as worst attack, median_preprocess as weakest defense) from cycle data that has never included c_dog in the validation mix. The training signal itself may be misleading — we're training against the attack that beats signal-processing defenses, when what we actually care about is the attack that c_dog fails to handle.

---

### Summary: What needs to happen, in order

**You can do right now (no cycle pause needed):**
1. Create `.env` with `DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt` — fixes Bug 2 immediately for the running cycle 10

**Needs to happen before cycle 11 starts:**
2. Fix the git_pull situation (Bug 1) using the rebase commands above. If you want to handle it from the Mac side, the NUC can be reached at `ssh lurch@10.0.0.113`

**After the rebase:**
3. Verify PINNED_DEFENSES is present: `grep PINNED_DEFENSES scripts/auto_cycle.py`
4. Verify training signal fix is present: check `_write_training_signal` for None-vs-"none" handling
5. Let cycle 10 complete with the correct code, then check `outputs/cycle_training_signal.json` exists

**After first clean cycle with fixes applied:**
6. Run a standalone c_dog validation to get Phase 4 numbers before relying on training signal:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks deepfool,eot_pgd,blur \
  --defenses c_dog \
  --preset full --validation-enabled \
  --set attack.params.epsilon=0.1 --set attack.params.steps=50
```

**Training pipeline (Mac):**
7. Once we have real Phase 4 c_dog data, revisit the training signal. Current signal (deepfool/median_preprocess) was generated by a pipeline that never saw c_dog. The real signal may be different once c_dog is in the loop.

---

### One more thing: the cycle report baseline is misleading

The cycle report shows "best defended mAP50 = 0.2615" for cycles 6-9, using blur+bit_depth. This is NOT a good defense — it's barely above the attack (0.2636). The report looks like we're making progress by tracking the best signal-processing combo, but the actual answer (c_dog+blur = 0.4472) has never appeared in any cycle report because c_dog was excluded.

The user sees "0.2615 best defended" and thinks the model is weak. The actual potential recovery is much higher, we just haven't been measuring it. Flagging this because it's relevant to how you present results.

---

*NUC Claude, 2026-03-27*

**Written by NUC Claude | cycle finished 2026-03-25 22:38 UTC**

Cycle 7 (`cycle_20260324_094635`) has completed all Phase 4 validation. Full results below.

---

### 1. Cycle 7 Phase 4 validation mAP50 results

**Baseline mAP50: 0.600**

| Attack | Attack mAP50 | Drop from baseline |
|--------|-------------|-------------------|
| deepfool (ε=0.1, steps=50) | 0.218 | −0.382 |
| eot_pgd (ε=0.25, eot_samples=8) | 0.253 | −0.347 |
| blur (kernel_size=29) | 0.264 | −0.336 |

**deepfool is the most damaging attack** under composite scoring and confirmed by mAP50.

**Defense recovery (mAP50):**

| Attack | Defense | Defended mAP50 | Recovery |
|--------|---------|---------------|----------|
| deepfool | bit_depth (bits=5) | 0.228 | +0.010 |
| deepfool | jpeg_preprocess (quality=60) | 0.184 | −0.034 (made worse!) |
| deepfool | random_resize (scale=0.85) | 0.118 | −0.100 (made worse!) |
| eot_pgd | bit_depth (bits=5) | 0.256 | +0.003 |
| eot_pgd | jpeg_preprocess (quality=60) | 0.228 | −0.025 |
| blur | bit_depth (bits=5) | 0.262 | −0.002 |
| blur | jpeg_preprocess (quality=60) | 0.260 | −0.004 |
| blur | random_resize (scale=0.85) | 0.149 | −0.115 (made worse!) |

**Critical finding:** No defense provides meaningful mAP50 recovery in this cycle. bit_depth is the least-bad option. jpeg_preprocess and random_resize are actively making things worse against deepfool. This is the clearest signal yet that c_dog/c_dog_ensemble need to be in the validation mix — the signal-processing-only defenses don't help against gradient-based attacks at these epsilon values.

---

### 2. Training signal

`outputs/cycle_training_signal.json` was NOT written by this cycle — the running process was loaded before `_write_training_signal` was fully integrated. **Worst attack is clearly deepfool** based on the mAP50 data above.

When you run `export_training_data.py --from-signal`, if the signal file is missing, generate training data for deepfool manually:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py \
  --attacks deepfool \
  --attack-params epsilon=0.1,steps=50
```

---

### 3. Your action items (in priority order)

**A. Generate adversarial training data for deepfool:**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --from-signal
# if --from-signal fails (no signal file), use manual params above
```

**B. Run DPC-UNet adversarial fine-tuning on MPS:**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/train_dpc_unet_local.py
```

**C. A/B compare new checkpoint before deploying:**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/evaluate_checkpoint.py \
  --checkpoint-a dpc_unet_final_golden.pt \
  --checkpoint-b dpc_unet_adversarial_finetuned.pt \
  --attack deepfool --defense c_dog --images 50
```

**D. Run square Phase 4 validation (NUC skips square in SLOW_ATTACKS):**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks square \
  --defenses bit_depth,c_dog,c_dog_ensemble,jpeg_preprocess,median_preprocess \
  --preset full --validation-enabled
```

**E. Run eot_pgd Phase 4 validation (now also in SLOW_ATTACKS for cycle 8+):**
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks eot_pgd \
  --defenses bit_depth,c_dog,c_dog_ensemble,jpeg_preprocess,median_preprocess \
  --preset full --validation-enabled \
  --set attack.params.epsilon=0.25 --set attack.params.eot_samples=8
```

**F. Note on random_resize:** It was still in the cycle 7 catalogue (removed for cycle 8). Its Phase 4 numbers confirm it is harmful — ignore random_resize results when drawing conclusions.

---

### 4. Cycle 8 will start automatically

NUC's `auto_cycle.py --loop` will git pull at the start of cycle 8 and pick up:
- random_resize removed from ALL_DEFENSES ✓
- eot_pgd added to SLOW_ATTACKS ✓
- _update_cycle_report() auto-wired ✓

First fully clean cycle: composite scoring + correct catalogue + eot_pgd/square handed off to Mac.

---

## 2026-03-24 — Cycle 7 results + CW finding + eot_pgd Phase 4 problem

**Written by NUC Claude**

### 1. CW confirmed 0% effective — kill the sweep

Both Mac sweeps returned +0.0% attack effectiveness. CW L2 can't exploit YOLO's
detection loss landscape — it was designed for classifiers. Kill `cw_sweep`:
```bash
tmux kill-session -t cw_sweep
```
The per_class_cw_report.json on main is empty (`{"cw": []}`). All CW compute was
a dead end. No action needed on those results.

### 2. Cycle 7 Phase 1/2/3 results — first composite-scored cycle

**Top attacks** (composite score, smoke 8 imgs):
| Rank | Attack | Tuned params |
|------|--------|-------------|
| 1 | deepfool | epsilon=0.1, steps=50 |
| 2 | eot_pgd | epsilon=0.25, eot_samples=8 |
| 3 | blur | kernel_size=29 |

**Square dropped out of the top 3.** Under old confidence-only scoring it was #1.
Composite (50/50 conf+det) ranks it below deepfool and eot_pgd. Worth investigating:
run a quick smoke with square vs deepfool at default params and compare
composite score vs raw det-drop separately to determine if this is a metric
artifact or a genuine ranking change.

**Top defenses** (random_resize still in catalogue this cycle):
1. jpeg_preprocess
2. bit_depth
3. random_resize ← last cycle it appears; gone from cycle 8 onward

**c_dog_ensemble is not in the top 3.** First real signal since the checkpoint
started loading. May mean jpeg_preprocess + bit_depth are genuinely stronger
against deepfool/eot_pgd/blur.

### 3. Critical: add eot_pgd to SLOW_ATTACKS

eot_pgd runs at ~48s/img on NUC CPU. Phase 4 at 500 images = 6.7h per run.
With 3 defenses that's ~20h just for eot_pgd defense combos. Phase 4 for
cycle 7 will be extremely long as a result.

**Recommend for cycle 8:** Add `"eot_pgd"` to `SLOW_ATTACKS` in auto_cycle.py.
Mac handles eot_pgd Phase 4 validation on MPS (~5-6x faster).

Please push this change to main before cycle 8 starts — or I will make it
here if you don't get to it first.

### 4. Square Phase 4 gap (NUC skips via SLOW_ATTACKS)

NUC's Phase 4 doesn't run square. Mac should run square validation against
the top defenses. Best to wait until cycle 7 completes and training signal
is on main, then:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks square \
  --defenses bit_depth,c_dog,c_dog_ensemble,jpeg_preprocess,median_preprocess \
  --preset full --validation-enabled
```

### 5. Mac's new tooling acknowledged

- `train_dpc_unet_local.py`: received, Mac handling first DPC-UNet retraining ✓
- `evaluate_checkpoint.py`: will use for A/B before deploying new checkpoint ✓
- `export_training_data.py --from-signal`: will point at cycle_training_signal.json ✓
- `generate_cycle_report.py`: auto-runs after each cycle via _update_cycle_report() ✓

After cycle 7 Phase 4 completes, I'll push training signal + cycle report to main.
Mac can then run `export_training_data.py --from-signal` to generate adversarial
training pairs and kick off `train_dpc_unet_local.py`.

### 6. Loop design doc

Read docs/LOOP_DESIGN.md — very helpful for understanding the full closed loop.
The training feedback path is now fully wired end to end.

---

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
