# Framework Run Comparison Report

Total discovered framework runs: **8**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_bim` | `yolo` | `bim` | `none` | `missing` |  | 0.7936 |
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7272 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7625 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7522 |
| `attack_gaussian_blur` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7272 |
| `attack_ifgsm` | `yolo` | `ifgsm` | `none` | `missing` |  | 0.7367 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7905 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7658 |

## Baseline vs Attack Deltas

| Model | Defense | Seed | Attack run | Attack | mAP50 drop | Avg conf drop |
|---|---|---:|---|---|---:|---:|
| `yolo` | `none` | 42 | `attack_bim` | `bim` |  | -0.0278 |
| `yolo` | `none` | 42 | `attack_blur` | `blur` |  | 0.0386 |
| `yolo` | `none` | 42 | `attack_deepfool` | `deepfool` |  | 0.0033 |
| `yolo` | `none` | 42 | `attack_fgsm` | `fgsm` |  | 0.0136 |
| `yolo` | `none` | 42 | `attack_gaussian_blur` | `gaussian_blur` |  | 0.0386 |
| `yolo` | `none` | 42 | `attack_ifgsm` | `ifgsm` |  | 0.0291 |
| `yolo` | `none` | 42 | `attack_pgd` | `pgd` |  | -0.0247 |