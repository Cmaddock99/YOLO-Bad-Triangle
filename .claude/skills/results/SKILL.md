---
name: results
description: Pull the latest sweep results and print a formatted comparison table showing detection drops, defense recovery, and trend vs previous runs.
---

Pull the latest sweep results and display a clean summary table.

## What to do

### Step 1 — Find the latest sweep

```bash
ls -t /Users/lurch/ml-labs/YOLO-Bad-Triangle/outputs/framework_reports/ | head -5
```

Pick the most recent sweep directory.

### Step 2 — Load the CSV

```bash
cat /Users/lurch/ml-labs/YOLO-Bad-Triangle/outputs/framework_reports/<latest_sweep>/framework_run_summary.csv
```

### Step 3 — Compute and display results

From the CSV, extract `total_detections` for each run. Baseline is the `baseline_none` row.

Calculate for each attack+defense combo:
- **Detection drop %** = `(baseline - defended) / baseline * 100`
- **Attack damage %** = `(baseline - attacked) / baseline * 100`
- **Recovery %** = `(defended - attacked) / (baseline - attacked) * 100` (how much the defense recovered)

Print two tables:

**Table 1 — Attack damage (no defense):**
| Attack | Detections | Drop vs baseline |
|---|---|---|
| fgsm | X | X% |
| pgd | X | X% |
| deepfool | X | X% |
| blur | X | X% |

**Table 2 — Defense recovery:**
| Attack + Defense | Defended | Drop vs baseline | Recovery from attack |
|---|---|---|---|
| fgsm + c_dog | X | X% | X% |
| pgd + c_dog | X | X% | X% |
| blur + c_dog | X | X% | X% |
| deepfool + c_dog | X | X% | X% |

**Known best results (100-epoch checkpoint) for comparison:**
- fgsm+c_dog: 30.0% drop
- pgd+c_dog: 29.9% drop
- blur+c_dog: 31.3% drop
- deepfool+c_dog: 88.7% drop

Mark results that beat the best with ✓ and those that are worse with ✗.

### Step 4 — Cross-sweep trend (optional)

If the user runs `/results all` or `/results trend`, also load previous sweeps and show how results have changed over time as a simple text chart.

### Step 5 — Suggest next steps

Based on the results, suggest one concrete action:
- If deepfool recovery is still poor (>85% drop): suggest more deepfool training pairs in next Colab run
- If all defenses improved vs best: suggest running a full 4-phase sweep to update the dashboard
- If results are mixed: note which attack improved and which didn't
