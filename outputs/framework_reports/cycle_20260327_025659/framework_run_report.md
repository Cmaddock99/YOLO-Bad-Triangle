# Framework Run Comparison Report

Total discovered framework runs: **23**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7272 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7549 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7956 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7521 |
| `attack_jpeg_attack` | `yolo` | `jpeg_attack` | `none` | `missing` |  | 0.7485 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7646 |
| `attack_square` | `yolo` | `square` | `none` | `missing` |  | 0.7183 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7658 |
| `defended_blur_bit_depth` | `yolo` | `blur` | `bit_depth` | `missing` |  | 0.6947 |
| `defended_blur_c_dog` | `yolo` | `blur` | `c_dog` | `missing` |  | 0.7215 |
| `defended_blur_c_dog_ensemble` | `yolo` | `blur` | `c_dog_ensemble` | `missing` |  | 0.7271 |
| `defended_blur_jpeg_preprocess` | `yolo` | `blur` | `jpeg_preprocess` | `missing` |  | 0.7006 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `missing` |  | 0.7016 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7955 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7528 |
| `defended_deepfool_c_dog_ensemble` | `yolo` | `deepfool` | `c_dog_ensemble` | `missing` |  | 0.8318 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8412 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `missing` |  | 0.7835 |
| `defended_eot_pgd_bit_depth` | `yolo` | `eot_pgd` | `bit_depth` | `missing` |  | 0.8552 |
| `defended_eot_pgd_c_dog` | `yolo` | `eot_pgd` | `c_dog` | `missing` |  | 0.7324 |
| `defended_eot_pgd_c_dog_ensemble` | `yolo` | `eot_pgd` | `c_dog_ensemble` | `missing` |  | 0.7942 |
| `defended_eot_pgd_jpeg_preprocess` | `yolo` | `eot_pgd` | `jpeg_preprocess` | `missing` |  | 0.7866 |
| `defended_eot_pgd_median_preprocess` | `yolo` | `eot_pgd` | `median_preprocess` | `missing` |  | 0.8200 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `jpeg_attack` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `blur` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `c_dog_ensemble` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog_ensemble` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `c_dog_ensemble` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |

## Per-Class Detection Drop

| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |
|---|---:|---|---:|---|---:|---:|---:|
| `yolo` | 42 | `blur` | 0 | person | 4 | 4 | 0.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 0 | person | 4 | 4 | 0.0% |
| `yolo` | 42 | `fgsm` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `jpeg_attack` | 0 | person | 4 | 4 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `jpeg_attack` | 58 | potted plant | 2 | 3 | -50.0% |
| `yolo` | 42 | `jpeg_attack` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `jpeg_attack` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 0 | person | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `pgd` | 58 | potted plant | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |