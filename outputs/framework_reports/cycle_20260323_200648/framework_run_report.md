# Framework Run Comparison Report

Total discovered framework runs: **9**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7272 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7516 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8156 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7522 |
| `attack_fgsm_center_mask` | `yolo` | `fgsm_center_mask` | `none` | `missing` |  | 0.7540 |
| `attack_fgsm_edge_mask` | `yolo` | `fgsm_edge_mask` | `none` | `missing` |  | 0.7596 |
| `attack_gaussian_blur` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7272 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7374 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7658 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm_center_mask` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm_edge_mask` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |

## Defense Recovery

No defended runs found. Run with `--defenses` to enable defense sweep.