# Team Summary

- Total discovered runs: **23**
- Attack runs analyzed: **22**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (85.7%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `defended_deepfool_c_dog_ensemble` | `deepfool` | 85.7% | 0.8318 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_c_dog` | `deepfool` | 76.2% | 0.7528 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 76.2% | 0.8412 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 71.4% | 0.7835 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_c_dog_ensemble` | `eot_pgd` | 71.4% | 0.7942 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 61.9% | 0.7955 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 57.1% | 0.7549 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_median_preprocess` | `eot_pgd` | 52.4% | 0.8200 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_bit_depth` | `eot_pgd` | 47.6% | 0.8552 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_eot_pgd_c_dog` | `eot_pgd` | 47.6% | 0.7324 | n/a | proxy (avg_conf) | Strong attack effect |
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