# Framework Run Comparison Report

Total discovered framework runs: **13**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7547 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7482 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7621 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7641 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7648 |
| `defended_blur_c_dog` | `yolo` | `blur` | `c_dog` | `missing` |  | 0.7566 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `missing` |  | 0.7522 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7408 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `missing` |  | 0.7480 |
| `defended_fgsm_c_dog` | `yolo` | `fgsm` | `c_dog` | `missing` |  | 0.7578 |
| `defended_fgsm_median_preprocess` | `yolo` | `fgsm` | `median_preprocess` | `missing` |  | 0.7592 |
| `defended_pgd_c_dog` | `yolo` | `pgd` | `c_dog` | `missing` |  | 0.7549 |
| `defended_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `missing` |  | 0.7573 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `` |  | `` |  |  |  |  |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `blur` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `fgsm` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `fgsm` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `pgd` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |