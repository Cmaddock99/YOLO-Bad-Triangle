# Framework Run Comparison Report

Total discovered framework runs: **5**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_cw` | `yolo` | `cw` | `none` | `missing` |  | 0.7658 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7658 |
| `defended_cw_c_dog` | `yolo` | `cw` | `c_dog` | `missing` |  | 0.7252 |
| `defended_cw_jpeg_preprocess` | `yolo` | `cw` | `jpeg_preprocess` | `missing` |  | 0.7485 |
| `defended_cw_median_preprocess` | `yolo` | `cw` | `median_preprocess` | `missing` |  | 0.7705 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `cw` | `` |  | `` |  |  |  |  |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `cw` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `cw` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `cw` | `median_preprocess` | `` |  | `` |  |  |  |