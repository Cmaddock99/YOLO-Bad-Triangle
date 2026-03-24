# Framework Run Comparison Report

Total discovered framework runs: **41**

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
| `defended_blur_confidence_filter` | `yolo` | `blur` | `confidence_filter` | `missing` |  | 0.7547 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `missing` |  | 0.7522 |
| `defended_gaussian_blur_confidence_filter` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.7547 |
| `defended_gaussian_blur_median_preprocess` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7522 |
| `defended_pgd_confidence_filter` | `yolo` | `pgd` | `confidence_filter` | `missing` |  | 0.7639 |
| `defended_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `missing` |  | 0.7607 |
| `tune_atk_blur_001` | `yolo` | `blur` | `none` | `missing` |  | 0.7163 |
| `tune_atk_blur_002` | `yolo` | `blur` | `none` | `missing` |  | 0.7319 |
| `tune_atk_blur_003` | `yolo` | `blur` | `none` | `missing` |  | 0.7260 |
| `tune_atk_gaussian_blur_001` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7163 |
| `tune_atk_gaussian_blur_002` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7319 |
| `tune_atk_gaussian_blur_003` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7260 |
| `tune_atk_gaussian_blur_best` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7163 |
| `tune_atk_pgd_001` | `yolo` | `pgd` | `none` | `missing` |  | 0.7385 |
| `tune_atk_pgd_002` | `yolo` | `pgd` | `none` | `missing` |  | 0.7570 |
| `tune_atk_pgd_003` | `yolo` | `pgd` | `none` | `missing` |  | 0.7475 |
| `tune_atk_pgd_004` | `yolo` | `pgd` | `none` | `missing` |  | 0.7482 |
| `tune_def_confidence_filter_001` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.9375 |
| `tune_def_confidence_filter_002` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.8766 |
| `tune_def_median_preprocess_001` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7464 |
| `tune_def_median_preprocess_002` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7438 |
| `tune_def_median_preprocess_003` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7381 |
| `validate_atk_blur` | `yolo` | `blur` | `none` | `complete` | 0.3160 | 0.7465 |
| `validate_atk_gaussian_blur` | `yolo` | `gaussian_blur` | `none` | `complete` | 0.3160 | 0.7465 |
| `validate_atk_pgd` | `yolo` | `pgd` | `none` | `complete` | 0.5511 | 0.7675 |
| `validate_baseline` | `yolo` | `none` | `none` | `complete` | 0.6002 | 0.7648 |
| `validate_blur_confidence_filter` | `yolo` | `blur` | `confidence_filter` | `complete` | 0.3160 | 0.9231 |
| `validate_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `complete` | 0.2724 | 0.7390 |
| `validate_gaussian_blur_confidence_filter` | `yolo` | `gaussian_blur` | `confidence_filter` | `complete` | 0.3160 | 0.9231 |
| `validate_gaussian_blur_median_preprocess` | `yolo` | `gaussian_blur` | `median_preprocess` | `complete` | 0.2724 | 0.7390 |
| `validate_pgd_confidence_filter` | `yolo` | `pgd` | `confidence_filter` | `complete` | 0.5511 | 0.9277 |
| `validate_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `complete` | 0.3854 | 0.7563 |

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
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` |  | `` |  | 0.3160 |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  | 0.3160 |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  | 0.5511 |  |  |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `pgd` | `confidence_filter` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `confidence_filter` | `` |  | `` |  | 0.3160 |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  | 0.2724 |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  | 0.3160 |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  | 0.2724 |  |
| `yolo` | `pgd` | `confidence_filter` | `untargeted_conf_suppression` |  | `` |  | 0.5511 |  |
| `yolo` | `pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  | 0.3854 |  |