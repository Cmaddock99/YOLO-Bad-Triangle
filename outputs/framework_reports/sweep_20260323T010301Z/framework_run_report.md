# Framework Run Comparison Report

Total discovered framework runs: **4**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `defended_blur_c_dog` | `yolo` | `blur` | `c_dog` | `missing` |  | 0.7548 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7265 |
| `defended_fgsm_c_dog` | `yolo` | `fgsm` | `c_dog` | `missing` |  | 0.7562 |
| `defended_pgd_c_dog` | `yolo` | `pgd` | `c_dog` | `missing` |  | 0.7616 |

## Attack Effectiveness

No baseline/attack pairs found.

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `blur` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `fgsm` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `pgd` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |