# Team Summary

- Total discovered runs: **68**
- Attack runs analyzed: **66**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `square` (91.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `tune_atk_square__eps0.3__n_queries500` | `square` | 91.0% | 0.7832 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.2__steps50` | `deepfool` | 90.0% | 0.8045 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_deepfool` | `deepfool` | 90.0% | 0.8450 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps20` | `deepfool` | 89.0% | 0.7574 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_deepfool` | `deepfool` | 89.0% | 0.8280 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps50` | `deepfool` | 88.0% | 0.7354 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps80` | `deepfool` | 88.0% | 0.7323 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_best` | `deepfool` | 88.0% | 0.7354 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.15__steps20` | `dispersion_reduction` | 88.0% | 0.7351 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.15__steps40` | `dispersion_reduction` | 88.0% | 0.7697 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.3__n_queries450` | `square` | 88.0% | 0.7082 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square_best` | `square` | 88.0% | 0.7082 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_deepfool` | `deepfool` | 88.0% | 0.8106 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_deepfool` | `deepfool` | 88.0% | 0.7938 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_deepfool` | `deepfool` | 88.0% | 0.8067 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size5_vs_square` | `square` | 88.0% | 0.7438 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size7_vs_square` | `square` | 88.0% | 0.7070 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.3__n_queries400` | `square` | 87.0% | 0.7400 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality40_vs_square` | `square` | 87.0% | 0.7867 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size3_vs_square` | `square` | 87.0% | 0.7464 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.05__steps50` | `deepfool` | 86.0% | 0.7463 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality55_vs_square` | `square` | 85.0% | 0.7643 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.15__n_queries450` | `square` | 84.0% | 0.7627 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_square` | `square` | 84.0% | 0.7379 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_square` | `square` | 83.0% | 0.7403 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_square` | `square` | 83.0% | 0.7388 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_square` | `square` | 83.0% | 0.7356 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_square` | `square` | 82.0% | 0.7183 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_square` | `square` | 82.0% | 0.7157 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 77.0% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_c_dog` | `deepfool` | 77.0% | 0.7401 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size3_vs_deepfool` | `deepfool` | 77.0% | 0.7483 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_dispersion_reduction` | `dispersion_reduction` | 76.0% | 0.7951 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 76.0% | 0.7392 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.075__steps20` | `dispersion_reduction` | 76.0% | 0.7634 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality40_vs_deepfool` | `deepfool` | 76.0% | 0.7668 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality55_vs_deepfool` | `deepfool` | 74.0% | 0.7322 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size5_vs_deepfool` | `deepfool` | 72.0% | 0.7535 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 64.0% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 64.0% | 0.7575 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess__kernel_size7_vs_deepfool` | `deepfool` | 64.0% | 0.7240 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_c_dog` | `dispersion_reduction` | 61.0% | 0.6956 | 0.2306 | ✓ mAP50 | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 59.0% | 0.7457 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_atk_dispersion_reduction` | `dispersion_reduction` | 58.0% | 0.6761 | 0.2381 | ✓ mAP50 | Strong attack effect |
| `defended_dispersion_reduction_c_dog` | `dispersion_reduction` | 53.0% | 0.7584 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 53.0% | 0.6940 | 0.2040 | ✓ mAP50 | Strong attack effect |
| `defended_dispersion_reduction_bit_depth` | `dispersion_reduction` | 50.0% | 0.7511 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_square_median_preprocess` | `square` | 48.0% | 0.7055 | 0.2768 | ✓ mAP50 | Strong attack effect |
| `defended_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 47.0% | 0.7525 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_median_preprocess` | `dispersion_reduction` | 43.0% | 0.7270 | 0.3082 | ✓ mAP50 | Strong attack effect |
| `defended_dispersion_reduction_median_preprocess` | `dispersion_reduction` | 40.0% | 0.7515 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_square_jpeg_preprocess` | `square` | 28.0% | 0.7320 | 0.3247 | ✓ mAP50 | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_median_preprocess` | `square` | 25.0% | 0.7371 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_jpeg_preprocess` | `square` | 14.0% | 0.7460 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_square_c_dog` | `square` | 12.0% | 0.7270 | 0.3503 | ✓ mAP50 | Strong attack effect |
| `defended_square_c_dog` | `square` | 10.0% | 0.7389 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 8.0% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |
| `defended_square_bit_depth` | `square` | 8.0% | 0.7374 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_atk_square` | `square` | 5.0% | 0.7195 | 0.3630 | ✓ mAP50 | Strong attack effect |
| `consistency_atk_square` | `square` | -39.0% | 0.7544 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_atk_deepfool` | `deepfool` | -160.0% | 0.7562 | 0.2184 | ✓ mAP50 | Strong attack effect |
| `validate_deepfool_c_dog` | `deepfool` | -179.0% | 0.7584 | 0.2238 | ✓ mAP50 | Strong attack effect |
| `validate_deepfool_jpeg_preprocess` | `deepfool` | -417.0% | 0.7632 | 0.3175 | ✓ mAP50 | Strong attack effect |
| `validate_deepfool_median_preprocess` | `deepfool` | -530.0% | 0.7672 | 0.3656 | ✓ mAP50 | Strong attack effect |