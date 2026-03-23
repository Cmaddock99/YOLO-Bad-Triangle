# Team Summary

- Total discovered runs: **9**
- Attack runs analyzed: **8**
- Baseline run: `baseline_none`

## Headline

- Strongest attack (by detection drop): `deepfool` (57.1%)
- Interpretation: Strong attack effect

## Attack Ranking

| Attack | Detection drop | Avg confidence | Interpretation |
|---|---:|---:|---|
| `deepfool` | 57.1% | 0.7516 | Strong attack effect |
| `eot_pgd` | 38.1% | 0.8156 | Strong attack effect |
| `blur` | 23.8% | 0.7272 | Strong attack effect |
| `gaussian_blur` | 23.8% | 0.7272 | Strong attack effect |
| `fgsm` | 19.0% | 0.7522 | Strong attack effect |
| `fgsm_edge_mask` | 9.5% | 0.7596 | Moderate robustness |
| `fgsm_center_mask` | 4.8% | 0.7540 | Moderate robustness |
| `pgd` | -4.8% | 0.7374 | Moderate robustness |