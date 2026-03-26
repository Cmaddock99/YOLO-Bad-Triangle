# Framework Run Comparison Report

Total discovered framework runs: **86**

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
| `defended_blur_random_resize` | `yolo` | `blur` | `random_resize` | `missing` |  | 0.7765 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7955 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7528 |
| `defended_deepfool_c_dog_ensemble` | `yolo` | `deepfool` | `c_dog_ensemble` | `missing` |  | 0.8318 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8412 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `missing` |  | 0.7835 |
| `defended_deepfool_random_resize` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8165 |
| `defended_eot_pgd_bit_depth` | `yolo` | `eot_pgd` | `bit_depth` | `missing` |  | 0.8552 |
| `defended_eot_pgd_c_dog` | `yolo` | `eot_pgd` | `c_dog` | `missing` |  | 0.7324 |
| `defended_eot_pgd_c_dog_ensemble` | `yolo` | `eot_pgd` | `c_dog_ensemble` | `missing` |  | 0.7942 |
| `defended_eot_pgd_jpeg_preprocess` | `yolo` | `eot_pgd` | `jpeg_preprocess` | `missing` |  | 0.7866 |
| `defended_eot_pgd_median_preprocess` | `yolo` | `eot_pgd` | `median_preprocess` | `missing` |  | 0.8200 |
| `defended_eot_pgd_random_resize` | `yolo` | `eot_pgd` | `random_resize` | `missing` |  | 0.8025 |
| `tune_atk_blur_001` | `yolo` | `blur` | `none` | `missing` |  | 0.7239 |
| `tune_atk_blur_002` | `yolo` | `blur` | `none` | `missing` |  | 0.7260 |
| `tune_atk_blur_003` | `yolo` | `blur` | `none` | `missing` |  | 0.7434 |
| `tune_atk_blur_004` | `yolo` | `blur` | `none` | `missing` |  | 0.7626 |
| `tune_atk_blur_005` | `yolo` | `blur` | `none` | `missing` |  | 0.7239 |
| `tune_atk_deepfool_001` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7549 |
| `tune_atk_deepfool_002` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7701 |
| `tune_atk_deepfool_003` | `yolo` | `deepfool` | `none` | `missing` |  | 0.8025 |
| `tune_atk_deepfool_004` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7730 |
| `tune_atk_deepfool_005` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7346 |
| `tune_atk_deepfool_006` | `yolo` | `deepfool` | `none` | `missing` |  | 0.8442 |
| `tune_atk_deepfool_007` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7549 |
| `tune_atk_deepfool_008` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7730 |
| `tune_atk_deepfool_009` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7346 |
| `tune_atk_deepfool_best` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7701 |
| `tune_atk_eot_pgd_001` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7956 |
| `tune_atk_eot_pgd_002` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8229 |
| `tune_atk_eot_pgd_003` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7816 |
| `tune_atk_eot_pgd_004` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7688 |
| `tune_atk_eot_pgd_005` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7906 |
| `tune_atk_eot_pgd_006` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7823 |
| `tune_atk_eot_pgd_007` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8037 |
| `tune_atk_eot_pgd_008` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7597 |
| `tune_atk_eot_pgd_009` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7732 |
| `tune_atk_eot_pgd_010` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8269 |
| `tune_atk_eot_pgd_011` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8220 |
| `tune_atk_eot_pgd_012` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8090 |
| `tune_atk_eot_pgd_013` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7966 |
| `tune_atk_eot_pgd_014` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7955 |
| `tune_atk_eot_pgd_015` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7597 |
| `tune_atk_eot_pgd_016` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8673 |
| `tune_atk_eot_pgd_017` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7954 |
| `tune_atk_eot_pgd_018` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8046 |
| `tune_atk_eot_pgd_019` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.8673 |
| `tune_atk_eot_pgd_020` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7954 |
| `tune_def_bit_depth_001` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7955 |
| `tune_def_bit_depth_002` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.8301 |
| `tune_def_bit_depth_003` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7798 |
| `tune_def_jpeg_preprocess_001` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8412 |
| `tune_def_jpeg_preprocess_002` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8588 |
| `tune_def_jpeg_preprocess_003` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.7779 |
| `tune_def_jpeg_preprocess_004` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8412 |
| `tune_def_jpeg_preprocess_005` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.8051 |
| `tune_def_random_resize_001` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8165 |
| `tune_def_random_resize_002` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8670 |
| `tune_def_random_resize_003` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8662 |
| `tune_def_random_resize_004` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8165 |
| `tune_def_random_resize_005` | `yolo` | `deepfool` | `random_resize` | `missing` |  | 0.8134 |
| `validate_atk_blur` | `yolo` | `blur` | `none` | `complete` | 0.2636 | 0.7346 |
| `validate_atk_deepfool` | `yolo` | `deepfool` | `none` | `complete` | 0.2184 | 0.7562 |
| `validate_atk_eot_pgd` | `yolo` | `eot_pgd` | `none` | `complete` | 0.2529 | 0.7481 |
| `validate_baseline` | `yolo` | `none` | `none` | `complete` | 0.6002 | 0.7648 |
| `validate_blur_bit_depth` | `yolo` | `blur` | `bit_depth` | `complete` | 0.2615 | 0.7336 |
| `validate_blur_jpeg_preprocess` | `yolo` | `blur` | `jpeg_preprocess` | `complete` | 0.2603 | 0.7301 |
| `validate_blur_random_resize` | `yolo` | `blur` | `random_resize` | `complete` | 0.1489 | 0.7384 |
| `validate_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `complete` | 0.2276 | 0.7472 |
| `validate_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `complete` | 0.1837 | 0.7518 |
| `validate_deepfool_random_resize` | `yolo` | `deepfool` | `random_resize` | `complete` | 0.1185 | 0.7448 |
| `validate_eot_pgd_bit_depth` | `yolo` | `eot_pgd` | `bit_depth` | `complete` | 0.2555 | 0.7502 |
| `validate_eot_pgd_jpeg_preprocess` | `yolo` | `eot_pgd` | `jpeg_preprocess` | `complete` | 0.2284 | 0.7470 |

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
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  | 0.2636 |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  | 0.2184 |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  | 0.2529 |  |  |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `blur` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `c_dog_ensemble` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `random_resize` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog_ensemble` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `c_dog_ensemble` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `eot_pgd` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `blur` | `bit_depth` | `` |  | `` |  | 0.2615 |  |
| `yolo` | `blur` | `jpeg_preprocess` | `` |  | `` |  | 0.2603 |  |
| `yolo` | `blur` | `random_resize` | `` |  | `` |  | 0.1489 |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  | 0.2276 |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  | 0.1837 |  |
| `yolo` | `deepfool` | `random_resize` | `untargeted_conf_suppression` |  | `` |  | 0.1185 |  |
| `yolo` | `eot_pgd` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  | 0.2555 |  |
| `yolo` | `eot_pgd` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  | 0.2284 |  |

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
| `yolo` | 42 | `blur` | 0 | person | 4 | 1 | 75.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 4 | 1 | 75.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 4 | 1 | 75.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
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
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 2 | -100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
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
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
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
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 3 | 25.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
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
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 3 | 25.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 29 | frisbee | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 29 | frisbee | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 29 | frisbee | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 4 | 287 | -7075.0% |
| `yolo` | 42 | `blur` | 2 | car | 0 | 15 |  |
| `yolo` | 42 | `blur` | 3 | motorcycle | 0 | 4 |  |
| `yolo` | 42 | `blur` | 4 | airplane | 0 | 4 |  |
| `yolo` | 42 | `blur` | 5 | bus | 0 | 13 |  |
| `yolo` | 42 | `blur` | 6 | train | 0 | 4 |  |
| `yolo` | 42 | `blur` | 7 | truck | 0 | 3 |  |
| `yolo` | 42 | `blur` | 8 | boat | 0 | 2 |  |
| `yolo` | 42 | `blur` | 10 | fire hydrant | 0 | 3 |  |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 12 | parking meter | 0 | 3 |  |
| `yolo` | 42 | `blur` | 14 | bird | 0 | 1 |  |
| `yolo` | 42 | `blur` | 15 | cat | 0 | 5 |  |
| `yolo` | 42 | `blur` | 16 | dog | 0 | 5 |  |
| `yolo` | 42 | `blur` | 17 | horse | 0 | 3 |  |
| `yolo` | 42 | `blur` | 18 | sheep | 0 | 11 |  |
| `yolo` | 42 | `blur` | 20 | elephant | 0 | 9 |  |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 0 | 3 |  |
| `yolo` | 42 | `blur` | 23 | giraffe | 0 | 4 |  |
| `yolo` | 42 | `blur` | 25 | umbrella | 0 | 4 |  |
| `yolo` | 42 | `blur` | 27 | tie | 0 | 5 |  |
| `yolo` | 42 | `blur` | 28 | suitcase | 0 | 1 |  |
| `yolo` | 42 | `blur` | 29 | frisbee | 0 | 7 |  |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 32 | sports ball | 0 | 5 |  |
| `yolo` | 42 | `blur` | 33 | kite | 0 | 2 |  |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 36 | skateboard | 0 | 1 |  |
| `yolo` | 42 | `blur` | 37 | surfboard | 0 | 4 |  |
| `yolo` | 42 | `blur` | 38 | tennis racket | 0 | 3 |  |
| `yolo` | 42 | `blur` | 39 | bottle | 0 | 2 |  |
| `yolo` | 42 | `blur` | 40 | wine glass | 0 | 2 |  |
| `yolo` | 42 | `blur` | 41 | cup | 0 | 6 |  |
| `yolo` | 42 | `blur` | 45 | bowl | 0 | 9 |  |
| `yolo` | 42 | `blur` | 46 | banana | 0 | 5 |  |
| `yolo` | 42 | `blur` | 47 | apple | 0 | 4 |  |
| `yolo` | 42 | `blur` | 48 | sandwich | 0 | 1 |  |
| `yolo` | 42 | `blur` | 49 | orange | 0 | 10 |  |
| `yolo` | 42 | `blur` | 50 | broccoli | 0 | 3 |  |
| `yolo` | 42 | `blur` | 51 | carrot | 0 | 2 |  |
| `yolo` | 42 | `blur` | 52 | hot dog | 0 | 3 |  |
| `yolo` | 42 | `blur` | 53 | pizza | 0 | 8 |  |
| `yolo` | 42 | `blur` | 54 | donut | 0 | 2 |  |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 6 | -100.0% |
| `yolo` | 42 | `blur` | 57 | couch | 0 | 3 |  |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 1 | 4 | -300.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 0 | 8 |  |
| `yolo` | 42 | `blur` | 61 | toilet | 0 | 6 |  |
| `yolo` | 42 | `blur` | 62 | tv | 2 | 9 | -350.0% |
| `yolo` | 42 | `blur` | 63 | laptop | 0 | 12 |  |
| `yolo` | 42 | `blur` | 64 | mouse | 0 | 3 |  |
| `yolo` | 42 | `blur` | 65 | remote | 0 | 2 |  |
| `yolo` | 42 | `blur` | 66 | keyboard | 0 | 1 |  |
| `yolo` | 42 | `blur` | 67 | cell phone | 0 | 4 |  |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 4 | 122 | -2950.0% |
| `yolo` | 42 | `deepfool` | 1 | bicycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 2 | car | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 3 | motorcycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 4 | airplane | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 5 | bus | 0 | 5 |  |
| `yolo` | 42 | `deepfool` | 6 | train | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 7 | truck | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 9 | traffic light | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 10 | fire hydrant | 0 | 6 |  |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 15 | cat | 0 | 5 |  |
| `yolo` | 42 | `deepfool` | 16 | dog | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 17 | horse | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 18 | sheep | 0 | 5 |  |
| `yolo` | 42 | `deepfool` | 19 | cow | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 20 | elephant | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 4 | -300.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 0 | 14 |  |
| `yolo` | 42 | `deepfool` | 23 | giraffe | 0 | 7 |  |
| `yolo` | 42 | `deepfool` | 27 | tie | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 29 | frisbee | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 33 | kite | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 36 | skateboard | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 37 | surfboard | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 0 | 7 |  |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 45 | bowl | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 46 | banana | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 50 | broccoli | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 51 | carrot | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 53 | pizza | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 57 | couch | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 1 | 4 | -300.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 61 | toilet | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 62 | tv | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 65 | remote | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 4 | 282 | -6950.0% |
| `yolo` | 42 | `eot_pgd` | 1 | bicycle | 0 | 7 |  |
| `yolo` | 42 | `eot_pgd` | 2 | car | 0 | 25 |  |
| `yolo` | 42 | `eot_pgd` | 3 | motorcycle | 0 | 4 |  |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 6 | train | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 9 | traffic light | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 10 | fire hydrant | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `eot_pgd` | 12 | parking meter | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 13 | bench | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 0 | 8 |  |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 0 | 12 |  |
| `yolo` | 42 | `eot_pgd` | 16 | dog | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 17 | horse | 0 | 7 |  |
| `yolo` | 42 | `eot_pgd` | 18 | sheep | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 19 | cow | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 16 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 0 | 21 |  |
| `yolo` | 42 | `eot_pgd` | 23 | giraffe | 0 | 12 |  |
| `yolo` | 42 | `eot_pgd` | 25 | umbrella | 0 | 4 |  |
| `yolo` | 42 | `eot_pgd` | 27 | tie | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 29 | frisbee | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 3 | -200.0% |
| `yolo` | 42 | `eot_pgd` | 31 | snowboard | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 32 | sports ball | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 33 | kite | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 0 | 3 |  |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 3 | -200.0% |
| `yolo` | 42 | `eot_pgd` | 36 | skateboard | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 37 | surfboard | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 0 | 10 |  |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 0 | 7 |  |
| `yolo` | 42 | `eot_pgd` | 49 | orange | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 50 | broccoli | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 52 | hot dog | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 53 | pizza | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 54 | donut | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 9 | -200.0% |
| `yolo` | 42 | `eot_pgd` | 57 | couch | 0 | 9 |  |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 1 | 7 | -600.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 61 | toilet | 0 | 13 |  |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 2 | 4 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 0 | 3 |  |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 0 | 5 |  |
| `yolo` | 42 | `eot_pgd` | 65 | remote | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 67 | cell phone | 0 | 7 |  |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 71 | sink | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 7 | -600.0% |
| `yolo` | 42 | `eot_pgd` | 75 | vase | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 3 | -50.0% |