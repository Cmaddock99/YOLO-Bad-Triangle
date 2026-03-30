# Framework Run Comparison Report

Total discovered framework runs: **68**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7566 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7271 |
| `attack_dispersion_reduction` | `yolo` | `dispersion_reduction` | `none` | `missing` |  | 0.7951 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7928 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7764 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7503 |
| `attack_square` | `yolo` | `square` | `none` | `missing` |  | 0.7183 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7623 |
| `consistency_atk_square` | `yolo` | `square` | `none` | `missing` |  | 0.7544 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7219 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7710 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.7870 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `missing` |  | 0.7746 |
| `defended_dispersion_reduction_bit_depth` | `yolo` | `dispersion_reduction` | `bit_depth` | `missing` |  | 0.7595 |
| `defended_dispersion_reduction_c_dog` | `yolo` | `dispersion_reduction` | `c_dog` | `missing` |  | 0.7444 |
| `defended_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `missing` |  | 0.7423 |
| `defended_dispersion_reduction_median_preprocess` | `yolo` | `dispersion_reduction` | `median_preprocess` | `missing` |  | 0.7469 |
| `defended_square_bit_depth` | `yolo` | `square` | `bit_depth` | `missing` |  | 0.7400 |
| `defended_square_c_dog` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7468 |
| `defended_square_jpeg_preprocess` | `yolo` | `square` | `jpeg_preprocess` | `missing` |  | 0.7403 |
| `defended_square_median_preprocess` | `yolo` | `square` | `median_preprocess` | `missing` |  | 0.7397 |
| `tune_atk_deepfool__epsilon0.05__steps50` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7463 |
| `tune_atk_deepfool__epsilon0.1__steps20` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7574 |
| `tune_atk_deepfool__epsilon0.1__steps50` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7354 |
| `tune_atk_deepfool__epsilon0.1__steps80` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7323 |
| `tune_atk_deepfool__epsilon0.2__steps50` | `yolo` | `deepfool` | `none` | `missing` |  | 0.8045 |
| `tune_atk_deepfool_best` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7354 |
| `tune_atk_dispersion_reduction__epsilon0.075__steps20` | `yolo` | `dispersion_reduction` | `none` | `missing` |  | 0.7634 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps20` | `yolo` | `dispersion_reduction` | `none` | `missing` |  | 0.7351 |
| `tune_atk_dispersion_reduction__epsilon0.15__steps40` | `yolo` | `dispersion_reduction` | `none` | `missing` |  | 0.7697 |
| `tune_atk_square__eps0.15__n_queries450` | `yolo` | `square` | `none` | `missing` |  | 0.7627 |
| `tune_atk_square__eps0.3__n_queries400` | `yolo` | `square` | `none` | `missing` |  | 0.7400 |
| `tune_atk_square__eps0.3__n_queries450` | `yolo` | `square` | `none` | `missing` |  | 0.7082 |
| `tune_atk_square__eps0.3__n_queries500` | `yolo` | `square` | `none` | `missing` |  | 0.7832 |
| `tune_atk_square_best` | `yolo` | `square` | `none` | `missing` |  | 0.7082 |
| `tune_def_bit_depth__bits5_vs_deepfool` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7299 |
| `tune_def_bit_depth__bits5_vs_square` | `yolo` | `square` | `bit_depth` | `missing` |  | 0.7302 |
| `tune_def_bit_depth__bits6_vs_deepfool` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.8157 |
| `tune_def_bit_depth__bits6_vs_square` | `yolo` | `square` | `bit_depth` | `missing` |  | 0.7409 |
| `tune_def_bit_depth__bits7_vs_deepfool` | `yolo` | `deepfool` | `bit_depth` | `missing` |  | 0.7530 |
| `tune_def_bit_depth__bits7_vs_square` | `yolo` | `square` | `bit_depth` | `missing` |  | 0.7285 |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7838 |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7232 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7674 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_square` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7634 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7999 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7566 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7750 |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_square` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7313 |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_deepfool` | `yolo` | `deepfool` | `c_dog` | `missing` |  | 0.7617 |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_square` | `yolo` | `square` | `c_dog` | `missing` |  | 0.7324 |
| `tune_def_jpeg_preprocess__quality45_vs_deepfool` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.7818 |
| `tune_def_jpeg_preprocess__quality45_vs_square` | `yolo` | `square` | `jpeg_preprocess` | `missing` |  | 0.7846 |
| `tune_def_jpeg_preprocess__quality60_vs_deepfool` | `yolo` | `deepfool` | `jpeg_preprocess` | `missing` |  | 0.7670 |
| `tune_def_jpeg_preprocess__quality60_vs_square` | `yolo` | `square` | `jpeg_preprocess` | `missing` |  | 0.7489 |
| `validate_atk_deepfool` | `yolo` | `deepfool` | `none` | `complete` | 0.2184 | 0.7562 |
| `validate_atk_dispersion_reduction` | `yolo` | `dispersion_reduction` | `none` | `complete` | 0.2381 | 0.6761 |
| `validate_atk_square` | `yolo` | `square` | `none` | `complete` | 0.3630 | 0.7195 |
| `validate_baseline` | `yolo` | `none` | `none` | `complete` | 0.6002 | 0.7648 |
| `validate_deepfool_bit_depth` | `yolo` | `deepfool` | `bit_depth` | `complete` | 0.2229 | 0.7465 |
| `validate_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `complete` | 0.2403 | 0.7533 |
| `validate_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `jpeg_preprocess` | `complete` | 0.1663 | 0.7613 |
| `validate_dispersion_reduction_bit_depth` | `yolo` | `dispersion_reduction` | `bit_depth` | `complete` | 0.2319 | 0.7128 |
| `validate_dispersion_reduction_c_dog` | `yolo` | `dispersion_reduction` | `c_dog` | `complete` | 0.2632 | 0.7244 |
| `validate_dispersion_reduction_jpeg_preprocess` | `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `complete` | 0.2015 | 0.6834 |
| `validate_square_bit_depth` | `yolo` | `square` | `bit_depth` | `complete` | 0.3863 | 0.7466 |
| `validate_square_c_dog` | `yolo` | `square` | `c_dog` | `complete` | 0.3890 | 0.7274 |
| `validate_square_jpeg_preprocess` | `yolo` | `square` | `jpeg_preprocess` | `complete` | 0.3767 | 0.7404 |

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
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  | 0.2184 |  |  |
| `yolo` | 42 | `dispersion_reduction` | `` |  | `` |  | 0.2381 |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  | 0.3630 |  |  |

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
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `bit_depth` | `` |  | `` |  |  |  |
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  |  |  |
| `yolo` | `square` | `bit_depth` | `` |  | `` |  |  |  |
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
| `yolo` | `deepfool` | `bit_depth` | `untargeted_conf_suppression` |  | `` |  | 0.2229 |  |
| `yolo` | `deepfool` | `c_dog` | `untargeted_conf_suppression` |  | `` |  | 0.2403 |  |
| `yolo` | `deepfool` | `jpeg_preprocess` | `untargeted_conf_suppression` |  | `` |  | 0.1663 |  |
| `yolo` | `dispersion_reduction` | `bit_depth` | `` |  | `` |  | 0.2319 |  |
| `yolo` | `dispersion_reduction` | `c_dog` | `` |  | `` |  | 0.2632 |  |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | `` |  | `` |  | 0.2015 |  |
| `yolo` | `square` | `bit_depth` | `` |  | `` |  | 0.3863 |  |
| `yolo` | `square` | `c_dog` | `` |  | `` |  | 0.3890 |  |
| `yolo` | `square` | `jpeg_preprocess` | `` |  | `` |  | 0.3767 |  |

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
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 122 | -183.7% |
| `yolo` | 42 | `deepfool` | 1 | bicycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 3 | 0.0% |
| `yolo` | 42 | `deepfool` | 3 | motorcycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 4 | -100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 5 | -25.0% |
| `yolo` | 42 | `deepfool` | 6 | train | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 9 | traffic light | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 10 | fire hydrant | 0 | 6 |  |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 5 | -400.0% |
| `yolo` | 42 | `deepfool` | 16 | dog | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 17 | horse | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 18 | sheep | 0 | 5 |  |
| `yolo` | 42 | `deepfool` | 19 | cow | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 20 | elephant | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 4 | -300.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 14 | -1300.0% |
| `yolo` | 42 | `deepfool` | 23 | giraffe | 0 | 7 |  |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 29 | frisbee | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 33 | kite | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 36 | skateboard | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 37 | surfboard | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 7 | -250.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 50 | broccoli | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 51 | carrot | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 53 | pizza | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 57 | couch | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 4 | -100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 61 | toilet | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 65 | remote | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 0 | person | 43 | 23 | 46.5% |
| `yolo` | 42 | `dispersion_reduction` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 5 | bus | 4 | 2 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 15 | cat | 1 | 3 | -200.0% |
| `yolo` | 42 | `dispersion_reduction` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 27 | tie | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 41 | cup | 2 | 1 | 50.0% |
| `yolo` | 42 | `dispersion_reduction` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 50 | broccoli | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 55 | cake | 1 | 1 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 60 | dining table | 2 | 2 | 0.0% |
| `yolo` | 42 | `dispersion_reduction` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `dispersion_reduction` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `dispersion_reduction` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 56 | -30.2% |
| `yolo` | 42 | `square` | 2 | car | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 5 | -25.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 27 | tie | 0 | 2 |  |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 31 | snowboard | 0 | 1 |  |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 36 | skateboard | 0 | 2 |  |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 50 | broccoli | 0 | 2 |  |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `square` | 57 | couch | 0 | 2 |  |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `square` | 61 | toilet | 0 | 1 |  |
| `yolo` | 42 | `square` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |