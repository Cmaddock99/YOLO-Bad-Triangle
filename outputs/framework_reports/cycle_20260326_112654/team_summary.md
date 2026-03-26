# Team Summary

- Total discovered runs: **19**
- Attack runs analyzed: **18**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (90.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `defended_deepfool_c_dog` | `deepfool` | 90.0% | 0.7609 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 87.0% | 0.7791 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 84.0% | 0.8256 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 78.0% | 0.7268 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 76.0% | 0.7235 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_median_preprocess` | `eot_pgd` | 40.0% | 0.7735 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_c_dog` | `blur` | 39.0% | 0.7475 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_c_dog` | `eot_pgd` | 36.0% | 0.7285 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_jpeg_preprocess` | `blur` | 29.0% | 0.7564 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_median_preprocess` | `blur` | 29.0% | 0.7510 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_blur_bit_depth` | `blur` | 27.0% | 0.7493 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_jpeg_preprocess` | `eot_pgd` | 26.0% | 0.7650 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_bit_depth` | `eot_pgd` | 25.0% | 0.7831 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 21.0% | 0.7785 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7763 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 11.0% | 0.7463 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_square` | `square` | 9.0% | 0.7433 | n/a | proxy (avg_conf) | Moderate robustness |