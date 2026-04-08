---
name: sweep
description: Run a YOLO-Bad-Triangle defense sweep with correct env vars pre-filled. Supports --phases to run only parts of the sweep.
---

Run a defense sweep against the current DPC-UNet checkpoint using the correct environment and arguments for this project.

## Usage

```
/sweep
/sweep --phases 3,4
/sweep --attacks fgsm,pgd --defenses c_dog
/sweep --attacks fgsm,pgd,deepfool,blur --defenses c_dog,median_preprocess --phases 1,2,3,4
```

## What to do

Parse any arguments the user passed after `/sweep`. Map them to the sweep_and_report.py flags below.

Then run the following command in the background using the Bash tool:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks <attacks> \
  --defenses <defenses> \
  --preset full \
  --workers 1 \
  <--phases X,Y if specified>
```

**Defaults (use these when not specified by the user):**
- `--attacks`: `blur,deepfool,fgsm,pgd`
- `--defenses`: `c_dog`
- `--phases`: omit (run all phases 1,2,3,4)
- `--workers`: always `1` (more than 1 causes memory crashes with DPC-UNet)

**Always include** `PYTHONPATH=src`.

If the sweep uses `c_dog` or `c_dog_ensemble`, keep the current
`DPC_UNET_CHECKPOINT_PATH` from the shell or `.env`. Only set or override it
explicitly when the user asks to benchmark a specific checkpoint.

After launching the background task, tell the user:
- What attacks and defenses are being swept
- Which phases are running
- The background task ID so they can monitor it
- That you'll notify them when it finishes

When the task completes, read the output and report:
- Detection counts and % drop vs baseline (1,437 detections) for each attack+defense combo
- Whether results improved vs the latest comparable tracked sweep/report for each attack+defense pair
