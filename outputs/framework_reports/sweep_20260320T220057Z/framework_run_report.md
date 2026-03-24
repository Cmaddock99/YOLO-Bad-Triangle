# Framework Run Comparison Report

Total discovered framework runs: **9**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `complete` | 0.5244 | 0.7547 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `complete` | 0.5984 | 0.7648 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `complete` | 0.5192 | 0.7621 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `complete` | 0.5322 | 0.7642 |
| `baseline_none` | `yolo` | `none` | `none` | `complete` | 0.5984 | 0.7648 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `complete` | 0.5082 | 0.7522 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `complete` | 0.5789 | 0.7661 |
| `defended_fgsm_median_preprocess` | `yolo` | `fgsm` | `median_preprocess` | `complete` | 0.4851 | 0.7592 |
| `defended_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `complete` | 0.4916 | 0.7541 |

## Attack Effectiveness

| Model | Seed | Attack | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | 0.5984 | 0.5244 | 0.0740 | 12.4% |
| `yolo` | 42 | `deepfool` | 0.5984 | 0.5984 | 0.0000 | 0.0% |
| `yolo` | 42 | `fgsm` | 0.5984 | 0.5192 | 0.0792 | 13.2% |
| `yolo` | 42 | `pgd` | 0.5984 | 0.5322 | 0.0662 | 11.1% |

## Defense Recovery

| Model | Attack | Defense | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---:|---:|---:|
| `yolo` | `blur` | `median_preprocess` | 0.5244 | 0.5082 | -21.9% |
| `yolo` | `deepfool` | `median_preprocess` | 0.5984 | 0.5789 |  |
| `yolo` | `fgsm` | `median_preprocess` | 0.5192 | 0.4851 | -43.0% |
| `yolo` | `pgd` | `median_preprocess` | 0.5322 | 0.4916 | -61.2% |