# Team Summary

- Total discovered runs: **10**
- Attack runs analyzed: **9**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `square` (82.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `attack_square` | `square` | 82.0% | 0.7183 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_deepfool` | `deepfool` | 77.0% | 0.7271 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_dispersion_reduction` | `dispersion_reduction` | 76.0% | 0.7951 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 64.0% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_c_dog` | `square` | 11.0% | 0.7468 | n/a | proxy (avg_conf) | Strong attack effect |
| `defended_square_bit_depth` | `square` | 9.0% | 0.7400 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 8.0% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |