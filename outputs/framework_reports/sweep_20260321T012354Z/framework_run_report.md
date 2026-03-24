# Framework Run Comparison Report

Total discovered framework runs: **13**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7318 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7756 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7581 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7629 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.8873 |
| `defended_deepfool_c_dog_ensemble` | `yolo` | `deepfool` | `c_dog_ensemble` | `missing` |  | 0.5594 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `missing` |  | 0.7577 |
| `defended_fgsm_c_dog` | `yolo` | `fgsm` | `c_dog` | `missing` |  | 0.7932 |
| `defended_fgsm_c_dog_ensemble` | `yolo` | `fgsm` | `c_dog_ensemble` | `missing` |  | 0.6970 |
| `defended_fgsm_median_preprocess` | `yolo` | `fgsm` | `median_preprocess` | `missing` |  | 0.7658 |
| `defended_pgd_c_dog` | `yolo` | `pgd` | `c_dog` | `missing` |  | 0.7669 |
| `defended_pgd_c_dog_ensemble` | `yolo` | `pgd` | `c_dog_ensemble` | `missing` |  | 0.6658 |
| `defended_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `missing` |  | 0.7582 |

## Attack Effectiveness

| Model | Seed | Attack | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `deepfool` |  |  |  |  |
| `yolo` | 42 | `fgsm` |  |  |  |  |
| `yolo` | 42 | `pgd` |  |  |  |  |

## Defense Recovery

| Model | Attack | Defense | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---:|---:|---:|
| `yolo` | `deepfool` | `c_dog` |  |  |  |
| `yolo` | `deepfool` | `c_dog_ensemble` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` |  |  |  |
| `yolo` | `fgsm` | `c_dog` |  |  |  |
| `yolo` | `fgsm` | `c_dog_ensemble` |  |  |  |
| `yolo` | `fgsm` | `median_preprocess` |  |  |  |
| `yolo` | `pgd` | `c_dog` |  |  |  |
| `yolo` | `pgd` | `c_dog_ensemble` |  |  |  |
| `yolo` | `pgd` | `median_preprocess` |  |  |  |