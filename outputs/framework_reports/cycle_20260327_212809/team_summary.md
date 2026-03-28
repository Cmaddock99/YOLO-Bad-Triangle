# Team Summary

- Total discovered runs: **8**
- Attack runs analyzed: **7**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (57.1%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `attack_deepfool` | `deepfool` | 57.1% | 0.7549 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 33.3% | 0.7956 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 23.8% | 0.7272 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7521 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 14.3% | 0.7646 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_square` | `square` | 14.3% | 0.7183 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_jpeg_attack` | `jpeg_attack` | 0.0% | 0.7485 | n/a | proxy (avg_conf) | No effect detected (verify metric or params) |