# Framework Run Comparison Report

Total discovered framework runs: **68**

## Run Inventory

| Run | Model | Attack | Defense | Semantics | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `attack_then_defense` | `missing` |  | 0.7566 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7271 |
| `attack_dispersion_reduction` | `yolo` | `dispersion_reduction` | `none` | `attack_then_defense` | `missing` |  | 0.7951 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `none` | `attack_then_defense` | `missing` |  | 0.7928 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `attack_then_defense` | `missing` |  | 0.7764 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `attack_then_defense` | `missing` |  | 0.7503 |
| `attack_square` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7183 |
| `baseline_none` | `yolo` | `none` | `none` | `attack_then_defense` | `missing` |  | 0.7623 |
| `consistency_atk_square` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7544 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7392 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7401 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7575 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7457 |
| `defended_dispersion_reduction_bit_depth` | `yolo` | `dispersion_reduction` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7511 |
| `defended_dispersion_reduction_c_dog` | `yolo` | `dispersion_reduction` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7584 |
| `defended_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7525 |
| `defended_dispersion_reduction_median_preprocess` | `yolo` | `dispersion_reduction` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7515 |
| `defended_square_bit_depth` | `yolo` | `square` | `bit_depth` | `attack_then_defense` | `missing` |  | 0.7374 |
| `defended_square_c_dog` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7389 |
| `defended_square_jpeg_preprocess` | `yolo` | `square` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7460 |
| `defended_square_median_preprocess` | `yolo` | `square` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7371 |
| `tune_atk_deepfool__epsilon0.05__steps50` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7463 |
| `tune_atk_deepfool__epsilon0.1__steps20` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7574 |
| `tune_atk_deepfool__epsilon0.1__steps50` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7354 |
| `tune_atk_deepfool__epsilon0.1__steps80` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7323 |
| `tune_atk_deepfool__epsilon0.2__steps50` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.8045 |
| `tune_atk_deepfool_best` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `missing` |  | 0.7354 |
| `tune_atk_dispersion_reduction__epsilon0.075__steps20` | `yolo` | `dispersion_reduction` | `none` | `attack_then_defense` | `missing` |  | 0.7634 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps20` | `yolo` | `dispersion_reduction` | `none` | `attack_then_defense` | `missing` |  | 0.7351 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps40` | `yolo` | `dispersion_reduction` | `none` | `attack_then_defense` | `missing` |  | 0.7697 |
| `tune_atk_square__eps0.15__n_queries450` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7627 |
| `tune_atk_square__eps0.3__n_queries400` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7400 |
| `tune_atk_square__eps0.3__n_queries450` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7082 |
| `tune_atk_square__eps0.3__n_queries500` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7832 |
| `tune_atk_square_best` | `yolo` | `square` | `none` | `attack_then_defense` | `missing` |  | 0.7082 |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.8106 |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7157 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7938 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_square` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7403 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.8280 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7388 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.8067 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_square` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7356 |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `missing` |  | 0.8450 |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `missing` |  | 0.7379 |
| `tune_def_jpeg_preprocess__quality40_vs_deepfool` | `yolo` | `deepfool` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7668 |
| `tune_def_jpeg_preprocess__quality40_vs_square` | `yolo` | `square` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7867 |
| `tune_def_jpeg_preprocess__quality55_vs_deepfool` | `yolo` | `deepfool` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7322 |
| `tune_def_jpeg_preprocess__quality55_vs_square` | `yolo` | `square` | `jpeg_preprocess` | `attack_then_defense` | `missing` |  | 0.7643 |
| `tune_def_median_preprocess__kernel_size3_vs_deepfool` | `yolo` | `deepfool` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7483 |
| `tune_def_median_preprocess__kernel_size3_vs_square` | `yolo` | `square` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7464 |
| `tune_def_median_preprocess__kernel_size5_vs_deepfool` | `yolo` | `deepfool` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7535 |
| `tune_def_median_preprocess__kernel_size5_vs_square` | `yolo` | `square` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7438 |
| `tune_def_median_preprocess__kernel_size7_vs_deepfool` | `yolo` | `deepfool` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7240 |
| `tune_def_median_preprocess__kernel_size7_vs_square` | `yolo` | `square` | `median_preprocess` | `attack_then_defense` | `missing` |  | 0.7070 |
| `validate_atk_deepfool` | `yolo` | `deepfool` | `none` | `attack_then_defense` | `complete` | 0.2184 | 0.7562 |
| `validate_atk_dispersion_reduction` | `yolo` | `dispersion_reduction` | `none` | `attack_then_defense` | `complete` | 0.2381 | 0.6761 |
| `validate_atk_square` | `yolo` | `square` | `none` | `attack_then_defense` | `complete` | 0.3630 | 0.7195 |
| `validate_baseline` | `yolo` | `none` | `none` | `attack_then_defense` | `complete` | 0.6002 | 0.7648 |
| `validate_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `attack_then_defense` | `complete` | 0.2238 | 0.7584 |
| `validate_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.3175 | 0.7632 |
| `validate_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `attack_then_defense` | `complete` | 0.3656 | 0.7672 |
| `validate_dispersion_reduction_c_dog` | `yolo` | `dispersion_reduction` | `c_dog` | `attack_then_defense` | `complete` | 0.2306 | 0.6956 |
| `validate_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.2040 | 0.6940 |
| `validate_dispersion_reduction_median_preprocess` | `yolo` | `dispersion_reduction` | `median_preprocess` | `attack_then_defense` | `complete` | 0.3082 | 0.7270 |
| `validate_square_c_dog` | `yolo` | `square` | `c_dog` | `attack_then_defense` | `complete` | 0.3503 | 0.7270 |
| `validate_square_jpeg_preprocess` | `yolo` | `square` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.3247 | 0.7320 |
| `validate_square_median_preprocess` | `yolo` | `square` | `median_preprocess` | `attack_then_defense` | `complete` | 0.2768 | 0.7055 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` | 0.6002 | 0.2184 | 0.3817 | 63.6% |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` | 0.6002 | 0.2381 | 0.3621 | 60.3% |
| `yolo` | 42 | `square` | `` |  | `` | 0.6002 | 0.3630 | 0.2372 | 39.5% |

## Defense Recovery

| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `dispersion_reduction` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `square` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `square` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `jpeg_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `median_preprocess` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` | 0.2184 | 0.2238 | 1.4% |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` | 0.2184 | 0.3175 | 26.0% |
| `yolo` | `deepfool` | `median_preprocess` | `untargeted_conf_suppression` |  | `` | 0.2184 | 0.3656 | 38.5% |
| `yolo` | `dispersion_reduction` | `c_dog` | `` |  | `` | 0.2381 | 0.2306 | -2.0% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `` |  | `` | 0.2381 | 0.2040 | -9.4% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | `` |  | `` | 0.2381 | 0.3082 | 19.4% |
| `yolo` | `square` | `c_dog` | `` |  | `` | 0.3630 | 0.3503 | -5.4% |
| `yolo` | `square` | `jpeg_preprocess` | `` |  | `` | 0.3630 | 0.3247 | -16.2% |
| `yolo` | `square` | `median_preprocess` | `` |  | `` | 0.3630 | 0.2768 | -36.4% |

## Per-Class Detection Drop

| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |
|---|---:|---|---:|---|---:|---:|---:|
| `yolo` | 42 | `blur` | 0 | person | 43 | 31 | 27.9% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 10 | 76.7% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 43 | 16 | 62.8% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 23 | giraffe | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 19 | 55.8% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 67 | cell phone | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 0 | person | 43 | 37 | 14.0% |
| `yolo` | 42 | `fgsm` | 2 | car | 3 | 5 | -66.7% |
| `yolo` | 42 | `fgsm` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 30 | skis | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `fgsm` | 40 | wine glass | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 41 | cup | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 60 | dining table | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `fgsm` | 63 | laptop | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 0 | person | 43 | 43 | 0.0% |
| `yolo` | 42 | `pgd` | 2 | car | 3 | 3 | 0.0% |
| `yolo` | 42 | `pgd` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 22 | zebra | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 40 | wine glass | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 47 | apple | 2 | 4 | -100.0% |
| `yolo` | 42 | `pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 56 | chair | 4 | 4 | 0.0% |
| `yolo` | 42 | `pgd` | 58 | potted plant | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `pgd` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 4 | 90.7% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 71 | -65.1% |
| `yolo` | 42 | `square` | 2 | car | 3 | 4 | -33.3% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 27 | tie | 0 | 2 |  |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 37 | surfboard | 0 | 1 |  |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 5 | -150.0% |
| `yolo` | 42 | `square` | 43 | knife | 0 | 1 |  |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 2 | -100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 50 | broccoli | 0 | 3 |  |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 5 | -25.0% |
| `yolo` | 42 | `square` | 57 | couch | 0 | 2 |  |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 5 | -150.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 6 | 86.0% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 4 | 90.7% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 5 | 88.4% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 5 | 88.4% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 5 | 88.4% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 5 | 88.4% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 43 | 16 | 62.8% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 23 | giraffe | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 43 | 8 | 81.4% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 43 | 8 | 81.4% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 4 | 90.7% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 3 | 93.0% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 4 | 90.7% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `square` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 576 | 122 | 78.8% |
| `yolo` | 42 | `deepfool` | 1 | bicycle | 8 | 3 | 62.5% |
| `yolo` | 42 | `deepfool` | 2 | car | 46 | 3 | 93.5% |
| `yolo` | 42 | `deepfool` | 3 | motorcycle | 27 | 3 | 88.9% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 9 | 4 | 55.6% |
| `yolo` | 42 | `deepfool` | 5 | bus | 20 | 5 | 75.0% |
| `yolo` | 42 | `deepfool` | 6 | train | 9 | 4 | 55.6% |
| `yolo` | 42 | `deepfool` | 7 | truck | 6 | 1 | 83.3% |
| `yolo` | 42 | `deepfool` | 8 | boat | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 9 | traffic light | 5 | 1 | 80.0% |
| `yolo` | 42 | `deepfool` | 10 | fire hydrant | 7 | 6 | 14.3% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 3 | 3 | 0.0% |
| `yolo` | 42 | `deepfool` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 13 | bench | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 15 | 1 | 93.3% |
| `yolo` | 42 | `deepfool` | 15 | cat | 17 | 5 | 70.6% |
| `yolo` | 42 | `deepfool` | 16 | dog | 9 | 2 | 77.8% |
| `yolo` | 42 | `deepfool` | 17 | horse | 24 | 2 | 91.7% |
| `yolo` | 42 | `deepfool` | 18 | sheep | 17 | 5 | 70.6% |
| `yolo` | 42 | `deepfool` | 19 | cow | 6 | 1 | 83.3% |
| `yolo` | 42 | `deepfool` | 20 | elephant | 13 | 3 | 76.9% |
| `yolo` | 42 | `deepfool` | 21 | bear | 4 | 4 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 25 | 14 | 44.0% |
| `yolo` | 42 | `deepfool` | 23 | giraffe | 9 | 7 | 22.2% |
| `yolo` | 42 | `deepfool` | 24 | backpack | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 25 | umbrella | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 16 | 1 | 93.8% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 14 | 1 | 92.9% |
| `yolo` | 42 | `deepfool` | 29 | frisbee | 8 | 3 | 62.5% |
| `yolo` | 42 | `deepfool` | 30 | skis | 10 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 31 | snowboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 13 | 3 | 76.9% |
| `yolo` | 42 | `deepfool` | 33 | kite | 9 | 2 | 77.8% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 7 | 1 | 85.7% |
| `yolo` | 42 | `deepfool` | 36 | skateboard | 9 | 2 | 77.8% |
| `yolo` | 42 | `deepfool` | 37 | surfboard | 12 | 2 | 83.3% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 14 | 7 | 50.0% |
| `yolo` | 42 | `deepfool` | 39 | bottle | 18 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 15 | 1 | 93.3% |
| `yolo` | 42 | `deepfool` | 41 | cup | 45 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 42 | fork | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 43 | knife | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 44 | spoon | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 22 | 1 | 95.5% |
| `yolo` | 42 | `deepfool` | 46 | banana | 11 | 1 | 90.9% |
| `yolo` | 42 | `deepfool` | 47 | apple | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 48 | sandwich | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 49 | orange | 13 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 50 | broccoli | 11 | 2 | 81.8% |
| `yolo` | 42 | `deepfool` | 51 | carrot | 7 | 1 | 85.7% |
| `yolo` | 42 | `deepfool` | 52 | hot dog | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 53 | pizza | 15 | 4 | 73.3% |
| `yolo` | 42 | `deepfool` | 54 | donut | 10 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 5 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 54 | 2 | 96.3% |
| `yolo` | 42 | `deepfool` | 57 | couch | 12 | 4 | 66.7% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 13 | 4 | 69.2% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 27 | 3 | 88.9% |
| `yolo` | 42 | `deepfool` | 61 | toilet | 10 | 3 | 70.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 23 | 1 | 95.7% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 26 | 3 | 88.5% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 8 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 65 | remote | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 10 | 1 | 90.0% |
| `yolo` | 42 | `deepfool` | 67 | cell phone | 10 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 71 | sink | 6 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 12 | 3 | 75.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 8 | 2 | 75.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 6 | 2 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 576 | 23 | 96.0% |
| `yolo` | 42 | `dispersion_reduction` | 1 | bicycle | 8 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 46 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 3 | motorcycle | 27 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 9 | 2 | 77.8% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 20 | 2 | 90.0% |
| `yolo` | 42 | `dispersion_reduction` | 6 | train | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 8 | boat | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 9 | traffic light | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 10 | fire hydrant | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 3 | 1 | 66.7% |
| `yolo` | 42 | `dispersion_reduction` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 13 | bench | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 17 | 3 | 82.4% |
| `yolo` | 42 | `dispersion_reduction` | 16 | dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 17 | horse | 24 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 18 | sheep | 17 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 19 | cow | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 20 | elephant | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 25 | 1 | 96.0% |
| `yolo` | 42 | `dispersion_reduction` | 23 | giraffe | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 24 | backpack | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 25 | umbrella | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 16 | 1 | 93.8% |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 14 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 29 | frisbee | 8 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 31 | snowboard | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 32 | sports ball | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 33 | kite | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 36 | skateboard | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 37 | surfboard | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 14 | 1 | 92.9% |
| `yolo` | 42 | `dispersion_reduction` | 39 | bottle | 18 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 45 | 1 | 97.8% |
| `yolo` | 42 | `dispersion_reduction` | 42 | fork | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 43 | knife | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 44 | spoon | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 22 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 11 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 5 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 48 | sandwich | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 49 | orange | 13 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 50 | broccoli | 11 | 1 | 90.9% |
| `yolo` | 42 | `dispersion_reduction` | 51 | carrot | 7 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 52 | hot dog | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 53 | pizza | 15 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 54 | donut | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 5 | 1 | 80.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 54 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 57 | couch | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 13 | 2 | 84.6% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 27 | 2 | 92.6% |
| `yolo` | 42 | `dispersion_reduction` | 61 | toilet | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 23 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 26 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 8 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 65 | remote | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 67 | cell phone | 10 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 71 | sink | 6 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 12 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 8 | 1 | 87.5% |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 576 | 56 | 90.3% |
| `yolo` | 42 | `square` | 1 | bicycle | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 2 | car | 46 | 2 | 95.7% |
| `yolo` | 42 | `square` | 3 | motorcycle | 27 | 0 | 100.0% |
| `yolo` | 42 | `square` | 4 | airplane | 9 | 2 | 77.8% |
| `yolo` | 42 | `square` | 5 | bus | 20 | 5 | 75.0% |
| `yolo` | 42 | `square` | 6 | train | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 7 | truck | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 8 | boat | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 9 | traffic light | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 10 | fire hydrant | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 12 | parking meter | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 13 | bench | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 14 | bird | 15 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 17 | 0 | 100.0% |
| `yolo` | 42 | `square` | 16 | dog | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 17 | horse | 24 | 0 | 100.0% |
| `yolo` | 42 | `square` | 18 | sheep | 17 | 0 | 100.0% |
| `yolo` | 42 | `square` | 19 | cow | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 20 | elephant | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 4 | 1 | 75.0% |
| `yolo` | 42 | `square` | 22 | zebra | 25 | 0 | 100.0% |
| `yolo` | 42 | `square` | 23 | giraffe | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 24 | backpack | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 25 | umbrella | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 27 | tie | 16 | 2 | 87.5% |
| `yolo` | 42 | `square` | 28 | suitcase | 14 | 0 | 100.0% |
| `yolo` | 42 | `square` | 29 | frisbee | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 10 | 1 | 90.0% |
| `yolo` | 42 | `square` | 31 | snowboard | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 32 | sports ball | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 33 | kite | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 36 | skateboard | 9 | 2 | 77.8% |
| `yolo` | 42 | `square` | 37 | surfboard | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 14 | 1 | 92.9% |
| `yolo` | 42 | `square` | 39 | bottle | 18 | 0 | 100.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 15 | 2 | 86.7% |
| `yolo` | 42 | `square` | 41 | cup | 45 | 1 | 97.8% |
| `yolo` | 42 | `square` | 42 | fork | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 43 | knife | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 44 | spoon | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 45 | bowl | 22 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 11 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 48 | sandwich | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 49 | orange | 13 | 0 | 100.0% |
| `yolo` | 42 | `square` | 50 | broccoli | 11 | 2 | 81.8% |
| `yolo` | 42 | `square` | 51 | carrot | 7 | 0 | 100.0% |
| `yolo` | 42 | `square` | 52 | hot dog | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 53 | pizza | 15 | 0 | 100.0% |
| `yolo` | 42 | `square` | 54 | donut | 10 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 5 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 54 | 2 | 96.3% |
| `yolo` | 42 | `square` | 57 | couch | 12 | 2 | 83.3% |
| `yolo` | 42 | `square` | 58 | potted plant | 9 | 1 | 88.9% |
| `yolo` | 42 | `square` | 59 | bed | 13 | 2 | 84.6% |
| `yolo` | 42 | `square` | 60 | dining table | 27 | 3 | 88.9% |
| `yolo` | 42 | `square` | 61 | toilet | 10 | 1 | 90.0% |
| `yolo` | 42 | `square` | 62 | tv | 23 | 1 | 95.7% |
| `yolo` | 42 | `square` | 63 | laptop | 26 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 65 | remote | 4 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 10 | 1 | 90.0% |
| `yolo` | 42 | `square` | 67 | cell phone | 10 | 0 | 100.0% |
| `yolo` | 42 | `square` | 69 | oven | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 71 | sink | 6 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 9 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 12 | 0 | 100.0% |
| `yolo` | 42 | `square` | 75 | vase | 8 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 6 | 2 | 66.7% |