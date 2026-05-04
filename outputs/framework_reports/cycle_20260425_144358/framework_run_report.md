# Framework Run Comparison Report

Total discovered framework runs: **92**

Pipeline profile: `yolo11n_lab_v1`
Authoritative metric: `mAP50`

## Run Inventory

| Run | Model | Attack | Artifact | Placement | Defense | Semantics | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7301 |
| `attack_deepfool` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6788 |
| `attack_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7162 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7298 |
| `attack_fgsm` | `yolo` | `fgsm` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7500 |
| `attack_pgd` | `yolo` | `pgd` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7440 |
| `attack_square` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7378 |
| `baseline_none` | `yolo` | `none` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7469 |
| `consistency_atk_square` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7376 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.6763 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7028 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.6966 |
| `defended_dispersion_reduction_bit_depth` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7263 |
| `defended_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7249 |
| `defended_dispersion_reduction_median_preprocess` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7465 |
| `defended_square_bit_depth` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7447 |
| `defended_square_jpeg_preprocess` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7334 |
| `defended_square_median_preprocess` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7410 |
| `tune_atk_deepfool__epsilon0.15__steps200` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6429 |
| `tune_atk_deepfool__epsilon0.3__steps170` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  |  |
| `tune_atk_deepfool__epsilon0.3__steps200` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  |  |
| `tune_atk_deepfool_scan__epsilon0.005__steps50` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7772 |
| `tune_atk_deepfool_scan__epsilon0.05__steps10` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6792 |
| `tune_atk_deepfool_scan__epsilon0.05__steps105` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7550 |
| `tune_atk_deepfool_scan__epsilon0.05__steps200` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7189 |
| `tune_atk_deepfool_scan__epsilon0.1525__steps50` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7482 |
| `tune_atk_deepfool_scan__epsilon0.3__steps50` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `missing` |  |  |
| `tune_atk_dispersion_reduction__epsilon0.075__steps100` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7395 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps100` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6891 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps80` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6879 |
| `tune_atk_dispersion_reduction_best` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.6891 |
| `tune_atk_dispersion_reduction_scan__epsilon0.01__steps50` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7813 |
| `tune_atk_dispersion_reduction_scan__epsilon0.05__steps100` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7425 |
| `tune_atk_dispersion_reduction_scan__epsilon0.05__steps20` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7684 |
| `tune_atk_dispersion_reduction_scan__epsilon0.05__steps60` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7466 |
| `tune_atk_dispersion_reduction_scan__epsilon0.08__steps50` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7438 |
| `tune_atk_dispersion_reduction_scan__epsilon0.15__steps50` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7311 |
| `tune_atk_square__eps0.15__n_queries500` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7344 |
| `tune_atk_square__eps0.3__n_queries450` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7506 |
| `tune_atk_square__eps0.3__n_queries500` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7895 |
| `tune_atk_square_best` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7895 |
| `tune_atk_square_scan__eps0.01__n_queries100` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7885 |
| `tune_atk_square_scan__eps0.05__n_queries275` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7639 |
| `tune_atk_square_scan__eps0.05__n_queries50` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7807 |
| `tune_atk_square_scan__eps0.05__n_queries500` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7745 |
| `tune_atk_square_scan__eps0.155__n_queries100` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7368 |
| `tune_atk_square_scan__eps0.3__n_queries100` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `missing` |  | 0.7353 |
| `tune_def_bit_depth__bits4_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7523 |
| `tune_def_bit_depth__bits4_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7354 |
| `tune_def_bit_depth__bits5_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7576 |
| `tune_def_bit_depth__bits5_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7395 |
| `tune_def_bit_depth__bits6_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7631 |
| `tune_def_bit_depth__bits6_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7549 |
| `tune_def_bit_depth_scan__bits3_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7360 |
| `tune_def_bit_depth_scan__bits3_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7510 |
| `tune_def_bit_depth_scan__bits5_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7576 |
| `tune_def_bit_depth_scan__bits5_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7395 |
| `tune_def_bit_depth_scan__bits7_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7610 |
| `tune_def_bit_depth_scan__bits7_vs_square` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7394 |
| `tune_def_jpeg_preprocess__quality40_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7223 |
| `tune_def_jpeg_preprocess__quality40_vs_square` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7625 |
| `tune_def_jpeg_preprocess__quality55_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7520 |
| `tune_def_jpeg_preprocess__quality55_vs_square` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7933 |
| `tune_def_jpeg_preprocess_scan__quality40_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7223 |
| `tune_def_jpeg_preprocess_scan__quality40_vs_square` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7625 |
| `tune_def_jpeg_preprocess_scan__quality68_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7484 |
| `tune_def_jpeg_preprocess_scan__quality68_vs_square` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7555 |
| `tune_def_jpeg_preprocess_scan__quality95_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7629 |
| `tune_def_jpeg_preprocess_scan__quality95_vs_square` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7401 |
| `tune_def_median_preprocess__kernel_size3_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7685 |
| `tune_def_median_preprocess__kernel_size3_vs_square` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7569 |
| `tune_def_median_preprocess__kernel_size5_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7333 |
| `tune_def_median_preprocess__kernel_size5_vs_square` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7621 |
| `tune_def_median_preprocess_scan__kernel_size17_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7272 |
| `tune_def_median_preprocess_scan__kernel_size17_vs_square` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7368 |
| `tune_def_median_preprocess_scan__kernel_size31_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7542 |
| `tune_def_median_preprocess_scan__kernel_size31_vs_square` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7938 |
| `tune_def_median_preprocess_scan__kernel_size3_vs_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7685 |
| `tune_def_median_preprocess_scan__kernel_size3_vs_square` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7569 |
| `validate_atk_deepfool` | `yolo` | `deepfool` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.0363 |  |
| `validate_atk_dispersion_reduction` | `yolo` | `dispersion_reduction` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.1725 | 0.7122 |
| `validate_atk_square` | `yolo` | `square` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.3991 | 0.7013 |
| `validate_baseline` | `yolo` | `none` | `` | `` | `none` | `attack_then_defense` | `complete` | 0.5765 | 0.7498 |
| `validate_deepfool_bit_depth` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `attack_then_defense` | `complete` | 0.0359 |  |
| `validate_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.0304 |  |
| `validate_deepfool_median_preprocess` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `attack_then_defense` | `complete` | 0.0248 |  |
| `validate_dispersion_reduction_bit_depth` | `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `attack_then_defense` | `complete` | 0.1858 | 0.6898 |
| `validate_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.1679 | 0.6891 |
| `validate_dispersion_reduction_median_preprocess` | `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `attack_then_defense` | `complete` | 0.2892 | 0.6940 |
| `validate_square_bit_depth` | `yolo` | `square` | `` | `` | `bit_depth` | `attack_then_defense` | `complete` | 0.4013 | 0.6981 |
| `validate_square_jpeg_preprocess` | `yolo` | `square` | `` | `` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.3109 | 0.6939 |
| `validate_square_median_preprocess` | `yolo` | `square` | `` | `` | `median_preprocess` | `attack_then_defense` | `complete` | 0.3280 | 0.6603 |

## Attack Effectiveness

| Model | Seed | Attack | Artifact | Placement | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` | 0.5765 | 0.0363 | 0.5402 | 93.7% |
| `yolo` | 42 | `dispersion_reduction` | `` | `` | `` |  | `` | 0.5765 | 0.1725 | 0.4040 | 70.1% |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` | 0.5765 | 0.3991 | 0.1774 | 30.8% |

## Defense Recovery

| Model | Attack | Artifact | Placement | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `deepfool` | `` | `` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `` | `` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `` | `` | `bit_depth` | `untargeted_conf_suppression` |  | `` | 0.0363 | 0.0359 | -0.1% |
| `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` | 0.0363 | 0.0304 | -1.1% |
| `yolo` | `deepfool` | `` | `` | `median_preprocess` | `untargeted_conf_suppression` |  | `` | 0.0363 | 0.0248 | -2.1% |
| `yolo` | `dispersion_reduction` | `` | `` | `bit_depth` | `` |  | `` | 0.1725 | 0.1858 | 3.3% |
| `yolo` | `dispersion_reduction` | `` | `` | `jpeg_preprocess` | `` |  | `` | 0.1725 | 0.1679 | -1.1% |
| `yolo` | `dispersion_reduction` | `` | `` | `median_preprocess` | `` |  | `` | 0.1725 | 0.2892 | 28.9% |
| `yolo` | `square` | `` | `` | `bit_depth` | `` |  | `` | 0.3991 | 0.4013 | 1.3% |
| `yolo` | `square` | `` | `` | `jpeg_preprocess` | `` |  | `` | 0.3991 | 0.3109 | -49.8% |
| `yolo` | `square` | `` | `` | `median_preprocess` | `` |  | `` | 0.3991 | 0.3280 | -40.1% |

## Imported Patch Recovery

No imported patch comparisons found.

## Per-Class Detection Drop

| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |
|---|---:|---|---:|---|---:|---:|---:|
| `yolo` | 42 | `blur` | 0 | person | 50 | 41 | 18.0% |
| `yolo` | 42 | `blur` | 2 | car | 6 | 5 | 16.7% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 3 | 25.0% |
| `yolo` | 42 | `blur` | 41 | cup | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 43 | knife | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 0 | 1 |  |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 47 | apple | 3 | 3 | 0.0% |
| `yolo` | 42 | `blur` | 48 | sandwich | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 3 | 3 | 0.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 63 | laptop | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 21 | 58.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 6 | train | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 25 | umbrella | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 32 | 36.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 2 | -100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 2 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 61 | toilet | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 50 | 24 | 52.0% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `eot_pgd` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 0 | person | 50 | 49 | 2.0% |
| `yolo` | 42 | `fgsm` | 2 | car | 6 | 4 | 33.3% |
| `yolo` | 42 | `fgsm` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 7 | truck | 0 | 1 |  |
| `yolo` | 42 | `fgsm` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `fgsm` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `fgsm` | 41 | cup | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 43 | knife | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 47 | apple | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 55 | cake | 0 | 1 |  |
| `yolo` | 42 | `fgsm` | 56 | chair | 3 | 4 | -33.3% |
| `yolo` | 42 | `fgsm` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 60 | dining table | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 63 | laptop | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 66 | keyboard | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 0 | person | 50 | 50 | 0.0% |
| `yolo` | 42 | `pgd` | 2 | car | 6 | 2 | 66.7% |
| `yolo` | 42 | `pgd` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 7 | truck | 0 | 1 |  |
| `yolo` | 42 | `pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 22 | zebra | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 30 | skis | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 38 | tennis racket | 3 | 2 | 33.3% |
| `yolo` | 42 | `pgd` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `pgd` | 41 | cup | 3 | 1 | 66.7% |
| `yolo` | 42 | `pgd` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 44 | spoon | 0 | 1 |  |
| `yolo` | 42 | `pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 47 | apple | 3 | 3 | 0.0% |
| `yolo` | 42 | `pgd` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 56 | chair | 3 | 4 | -33.3% |
| `yolo` | 42 | `pgd` | 57 | couch | 0 | 1 |  |
| `yolo` | 42 | `pgd` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `pgd` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 60 | dining table | 3 | 1 | 66.7% |
| `yolo` | 42 | `pgd` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `pgd` | 63 | laptop | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 66 | keyboard | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 75 | vase | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 47 | 6.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 4 | 33.3% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 0 | 1 |  |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 54 | donut | 0 | 1 |  |
| `yolo` | 42 | `square` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 72 | -44.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 4 | 33.3% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 0 | 1 |  |
| `yolo` | 42 | `square` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 36 | skateboard | 0 | 1 |  |
| `yolo` | 42 | `square` | 37 | surfboard | 0 | 1 |  |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 50 | broccoli | 0 | 5 |  |
| `yolo` | 42 | `square` | 54 | donut | 0 | 1 |  |
| `yolo` | 42 | `square` | 56 | chair | 3 | 4 | -33.3% |
| `yolo` | 42 | `square` | 57 | couch | 0 | 1 |  |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 4 | -33.3% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 4 | -33.3% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 71 | sink | 0 | 1 |  |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 2 | 96.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 25 | umbrella | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 25 | 50.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 2 | 33.3% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 19 | 62.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 10 | 80.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 57 | couch | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 10 | 80.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 2 | 96.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 50 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 15 | 70.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 21 | 58.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 3 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 3 | -50.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 19 | 62.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 19 | 62.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 20 | 60.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 16 | 68.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 50 | 5 | 90.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 3 | 94.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 2 | 96.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 1 | 98.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 1 | 98.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 3 | 94.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 4 | 92.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 2 | 96.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 5 | -66.7% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 50 | 2 | 96.0% |
| `yolo` | 42 | `square` | 2 | car | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 39 | bottle | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 606 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 1 | bicycle | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 74 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 3 | motorcycle | 26 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 18 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 6 | train | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 7 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 8 | boat | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 9 | traffic light | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 10 | fire hydrant | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 13 | bench | 7 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 16 | dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 17 | horse | 23 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 18 | sheep | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 19 | cow | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 20 | elephant | 15 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 26 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 23 | giraffe | 10 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 24 | backpack | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 25 | umbrella | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 17 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 29 | frisbee | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 7 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 33 | kite | 14 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 7 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 36 | skateboard | 11 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 37 | surfboard | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 17 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 28 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 15 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 40 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 42 | fork | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 44 | spoon | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 24 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 17 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 8 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 49 | orange | 18 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 50 | broccoli | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 51 | carrot | 8 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 52 | hot dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 53 | pizza | 17 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 54 | donut | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 64 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 57 | couch | 15 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 16 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 15 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 25 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 61 | toilet | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 22 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 24 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 65 | remote | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 14 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 19 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 71 | sink | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 73 | book | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 12 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 10 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 606 | 10 | 98.3% |
| `yolo` | 42 | `dispersion_reduction` | 1 | bicycle | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 74 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 3 | motorcycle | 26 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 9 | 2 | 77.8% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 18 | 1 | 94.4% |
| `yolo` | 42 | `dispersion_reduction` | 6 | train | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 8 | boat | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 9 | traffic light | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 10 | fire hydrant | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 13 | bench | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 13 | 1 | 92.3% |
| `yolo` | 42 | `dispersion_reduction` | 16 | dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 17 | horse | 23 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 18 | sheep | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 19 | cow | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 20 | elephant | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 26 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 23 | giraffe | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 24 | backpack | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 25 | umbrella | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 17 | 1 | 94.1% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 29 | frisbee | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 7 | 1 | 85.7% |
| `yolo` | 42 | `dispersion_reduction` | 32 | sports ball | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 33 | kite | 14 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 36 | skateboard | 11 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 37 | surfboard | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 17 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 28 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 40 | 1 | 97.5% |
| `yolo` | 42 | `dispersion_reduction` | 42 | fork | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 44 | spoon | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 24 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 17 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 8 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 49 | orange | 18 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 50 | broccoli | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 51 | carrot | 8 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 52 | hot dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 53 | pizza | 17 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 54 | donut | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 64 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 57 | couch | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 16 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 25 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 61 | toilet | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 22 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 24 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 65 | remote | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 14 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 19 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 71 | sink | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 73 | book | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 606 | 54 | 91.1% |
| `yolo` | 42 | `square` | 1 | bicycle | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 2 | car | 74 | 3 | 95.9% |
| `yolo` | 42 | `square` | 3 | motorcycle | 26 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 9 | 1 | 88.9% |
| `yolo` | 42 | `square` | 5 | bus | 18 | 3 | 83.3% |
| `yolo` | 42 | `square` | 6 | train | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 7 | 1 | 85.7% |
| `yolo` | 42 | `square` | 8 | boat | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 9 | traffic light | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 10 | fire hydrant | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 13 | bench | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 14 | bird | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 16 | dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 17 | horse | 23 | 0 | 100.0% |
| `yolo` | 42 | `square` | 18 | sheep | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 19 | cow | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 20 | elephant | 15 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 4 | 1 | 75.0% |
| `yolo` | 42 | `square` | 22 | zebra | 26 | 0 | 100.0% |
| `yolo` | 42 | `square` | 23 | giraffe | 10 | 0 | 100.0% |
| `yolo` | 42 | `square` | 24 | backpack | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 25 | umbrella | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 17 | 2 | 88.2% |
| `yolo` | 42 | `square` | 28 | suitcase | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 29 | frisbee | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 7 | 1 | 85.7% |
| `yolo` | 42 | `square` | 31 | snowboard | 0 | 1 |  |
| `yolo` | 42 | `square` | 32 | sports ball | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 33 | kite | 14 | 7 | 50.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 36 | skateboard | 11 | 1 | 90.9% |
| `yolo` | 42 | `square` | 37 | surfboard | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 17 | 1 | 94.1% |
| `yolo` | 42 | `square` | 39 | bottle | 28 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 15 | 3 | 80.0% |
| `yolo` | 42 | `square` | 41 | cup | 40 | 2 | 95.0% |
| `yolo` | 42 | `square` | 42 | fork | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 44 | spoon | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 24 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 17 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 49 | orange | 18 | 0 | 100.0% |
| `yolo` | 42 | `square` | 50 | broccoli | 13 | 1 | 92.3% |
| `yolo` | 42 | `square` | 51 | carrot | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 52 | hot dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 53 | pizza | 17 | 0 | 100.0% |
| `yolo` | 42 | `square` | 54 | donut | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 56 | chair | 64 | 1 | 98.4% |
| `yolo` | 42 | `square` | 57 | couch | 15 | 1 | 93.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 16 | 1 | 93.8% |
| `yolo` | 42 | `square` | 59 | bed | 15 | 2 | 86.7% |
| `yolo` | 42 | `square` | 60 | dining table | 25 | 2 | 92.0% |
| `yolo` | 42 | `square` | 61 | toilet | 12 | 1 | 91.7% |
| `yolo` | 42 | `square` | 62 | tv | 22 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 24 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 65 | remote | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 14 | 0 | 100.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 19 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 71 | sink | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 73 | book | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 10 | 1 | 90.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 7 | 0 | 100.0% |