# Framework Run Comparison Report

Total discovered framework runs: **3**

## Run Inventory

| Run | Model | Attack | Artifact | Placement | Defense | Semantics | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---|---|---|---:|---:|
| `attack_fgsm` | `yolo` | `fgsm` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.7132 | 0.5731 |
| `baseline_none` | `yolo` | `none` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.7082 | 0.6316 |
| `defended_fgsm_median_preprocess` | `yolo` | `fgsm` | `` | `` | `median_preprocess` | `attack_then_defense` | `complete` | 0.6639 | 0.6834 |

## Attack Effectiveness

| Model | Seed | Attack | Artifact | Placement | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `fgsm` | `` | `` | `untargeted_conf_suppression` |  | `` | 0.7082 | 0.7132 | -0.0050 | -0.7% |

## Defense Recovery

| Model | Attack | Artifact | Placement | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `fgsm` | `` | `` | `median_preprocess` | `untargeted_conf_suppression` |  | `` | 0.7132 | 0.6639 | 991.6% |

## Imported Patch Recovery

No imported patch comparisons found.

## Per-Class Detection Drop

| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |
|---|---:|---|---:|---|---:|---:|---:|
| `yolo` | 42 | `fgsm` | 0 | person | 6 | 5 | 16.7% |
| `yolo` | 42 | `fgsm` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 56 | chair | 3 | 4 | -33.3% |
| `yolo` | 42 | `fgsm` | 58 | potted plant | 4 | 4 | 0.0% |
| `yolo` | 42 | `fgsm` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 60 | dining table | 0 | 1 |  |
| `yolo` | 42 | `fgsm` | 62 | tv | 2 | 3 | -50.0% |
| `yolo` | 42 | `fgsm` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 73 | book | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 77 | teddy bear | 3 | 3 | 0.0% |