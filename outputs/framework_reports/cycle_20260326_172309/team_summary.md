# Team Summary

- Total discovered runs: **54**
- Attack runs analyzed: **52**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (85.7%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `defended_deepfool_c_dog_ensemble` | `deepfool` | 85.7% | 0.8318 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess_001` | `deepfool` | 81.0% | 0.8709 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess_002` | `deepfool` | 81.0% | 0.8289 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_c_dog` | `deepfool` | 76.2% | 0.7528 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 76.2% | 0.8412 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_blur_002` | `blur` | 76.2% | 0.7626 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess_002` | `deepfool` | 76.2% | 0.8412 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 71.4% | 0.7835 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_c_dog_ensemble` | `eot_pgd` | 71.4% | 0.7942 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_blur_001` | `blur` | 71.4% | 0.7260 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_002` | `deepfool` | 71.4% | 0.8442 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_eot_pgd_003` | `eot_pgd` | 71.4% | 0.8673 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth_002` | `deepfool` | 71.4% | 0.8301 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_median_preprocess_003` | `deepfool` | 71.4% | 0.7835 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_001` | `deepfool` | 66.7% | 0.7701 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_004` | `deepfool` | 66.7% | 0.7730 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_best` | `deepfool` | 66.7% | 0.7701 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth_003` | `deepfool` | 66.7% | 0.7798 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess_003` | `deepfool` | 66.7% | 0.8051 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 61.9% | 0.7955 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_005` | `deepfool` | 61.9% | 0.7346 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_eot_pgd_001` | `eot_pgd` | 61.9% | 0.7955 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_eot_pgd_004` | `eot_pgd` | 61.9% | 0.7954 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_bit_depth_001` | `deepfool` | 61.9% | 0.7955 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_def_jpeg_preprocess_001` | `deepfool` | 61.9% | 0.7779 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 57.1% | 0.7549 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_deepfool_003` | `deepfool` | 57.1% | 0.7549 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_eot_pgd_002` | `eot_pgd` | 57.1% | 0.8046 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_median_preprocess` | `eot_pgd` | 52.4% | 0.8200 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_bit_depth` | `eot_pgd` | 47.6% | 0.8552 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_c_dog` | `eot_pgd` | 47.6% | 0.7324 | n/a | proxy (avg_conf) | Strong attack effect |
| `tune_atk_blur_003` | `blur` | 47.6% | 0.7239 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 33.3% | 0.7956 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_c_dog` | `blur` | 33.3% | 0.7215 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_c_dog_ensemble` | `blur` | 33.3% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_jpeg_preprocess` | `eot_pgd` | 33.3% | 0.7866 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 23.8% | 0.7272 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_median_preprocess` | `blur` | 23.8% | 0.7016 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7521 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_bit_depth` | `blur` | 19.0% | 0.6947 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_jpeg_preprocess` | `blur` | 19.0% | 0.7006 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 14.3% | 0.7646 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_square` | `square` | 14.3% | 0.7183 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_jpeg_attack` | `jpeg_attack` | 0.0% | 0.7485 | n/a | proxy (avg_conf) | No effect detected (verify metric or params) |
| `validate_deepfool_median_preprocess` | `deepfool` | -385.7% | 0.7560 | 0.1215 | proxy (avg_conf) | Strong attack effect |
| `validate_deepfool_jpeg_preprocess` | `deepfool` | -909.5% | 0.7518 | 0.1837 | proxy (avg_conf) | Strong attack effect |
| `validate_atk_deepfool` | `deepfool` | -1138.1% | 0.7562 | 0.2184 | proxy (avg_conf) | Strong attack effect |
| `validate_deepfool_bit_depth` | `deepfool` | -1147.6% | 0.7472 | 0.2276 | proxy (avg_conf) | Strong attack effect |
| `validate_blur_median_preprocess` | `blur` | -2304.8% | 0.7373 | 0.2492 | proxy (avg_conf) | Strong attack effect |
| `validate_blur_jpeg_preprocess` | `blur` | -2447.6% | 0.7301 | 0.2603 | proxy (avg_conf) | Strong attack effect |
| `validate_atk_blur` | `blur` | -2471.4% | 0.7346 | 0.2636 | proxy (avg_conf) | Strong attack effect |
| `validate_blur_bit_depth` | `blur` | -2481.0% | 0.7336 | 0.2615 | proxy (avg_conf) | Strong attack effect |