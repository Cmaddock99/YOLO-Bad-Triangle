# Framework Run Comparison Report

Total discovered framework runs: **48**

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
| `tune_atk_blur_kern15` | `yolo` | `blur` | `none` | `missing` |  | 0.7811 |
| `tune_atk_blur_kern21` | `yolo` | `blur` | `none` | `missing` |  | 0.7434 |
| `tune_atk_blur_kern5` | `yolo` | `blur` | `none` | `missing` |  | 0.7543 |
| `tune_atk_blur_kern9` | `yolo` | `blur` | `none` | `missing` |  | 0.7272 |
| `tune_atk_gaussian_blur_kern15` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7811 |
| `tune_atk_gaussian_blur_kern21` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7434 |
| `tune_atk_gaussian_blur_kern5` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7543 |
| `tune_atk_gaussian_blur_kern9` | `yolo` | `gaussian_blur` | `none` | `missing` |  | 0.7272 |
| `tune_atk_pgd_epsi0.008_step10` | `yolo` | `pgd` | `none` | `missing` |  | 0.7248 |
| `tune_atk_pgd_epsi0.008_step20` | `yolo` | `pgd` | `none` | `missing` |  | 0.7308 |
| `tune_atk_pgd_epsi0.008_step40` | `yolo` | `pgd` | `none` | `missing` |  | 0.7262 |
| `tune_atk_pgd_epsi0.016_step10` | `yolo` | `pgd` | `none` | `missing` |  | 0.7191 |
| `tune_atk_pgd_epsi0.016_step20` | `yolo` | `pgd` | `none` | `missing` |  | 0.7374 |
| `tune_atk_pgd_epsi0.016_step40` | `yolo` | `pgd` | `none` | `missing` |  | 0.7626 |
| `tune_atk_pgd_epsi0.032_step10` | `yolo` | `pgd` | `none` | `missing` |  | 0.7573 |
| `tune_atk_pgd_epsi0.032_step20` | `yolo` | `pgd` | `none` | `missing` |  | 0.7541 |
| `tune_atk_pgd_epsi0.032_step40` | `yolo` | `pgd` | `none` | `missing` |  | 0.7429 |
| `tune_def_confidence_filter_thre0.3` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.7272 |
| `tune_def_confidence_filter_thre0.4` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.7272 |
| `tune_def_confidence_filter_thre0.5` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.7272 |
| `tune_def_confidence_filter_thre0.6` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.7774 |
| `tune_def_confidence_filter_thre0.7` | `yolo` | `gaussian_blur` | `confidence_filter` | `missing` |  | 0.8590 |
| `tune_def_median_preprocess_kern3` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7016 |
| `tune_def_median_preprocess_kern5` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7239 |
| `tune_def_median_preprocess_kern7` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.8002 |
| `tune_def_median_preprocess_kern9` | `yolo` | `gaussian_blur` | `median_preprocess` | `missing` |  | 0.7775 |
| `validate_atk_pgd` | `yolo` | `pgd` | `none` | `complete` | 0.5511 | 0.7675 |
| `validate_blur_confidence_filter` | `yolo` | `blur` | `confidence_filter` | `complete` | 0.5260 | 0.8464 |
| `validate_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `complete` | 0.4464 | 0.7552 |
| `validate_gaussian_blur_confidence_filter` | `yolo` | `gaussian_blur` | `confidence_filter` | `complete` | 0.5260 | 0.8464 |
| `validate_gaussian_blur_median_preprocess` | `yolo` | `gaussian_blur` | `median_preprocess` | `complete` | 0.4464 | 0.7552 |
| `validate_pgd_confidence_filter` | `yolo` | `pgd` | `confidence_filter` | `complete` | 0.5511 | 0.8504 |
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
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `gaussian_blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
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
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `blur` | `confidence_filter` | `` |  | `` |  | 0.5260 |  |
| `yolo` | `blur` | `median_preprocess` | `` |  | `` |  | 0.4464 |  |
| `yolo` | `gaussian_blur` | `confidence_filter` | `` |  | `` |  | 0.5260 |  |
| `yolo` | `gaussian_blur` | `median_preprocess` | `` |  | `` |  | 0.4464 |  |
| `yolo` | `pgd` | `confidence_filter` | `untargeted_conf_suppression` |  | `` |  | 0.5511 |  |
| `yolo` | `pgd` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  | 0.3854 |  |