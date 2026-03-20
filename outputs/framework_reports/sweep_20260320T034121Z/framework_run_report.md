# Framework Run Comparison Report

Total discovered framework runs: **5**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7547 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7661 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7621 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7625 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7648 |

## Baseline vs Attack Deltas

| Model | Defense | Seed | Attack run | Attack | mAP50 drop | Avg conf drop |
|---|---|---:|---|---|---:|---:|
| `yolo` | `none` | 42 | `attack_blur` | `blur` |  | 0.0101 |
| `yolo` | `none` | 42 | `attack_deepfool` | `deepfool` |  | -0.0013 |
| `yolo` | `none` | 42 | `attack_fgsm` | `fgsm` |  | 0.0026 |
| `yolo` | `none` | 42 | `attack_pgd` | `pgd` |  | 0.0023 |