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
| `tune_def_jpeg_preprocess__quality45_vs_deepfool` | `deepfool` | 91.0% | 0.7818 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.2__steps50` | `deepfool` | 90.0% | 0.8045 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits6_vs_deepfool` | `deepfool` | 90.0% | 0.8157 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps20` | `deepfool` | 89.0% | 0.7574 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality60_vs_deepfool` | `deepfool` | 89.0% | 0.7670 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps50` | `deepfool` | 88.0% | 0.7354 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.1__steps80` | `deepfool` | 88.0% | 0.7323 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_best` | `deepfool` | 88.0% | 0.7354 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.15__steps20` | `dispersion_reduction` | 88.0% | 0.7351 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.15__steps40` | `dispersion_reduction` | 88.0% | 0.7697 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.3__n_queries450` | `square` | 88.0% | 0.7082 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square_best` | `square` | 88.0% | 0.7082 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits7_vs_deepfool` | `deepfool` | 88.0% | 0.7530 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_deepfool` | `deepfool` | 88.0% | 0.7750 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.3__n_queries400` | `square` | 87.0% | 0.7400 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_deepfool` | `deepfool` | 87.0% | 0.7674 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool__epsilon0.05__steps50` | `deepfool` | 86.0% | 0.7463 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_deepfool` | `deepfool` | 86.0% | 0.7999 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep25_vs_square` | `square` | 85.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_deepfool` | `deepfool` | 85.0% | 0.7617 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality45_vs_square` | `square` | 85.0% | 0.7846 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess__quality60_vs_square` | `square` | 85.0% | 0.7489 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 84.0% | 0.7746 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_square__eps0.15__n_queries450` | `square` | 84.0% | 0.7627 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits5_vs_deepfool` | `deepfool` | 84.0% | 0.7299 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_deepfool` | `deepfool` | 84.0% | 0.7838 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep10_vs_square` | `square` | 84.0% | 0.7634 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 83.0% | 0.7870 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits6_vs_square` | `square` | 83.0% | 0.7409 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.35__timestep25_vs_square` | `square` | 83.0% | 0.7232 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.55__timestep40_vs_square` | `square` | 83.0% | 0.7313 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_c_dog__sharpen_alpha0.7__timestep25_vs_square` | `square` | 83.0% | 0.7324 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_square` | `square` | 82.0% | 0.7183 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits7_vs_square` | `square` | 82.0% | 0.7285 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth__bits5_vs_square` | `square` | 81.0% | 0.7302 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 77.0% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_dispersion_reduction` | `dispersion_reduction` | 76.0% | 0.7951 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_c_dog` | `deepfool` | 76.0% | 0.7710 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_dispersion_reduction__epsilon0.075__steps20` | `dispersion_reduction` | 76.0% | 0.7634 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 75.0% | 0.7219 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 66.0% | 0.6834 | 0.2015 | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_bit_depth` | `dispersion_reduction` | 65.0% | 0.7128 | 0.2319 | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 64.0% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_median_preprocess` | `dispersion_reduction` | 64.0% | 0.7469 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_atk_dispersion_reduction` | `dispersion_reduction` | 58.0% | 0.6761 | 0.2381 | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 56.0% | 0.7423 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_dispersion_reduction_c_dog` | `dispersion_reduction` | 53.0% | 0.7244 | 0.2632 | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_bit_depth` | `dispersion_reduction` | 52.0% | 0.7595 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_c_dog` | `dispersion_reduction` | 42.0% | 0.7444 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_square_jpeg_preprocess` | `square` | 30.0% | 0.7404 | 0.3767 | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_median_preprocess` | `square` | 19.0% | 0.7397 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_square_bit_depth` | `square` | 19.0% | 0.7466 | 0.3863 | proxy (avg_conf) | Strong attack effect |
| `defended_square_jpeg_preprocess` | `square` | 17.0% | 0.7403 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_c_dog` | `square` | 11.0% | 0.7468 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_bit_depth` | `square` | 9.0% | 0.7400 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 8.0% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |
| `validate_square_c_dog` | `square` | 7.0% | 0.7274 | 0.3890 | proxy (avg_conf) | Strong attack effect |
| `validate_atk_square` | `square` | 5.0% | 0.7195 | 0.3630 | proxy (avg_conf) | Strong attack effect |
| `consistency_atk_square` | `square` | -39.0% | 0.7544 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_deepfool_jpeg_preprocess` | `deepfool` | -74.0% | 0.7613 | 0.1663 | proxy (avg_conf) | Strong attack effect |
| `validate_deepfool_bit_depth` | `deepfool` | -155.0% | 0.7465 | 0.2229 | proxy (avg_conf) | Strong attack effect |
| `validate_atk_deepfool` | `deepfool` | -160.0% | 0.7562 | 0.2184 | proxy (avg_conf) | Strong attack effect |
| `validate_deepfool_c_dog` | `deepfool` | -177.0% | 0.7533 | 0.2403 | proxy (avg_conf) | Strong attack effect |