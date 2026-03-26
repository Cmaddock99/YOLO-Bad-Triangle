# Team Summary

- Total discovered runs: **7**
- Attack runs analyzed: **6**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (78.0%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `attack_deepfool` | `deepfool` | 78.0% | 0.7268 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_blur` | `blur` | 27.0% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_eot_pgd` | `eot_pgd` | 21.0% | 0.7785 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 19.0% | 0.7763 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 11.0% | 0.7463 | n/a | proxy (avg_conf) | Moderate robustness |
| `attack_square` | `square` | 9.0% | 0.7433 | n/a | proxy (avg_conf) | Moderate robustness |