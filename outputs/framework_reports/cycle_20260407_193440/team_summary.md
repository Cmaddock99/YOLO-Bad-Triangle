# Team Summary

- Total discovered runs: **114**
- Attack runs analyzed: **7**
- Baseline run: `validate_baseline`

## Headline

- Strongest attack (by detection drop): `eot_pgd` (97.5%)
- Interpretation: Strong attack effect

## Attack Ranking

| Run | Attack | Det drop | Avg conf | mAP50 | Source | Interpretation |
|---|---|---:|---:|---:|---|---|
| `attack_eot_pgd` | `eot_pgd` | 97.5% | 0.7928 | n/a | proxy (avg_conf) | Strong attack effect |
| `validate_atk_dispersion_reduction` | `dispersion_reduction` | 97.1% | 0.6761 | 0.2381 | ✓ mAP50 | Strong attack effect |
| `attack_blur` | `blur` | 94.9% | 0.7566 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_fgsm` | `fgsm` | 94.4% | 0.7764 | n/a | proxy (avg_conf) | Strong attack effect |
| `attack_pgd` | `pgd` | 93.6% | 0.7503 | n/a | proxy (avg_conf) | Moderate robustness |
| `validate_atk_square` | `square` | 93.4% | 0.7195 | 0.3630 | ✓ mAP50 | Strong attack effect |
| `validate_atk_deepfool` | `deepfool` | 81.4% | 0.7549 | 0.2422 | ✓ mAP50 | Strong attack effect |

## Provenance

- YOLO checkpoint: `9b09cc8bf347` (`/home/lurch/YOLO-Bad-Triangle/yolo26n.pt`)
- Defense checkpoint: none loaded
- Clean gate: PASS — candidate shows no clean accuracy regression; marginally better than previous on clean images (+0.0025 mAP50). (/home/lurch/YOLO-Bad-Triangle/outputs/eval_ab_clean.json)
- Generated: 2026-04-10T03:53:22.938858+00:00