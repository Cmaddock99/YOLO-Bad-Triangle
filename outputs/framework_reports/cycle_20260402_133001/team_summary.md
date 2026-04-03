# Team Summary

- Total discovered runs: **20**
- Attack runs analyzed: **19**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (83.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `defended_deepfool_c_dog` | `deepfool` | 83.0% | 0.7788 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_square` | `square` | 82.0% | 0.7183 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 77.0% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_dispersion_reduction` | `dispersion_reduction` | 76.0% | 0.7951 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_bit_depth` | `deepfool` | 76.0% | 0.7392 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 64.0% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_jpeg_preprocess` | `deepfool` | 64.0% | 0.7575 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_deepfool_median_preprocess` | `deepfool` | 59.0% | 0.7457 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_c_dog` | `dispersion_reduction` | 54.0% | 0.7473 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_bit_depth` | `dispersion_reduction` | 50.0% | 0.7511 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_jpeg_preprocess` | `dispersion_reduction` | 47.0% | 0.7525 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_dispersion_reduction_median_preprocess` | `dispersion_reduction` | 40.0% | 0.7515 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_median_preprocess` | `square` | 25.0% | 0.7371 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_jpeg_preprocess` | `square` | 14.0% | 0.7460 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 8.0% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |
| `defended_square_bit_depth` | `square` | 8.0% | 0.7374 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_c_dog` | `square` | 8.0% | 0.7276 | n/a | proxy (avg_conf) | Strong attack effect |