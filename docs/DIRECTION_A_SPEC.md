# Direction A Spec: Evaluating c_dog as a Fortification Path

**Date:** 2026-04-09
**Status:** Active
**Scope:** c_dog / DPC-UNet as one fortification candidate inside the attack-defend-fortify loop

---

## Project Goal

This repo is a machine-vision robustness lab. Its job is to run the triad on a vision model:

1. **Attack** the model — find and characterize adversarial perturbations
2. **Defend** the model — apply preprocessing or learned defenses
3. **Fortify** the system — improve the defended stack based on measured results

The repo is not defined by c_dog. c_dog is one trainable defense candidate inside that
larger loop.

---

## Direction A Goal

Determine whether c_dog is a fortification path worth continuing relative to classical
defenses on the currently worst validated attack.

This is a sub-question, not the closure condition for the whole repo.

---

## What "Closed" Means

Direction A closes when one of these becomes true:

**Positive closure:** c_dog reproducibly outperforms the strongest classical baseline on
the worst validated attack, without unacceptable clean-performance regression.

**Negative closure:** after bounded targeted fortification work, c_dog still does not
outperform the strongest classical baseline, and the repo records that result clearly.

Both outcomes are valid. The goal is defensible evidence, not forcing a win.

---

## Current Evidence (as of 2026-04-09)

| Cycle | c_dog vs deepfool | jpeg vs deepfool | bit_depth vs deepfool | Status |
|---|---|---|---|---|
| cycle_20260331_131443 (c11) | **0.2403** | n/a (not in top_defenses) | 0.2229 | c_dog > bit_depth ✅ |
| cycle_20260402_133001 (c12) | 0.2065 | **0.3175** | 0.2290 | c_dog last ❌ |
| cycle_20260404_003651 (c13) | 0.2238 | **0.3175** | n/a | identical to c12 ⚠️ |
| cycle_20260405_073545 (c14) | 0.2238 | **0.3175** | n/a | identical to c12 ⚠️ |
| cycle_20260406_054944 (c15) | 0.2238 | **0.3175** | n/a | identical to c12 ⚠️ |

Baseline (no attack, no defense): 0.6002 mAP50
Worst attack: deepfool — 63.6% damage (0.2184 mAP50)
Strongest classical baseline: **jpeg_preprocess at 0.3175** (not bit_depth)

**Important:** Cycles 13–15 have byte-for-bit identical Phase 4 results. These are not
independent evidence. The NUC is almost certainly reusing cached run artifacts rather
than re-executing Phase 4. The current evidence base is: one clean c_dog win (c11),
one confirmed regression (c12), and three non-independent repeats of c12's data.

---

## Phase 0: Evidence Integrity

**Goal:** Verify that new cycle evidence is real before using it to choose a fortification action.

**Concrete checks required (requires SSH to NUC at 10.0.0.113):**

1. Inspect `auto_cycle.py` Phase 4 skip logic — does the cycle check for existing
   `validate_*/metrics.json` before running? Identify the exact condition.
2. Compare `run_summary.json:provenance.checkpoint_fingerprint_sha256` across cycles
   12–15 run artifacts on the NUC. If identical across cycles, artifacts were reused, not re-run.
3. Check artifact timestamps at `/home/lurch/YOLO-Bad-Triangle/outputs/framework_runs/`
   for cycles 13–15. If `validate_*/metrics.json` timestamps predate each cycle's start
   time, those are confirmed stale reuses.

**Exit condition:** A fresh Phase 4 run is confirmed to have executed with the intended
checkpoint and config. All subsequent evidence must come from runs that pass this check.

---

## Phase 1: Signal Audit

**Goal:** Confirm the fortification signal is derived from authoritative completed evidence.

**Checks:**

1. Reconcile `outputs/cycle_training_signal.json` against the corresponding Phase 4
   artifacts. The current signal (cycle_20260402_133001) shows c_dog recovery of -0.0312.
   Phase 4 artifacts show a raw mAP50 delta of -0.0119. The formula in
   `_write_training_signal()` (`auto_cycle.py:1550–1749`) includes additional terms beyond
   raw delta — resolve what those are before trusting the signal value.
2. Confirm `ranking_source: phase4_map50` is accurate — the signal must not derive from
   Phase 1/2/3 smoke metrics.
3. Classify the current signal as one of:
   - **valid** — Phase 4 complete, formula verified, evidence is authoritative
   - **stale** — Phase 4 incomplete or a cache hit drove the result
   - **non-authoritative** — derived from smoke metrics, not Phase 4

**Rule:** No retraining or checkpoint promotion based on a stale or non-authoritative signal.

---

## Phase 2: Choose the Fortification Action

**Goal:** Make the next system-hardening move based on evidence, not habit.

**The baseline to beat:** jpeg_preprocess at 0.3175 mAP50 on deepfool.
This is the strongest classical baseline in the current verified evidence. It changes
each cycle — always re-check from the most recent authoritative Phase 4 results before
locking in a decision.

**Decision rule:**

| Condition | Action |
|---|---|
| Phase 4 evidence is not yet trustworthy | resolve Phase 0 before deciding anything |
| c_dog within ~0.05 of jpeg on deepfool | targeted deepfool-focused retraining |
| c_dog gap > 0.10 to jpeg on deepfool | consider architecture or timestep schedule changes first; gradient-based retraining alone may not close this gap |
| deepfool no longer worst attack | redirect fortification toward the new worst attack |

**Allowed outcomes:**

- Targeted c_dog retraining — deepfool only, no multi-attack dilution. Round 3 trained
  on a square_retention mix (deepfool + blur + square) and produced zero net improvement.
  Single-attack focus is required.
- c_dog parameter retuning only (timestep, sharpen_alpha, timestep_schedule)
- Hold c_dog steady and favor the best classical defense for this attack
- Broaden attack coverage if worst-attack evidence is still not stable

---

## Phase 3: Fortify

**If retraining is selected:**

- Train on the worst validated attack only (deepfool if Phase 2 still supports it)
- Resume from current `dpc_unet_adversarial_finetuned.pt` — do not restart from scratch
- Keep loss weights unchanged: pixel=1.0, edge=0.15, feature=0.30
- Apply the clean A/B gate before deployment: `delta_mAP50 >= -0.005`
- Reject deployment if clean regression exceeds this threshold

**If retraining is not selected:**

Execute the chosen non-training fortification action and document it explicitly in the
cycle's history entry and the closure doc.

**Key files:**
- `notebooks/finetune_dpc_unet.ipynb` — Colab retraining (attack list is the only change)
- `scripts/export_training_data.py` — reads signal, exports adversarial pairs
- `src/lab/defenses/preprocess_dpc_unet_adapter.py` — c_dog runtime params
- `outputs/eval_ab_clean.json` — clean A/B gate reference

---

## Phase 4: Validate

Run a full authoritative cycle:

```bash
python scripts/auto_cycle.py --phases 1,2,3,4
```

Judge results from **Phase 4 only.** Do not use Phase 1/2/3 smoke metrics as the verdict.

**Primary questions:**
1. What is the worst attack now?
2. Which defense is strongest now?
3. Did the chosen fortification action improve the defended stack?
4. Did clean performance remain within bounds?

**Comparison table to fill in after the cycle completes:**

| Attack | jpeg mAP50 | c_dog mAP50 | c_dog delta to jpeg | Noise floor passed? |
|---|---|---|---|---|
| deepfool | TBD | TBD | TBD | delta > +0.005? |
| square | TBD | TBD | TBD | c_dog > jpeg? |

---

## Direction A Success Criteria

Direction A is a **positive result** when all hold:

- c_dog beats the strongest classical baseline on the worst validated attack
- The lead exceeds the noise floor: > +0.005 mAP50
- The result repeats across two independent authoritative Phase 4 validations
- Clean A/B remains within the regression gate (delta >= -0.005)

## Direction A Failure Criteria

Direction A is a **negative result** when:

- Two bounded targeted fortification rounds still fail to produce a reproducible c_dog lead, OR
- c_dog only wins at the cost of unacceptable clean regression

That closes Direction A. It does not close the repo.

---

## Required Write-Up

Regardless of outcome, a closure doc must be written. Add it to `docs/analysis/` with
the date in the filename:

```
docs/analysis/direction_a_closure_2026-04-XX.md
```

**Required sections:**

1. Project goal: attack, defend, fortify
2. Direction A question: is c_dog worth continuing as a fortification path?
3. Authoritative evidence by cycle (Phase 4 mAP50 only, with cycle IDs)
4. Fortification actions tried (what was retrained, what changed, what was rejected)
5. Verdict: **continue c_dog** / **pause c_dog** / **retire c_dog**
6. Implications for the next fortification direction

---

## What This Spec Does NOT Address

- c_dog_ensemble re-evaluation (separate track, pursue if c_dog positive)
- eot_pgd and DR Phase 4 coverage (open items in SPEC.md)
- Dashboard or presentation layer
- Generalization to non-YOLO models
- Runner, reporting, or schema layer changes
