# Cycle Report

Generated from 7 completed cycle(s) in `outputs/cycle_history/`.

## Executive Summary

| Cycle | Date | Baseline mAP50 | Best defended mAP50 | Best config | Worst attack |
|---|---|---:|---:|---|---|
| 1 | 2026-03-23 | n/a | 0.5511 | pgd+confidence_filter | n/a |
| 2 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 3 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 4 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 5 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 6 | 2026-03-25 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 7 | 2026-03-26 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |

## Baseline mAP50 Trend

How the model's clean (unattacked) performance has changed across cycles.
Upward trend = model fortification is working.

| Cycle | Baseline mAP50 | Change vs prev |
|---|---:|---:|
| 1 | n/a | — |
| 2 | 0.6002 | — |
| 3 | 0.6002 | +0.0000 |
| 4 | 0.6002 | +0.0000 |
| 5 | 0.6002 | +0.0000 |
| 6 | 0.6002 | +0.0000 |
| 7 | 0.6002 | +0.0000 |

## Attack × Defense mAP50 Trends

Defended mAP50 for each attack+defense pair across cycles. Higher = better defense. Baseline mAP50 shown for reference.

### Attack: blur

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth | confidence_filter | jpeg_preprocess | median_preprocess | random_resize |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | 0.5260 | n/a | 0.4464 | n/a |
| 2 | 0.6002 | 0.3160 | n/a | 0.3160 | n/a | 0.2724 | n/a |
| 3 | 0.6002 | 0.3160 | n/a | 0.3160 | n/a | 0.2724 | n/a |
| 4 | 0.6002 | 0.3160 | n/a | 0.3160 | n/a | 0.2724 | n/a |
| 5 | 0.6002 | 0.3160 | n/a | 0.3160 | n/a | 0.2724 | n/a |
| 6 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | n/a | 0.1489 |
| 7 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |

### Attack: deepfool

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth | jpeg_preprocess | median_preprocess | random_resize |
|---|---:|---:|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a | n/a | n/a |
| 6 | 0.6002 | 0.2184 | 0.2276 | 0.1837 | n/a | 0.1185 |
| 7 | 0.6002 | 0.2184 | 0.2276 | 0.1837 | 0.1215 | n/a |

### Attack: eot_pgd

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth | jpeg_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a |
| 6 | 0.6002 | 0.2529 | 0.2555 | 0.2284 |
| 7 | 0.6002 | n/a | n/a | n/a |

### Attack: gaussian_blur

| Cycle | Baseline mAP50 | Attack mAP50 | confidence_filter | median_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | n/a | 0.5260 | 0.4464 |
| 2 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 3 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 4 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 5 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 6 | 0.6002 | n/a | n/a | n/a |
| 7 | 0.6002 | n/a | n/a | n/a |

### Attack: pgd

| Cycle | Baseline mAP50 | Attack mAP50 | confidence_filter | median_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | 0.5511 | 0.5511 | 0.3854 |
| 2 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 3 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 4 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 5 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 6 | 0.6002 | n/a | n/a | n/a |
| 7 | 0.6002 | n/a | n/a | n/a |

## Training Signal History

The worst_attack identified after each cycle drives DPC-UNet retraining in Colab.

| Cycle | Worst attack | Weakest defense | Recovery |
|---|---|---|---:|
| 1 | n/a | n/a | n/a |
| 2 | pgd | confidence_filter | -5.958 |
| 3 | pgd | confidence_filter | -5.958 |
| 4 | pgd | confidence_filter | -5.958 |
| 5 | pgd | confidence_filter | -5.958 |
| 6 | eot_pgd | jpeg_preprocess | -0.061 |
| 7 | deepfool | median_preprocess | -0.134 |
