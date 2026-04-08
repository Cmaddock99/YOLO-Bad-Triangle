# Loop Design

The goal of YOLO-Bad-Triangle is to demonstrate a closed adversarial robustness
loop: each cycle should produce a measurably harder-to-attack model than the one
before it.

## The Four-Phase Cycle

Each cycle runs four phases in sequence via `scripts/auto_cycle.py --loop`.

| Phase | Name | Dataset | Metric | Output |
|---|---|---|---|---|
| 1 | Characterize | 32 images by default (smoke); slower attacks use lower caps | Composite suppression (avg-confidence + detections) | Top-N worst attacks |
| 2 | Matrix | 32 images by default (smoke) | Composite recovery | Top-N best defenses |
| 3 | Tune | 16 images by default; slower attacks use lower caps | Composite recovery | Best attack + defense params |
| 4 | Validate | 500 images by default; selected slow attacks are capped at 50 | mAP50 | Ground-truth performance |

Phases 1–3 use fast proxy metrics (composite health from avg confidence + detection count)
because they need to run many times during ranking and coordinate-descent tuning. Phase 4 is the only
authoritative number — mAP50 on the validation set.

Current per-attack caps in `auto_cycle.py`:

- Phase 1 characterize: `square=8`, `eot_pgd=12`, `dispersion_reduction=12`
- Phase 3 tune: `square=8`, `eot_pgd=12`, `dispersion_reduction=12`
- Phase 4 validate: `square=50`, `eot_pgd=50`, `dispersion_reduction=50`

## Warm-Start Carry-Forward

After each completed cycle, `carry_forward_params()` writes
`outputs/cycle_warm_start.json` with the best attack and defense parameters found.
The next cycle loads these as starting points for Phase 3 coordinate descent, so
improvements compound across cycles rather than restarting from defaults each time.

## The Retraining Signal

After Phase 4, `_write_training_signal()` writes `outputs/cycle_training_signal.json`:

```json
{
  "worst_attack": "blur",
  "worst_attack_params": {"attack.params.kernel_size": 25},
  "weakest_defense": "median_preprocess",
  "weakest_defense_recovery": 0.12,
  "cycle_id": "cycle_20260323_154325"
}
```

This identifies the worst measured attack and the weakest measured defense for
that attack.

Important caveat: `weakest_defense` is a diagnostic field, not a guarantee that
the chosen defense is trainable. If you use the signal to plan DPC-UNet
retraining, confirm that the selected defense is one the model can actually
improve.

## Connecting to Colab Retraining

The intended flow after a cycle completes:

1. **Read the signal** — `outputs/cycle_training_signal.json` identifies `worst_attack`
2. **Generate training pairs** — `scripts/export_training_data.py --from-signal` packs
   adversarial images (using `worst_attack` at `worst_attack_params`) + clean images
   into `outputs/training_exports/<cycle_id>_training_data.zip`
3. **Upload to Drive** — upload the zip to Google Drive root
4. **Retrain in Colab** — open `notebooks/finetune_dpc_unet.ipynb`, add the signal-reading
   cell (see below), run all cells on a T4 GPU
5. **Evaluate the new checkpoint** — `scripts/evaluate_checkpoint.py --checkpoint-a old.pt
   --checkpoint-b new.pt` compares mAP50; only deploy if the candidate passes the clean A/B gate
   against the currently active checkpoint
6. **Deploy** — move the candidate into the path pointed to by `DPC_UNET_CHECKPOINT_PATH`
   (or update that env var target)
7. **Next cycle** — the improved DPC-UNet is now the active defense; repeat

### Colab Notebook Signal Cell

Add this cell near the top of `notebooks/finetune_dpc_unet.ipynb` (before the training loop):

```python
import json, pathlib
signal_path = pathlib.Path("/content/drive/MyDrive/YOLO-Bad-Triangle/cycle_training_signal.json")
if signal_path.exists():
    signal = json.loads(signal_path.read_text())
    print(f"Training signal: worst_attack={signal['worst_attack']} "
          f"recovery={signal['weakest_defense_recovery']:.3f}")
    ATTACK_NAME = signal["worst_attack"]
    ATTACK_PARAMS = signal["worst_attack_params"]
else:
    print("No signal found — using defaults")
    ATTACK_NAME = "pgd"
    ATTACK_PARAMS = {"attack.params.epsilon": 0.016}
```

## Longitudinal Tracking

`scripts/generate_cycle_report.py` reads all `outputs/cycle_history/*.json` and writes:

- `outputs/cycle_report.md` — executive summary table + per-attack×defense mAP50 trends
- `outputs/cycle_report.csv` — raw data for analysis

This updates automatically after each cycle completes (called from `save_cycle_history()`).

Reporting and warning generation prefer authoritative Phase 4 rows over
diagnostic smoke rows when both exist for the same comparison. Smoke-only runs
remain useful for ranking and tuning, but they are not deployment evidence.

## Repo Hygiene for Outputs

To keep diffs reviewable while preserving useful history:

- Commit: structured reports and summaries needed for trend analysis
  (`outputs/framework_reports/`, `outputs/cycle_report.md`, `outputs/cycle_report.csv`).
- Do not commit: large local transfer artifacts and one-off handoff files
  (for example `outputs/*.zip`, `outputs/*.pdf`).
- Keep runtime lock/state files ephemeral (`outputs/.cycle.lock`, `outputs/cycle_state.json`).

Safe pull sequence when local WIP exists:

1. `git stash push -u -m "pre-pull backup <date>"`
2. `git pull --rebase origin main`
3. `git stash pop` and resolve conflicts (if any)
4. `git stash drop` once the restore is verified

## What "Done" Looks Like

The loop is working when `outputs/cycle_report.md` shows monotonically increasing
`Best defended mAP50` across cycles — meaning each retrained DPC-UNet checkpoint
holds up better against the worst attack than the previous one.

A concrete target: after 10 cycles, the best defended mAP50 under the worst attack
should approach the clean baseline mAP50 (currently ~0.60). If it stalls below ~0.45,
the retraining signal is not pointing at the right attack — consider switching to
`--from-signal` with a wider pool of attacks.

## Defense Catalogue

Active defenses in `ALL_DEFENSES`:

| Defense | Mechanism |
|---|---|
| `c_dog` | DPC-UNet learned denoiser (the novel defense) |
| `median_preprocess` | Median blur input preprocessing |
| `jpeg_preprocess` | JPEG re-encode input preprocessing |
| `bit_depth` | Bit-depth reduction preprocessing |

Registered but currently excluded from `ALL_DEFENSES`:

- `c_dog_ensemble`
- `random_resize`

They remain available for manual experiments, but the current automated cycle
does not rank or tune them.
