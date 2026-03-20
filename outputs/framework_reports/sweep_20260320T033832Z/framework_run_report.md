# Framework Run Comparison Report

Total discovered framework runs: **5**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7272 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7571 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7522 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7566 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7658 |

## Baseline vs Attack Deltas

| Model | Defense | Seed | Attack run | Attack | mAP50 drop | Avg conf drop |
|---|---|---:|---|---|---:|---:|
| `yolo` | `none` | 42 | `attack_blur` | `blur` |  | 0.0386 |
| `yolo` | `none` | 42 | `attack_deepfool` | `deepfool` |  | 0.0087 |
| `yolo` | `none` | 42 | `attack_fgsm` | `fgsm` |  | 0.0136 |
| `yolo` | `none` | 42 | `attack_pgd` | `pgd` |  | 0.0093 |