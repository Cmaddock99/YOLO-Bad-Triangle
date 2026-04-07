# Handoff Note — for the next Claude on this machine

**Left by:** Claude (Sonnet 4.6), session ending ~2026-04-05 evening  
**Status:** 4 background eval runs are in progress or completed. You need to collect results, write eval artifacts, and update CLAUDE.md.

---

## What's running / what just ran

Four attacked A/B runs were kicked off in the background to fill a known evidence gap: round 3 of the adversarial checkpoint was deployed on 2026-04-05 using only a clean (no-attack) gate. No attacked A/B was ever run to confirm it's actually better than round 2 under attack conditions.

Run names and what they are:

| Run name | Checkpoint | Attack | Defense | Images | Seed |
|---|---|---|---|---|---|
| `ab_r3_square_nodef` | round 3 (active `.pt`) | square | none | 50 | 137 |
| `ab_r2_square_nodef` | round 2 (`.pt.prev`) | square | none | 50 | 137 |
| `ab_r3_deepfool_nodef` | round 3 (active `.pt`) | deepfool | none | 100 | 137 |
| `ab_r2_deepfool_nodef` | round 2 (`.pt.prev`) | deepfool | none | 100 | 137 |

Outputs land in `outputs/framework_runs/<run_name>/metrics.json`.

**Why no defense?** The cycle data showed c_dog getting only ~1.4% recovery on deepfool and going negative on square — using it as the A/B defense would bury the checkpoint-vs-checkpoint signal in noise. Defense=none gives a clean direct comparison.

---

## What you need to do

### Step 1 — Check runs completed

```bash
ls outputs/framework_runs/ab_r3_square_nodef/metrics.json
ls outputs/framework_runs/ab_r2_square_nodef/metrics.json
ls outputs/framework_runs/ab_r3_deepfool_nodef/metrics.json
ls outputs/framework_runs/ab_r2_deepfool_nodef/metrics.json
```

If any are missing, the run hasn't finished yet — wait or rerun it:

```bash
cd /Users/lurch/ml-labs/YOLO-Bad-Triangle

# Rerun example (square, round 3):
PYTHONPATH=src DPC_UNET_CHECKPOINT_PATH=dpc_unet_adversarial_finetuned.pt \
  .venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --seed 137 \
  --set attack.name=square --set defense.name=none \
  --set runner.max_images=50 --set validation.enabled=true \
  --set runner.run_name=ab_r3_square_nodef

# Swap in .pt.prev and ab_r2_square_nodef for round 2, etc.
```

### Step 2 — Read the mAP50 values

From each `metrics.json`, read the `mAP50` field. Then compute:

```
delta_square   = ab_r3_square_nodef.mAP50   - ab_r2_square_nodef.mAP50
delta_deepfool = ab_r3_deepfool_nodef.mAP50 - ab_r2_deepfool_nodef.mAP50
```

Positive delta = round 3 is more robust to that attack than round 2. That's what we want.

### Step 3 — Write eval artifact files

Write `outputs/eval_ab_square_round3.json` (schema matches `eval_ab_square_phase4.json`):

```json
{
  "checkpoint_a": {
    "path": "dpc_unet_adversarial_finetuned.pt.prev",
    "label": "round 2",
    "mAP50": <ab_r2_square_nodef mAP50>
  },
  "checkpoint_b": {
    "path": "dpc_unet_adversarial_finetuned.pt",
    "label": "round 3",
    "mAP50": <ab_r3_square_nodef mAP50>
  },
  "delta_mAP50": <delta_square>,
  "verdict": "<B is better / A is better / within noise>",
  "attack": "square",
  "defense": "none",
  "seed": 137,
  "images_evaluated": 50
}
```

Write `outputs/eval_ab_deepfool_round3.json` with the same schema (images_evaluated=100).

### Step 4 — Update CLAUDE.md

In `CLAUDE.md`, find the `### Checkpoint facts` section and add the attacked A/B results under the finetuned checkpoint entry. Something like:

```
  - Attacked A/B round 3 vs round 2 (2026-04-05, seed 137, defense=none):
    - square (50 img): delta=<value>
    - deepfool (100 img): delta=<value>
  - Evidence: outputs/eval_ab_square_round3.json, outputs/eval_ab_deepfool_round3.json
```

### Step 5 — Commit

```bash
git add outputs/eval_ab_square_round3.json outputs/eval_ab_deepfool_round3.json CLAUDE.md
git commit -m "eval: add round 3 vs round 2 attacked A/B (square + deepfool, defense=none)"
git push
```

Then tell the user to `git pull` on the NUC.

---

## Decision rules

- **Both deltas positive:** Round 3 is an improvement. Good news.
- **Deltas within ±0.005:** Within noise — neither checkpoint is clearly better on attack resistance. That's fine; round 3 already passed the clean gate.
- **Either delta worse than -0.005:** Flag it to the user before doing anything. Do NOT automatically roll back — the user needs to decide.

**Do not roll back the checkpoint automatically.** If results are bad, surface the numbers and wait for explicit instruction.

---

## Background context you should know

- Round 3 was trained on `square_retention` preset: square x5 oversample + deepfool + blur pairs, resumed from round 2.
- The clean A/B (round 3 vs round 2, 500 images, c_dog, no attack) showed +0.0025 mAP50 — marginally better but within noise. Evidence: `outputs/eval_ab_clean.json`.
- The existing `eval_ab_square_phase4.json` and `eval_ab_deepfool_phase4.json` compare the **golden** checkpoint vs the finetuned checkpoint — not round 3 vs round 2. They are NOT the evidence you're filling.
- The `colab-check` skill was updated this session to require an attacked gate for future deployments.
- The NUC cycle loop is idle between cycles right now. Latest completed cycle: `cycle_20260404_003651`.

---

## What NOT to do

- Don't use c_dog as the defense for the A/B comparison (see "why no defense" above).
- Don't compare against the golden checkpoint — compare round 3 vs round 2 only.
- Don't queue another Colab training run until you know whether round 3 actually improved attack resistance.
- Don't delete `HANDOFF.md` until the work is done and committed.
