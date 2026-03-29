# Team Summary

- Total discovered runs: **20**
- Attack runs analyzed: **19**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (84.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `defended_deepfool_median_preprocess` | `deepfool` | 84.0% | 0.7746 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 83.0% | 0.7870 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_square` | `square` | 82.0% | 0.7183 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 77.0% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_dispersion_reduction` | `dispersion_reduction` | 76.0% | 0.7951 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 75.0% | 0.7219 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_c_dog` | `deepfool` | 75.0% | 0.7440 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 64.0% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_median_preprocess` | `dispersion_reduction` | 64.0% | 0.7469 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 56.0% | 0.7423 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_bit_depth` | `dispersion_reduction` | 52.0% | 0.7595 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_c_dog` | `dispersion_reduction` | 50.0% | 0.7572 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_median_preprocess` | `square` | 19.0% | 0.7397 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_jpeg_preprocess` | `square` | 17.0% | 0.7403 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_c_dog` | `square` | 11.0% | 0.7463 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_bit_depth` | `square` | 9.0% | 0.7400 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 8.0% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |