---
name: colab-check
description: Check Google Drive for an updated DPC-UNet checkpoint from Colab. If a new one is found, download it and automatically kick off a defense sweep.
---

Check whether a new DPC-UNet checkpoint has been saved to Google Drive by a Colab training run, and optionally download it and run the defense sweep.

## What to do

### Step 1 — Check Drive timestamps

Run:
```bash
rclone lsl gdrive: --max-depth 1 2>/dev/null | grep "\.pt"
```

The known baseline timestamps (training NOT yet complete) are:
- `dpc_unet_adversarial_finetuned.pt` — 2026-03-22 20:41:08
- `dpc_unet_training_resume.pt` — 2026-03-22 20:43:11

Compare the current timestamps to these baselines:

**If `dpc_unet_training_resume.pt` is newer** but `dpc_unet_adversarial_finetuned.pt` is unchanged:
→ Training is still in progress. Report the resume checkpoint timestamp and estimate progress if possible (each epoch takes ~45-60 seconds on T4, 120 total epochs).

**If `dpc_unet_adversarial_finetuned.pt` is newer than 2026-03-22 20:41:08:**
→ Training is complete. Proceed to Step 2.

**If neither file has changed:**
→ Colab hasn't started or hasn't completed an epoch yet. Tell the user.

### Step 2 — Download the new checkpoint

```bash
rclone copy gdrive:dpc_unet_adversarial_finetuned.pt /Users/lurch/ml-labs/YOLO-Bad-Triangle/ && echo "Downloaded"
```

Verify the local file timestamp updated:
```bash
ls -lh /Users/lurch/ml-labs/YOLO-Bad-Triangle/dpc_unet_adversarial_finetuned.pt
```

### Step 3 — Ask the user if they want to run the sweep

Tell the user:
- Training is complete
- New checkpoint downloaded (show file size and timestamp)
- Ask: "Run the defense sweep now? (phases 3+4, ~2 hours)"

If they say yes, run the sweep using the same logic as the `/sweep` skill with `--phases 3,4`.

### Step 4 — After sweep completes

Report results in a comparison table:

| Attack + Defense | New result | Previous best | Change |
|---|---|---|---|
| fgsm + c_dog | X% drop | 30.0% | ↑/↓ |
| pgd + c_dog | X% drop | 29.9% | ↑/↓ |
| blur + c_dog | X% drop | 31.3% | ↑/↓ |
| deepfool + c_dog | X% drop | 88.7% | ↑/↓ |

Baseline is always 1,437 detections. Lower % = better defense recovery.
