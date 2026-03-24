# Cycle Report

Generated from 5 completed cycle(s) in `outputs/cycle_history/`.

## Executive Summary

| Cycle | Date | Baseline mAP50 | Best defended mAP50 | Best config | Worst attack |
|---|---|---:|---:|---|---|
| 1 | 2026-03-23 | n/a | 0.5511 | pgd+confidence_filter | n/a |
| 2 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 3 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 4 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |
| 5 | 2026-03-23 | 0.6002 | 0.5511 | pgd+confidence_filter | blur |

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

## Attack × Defense mAP50 Trends

Defended mAP50 for each attack+defense pair across cycles. Higher = better defense. Baseline mAP50 shown for reference.

### Attack: blur

| Cycle | Baseline mAP50 | Attack mAP50 | confidence_filter | median_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | n/a | 0.5260 | 0.4464 |
| 2 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 3 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 4 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 5 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |

### Attack: gaussian_blur

| Cycle | Baseline mAP50 | Attack mAP50 | confidence_filter | median_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | n/a | 0.5260 | 0.4464 |
| 2 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 3 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 4 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |
| 5 | 0.6002 | 0.3160 | 0.3160 | 0.2724 |

### Attack: pgd

| Cycle | Baseline mAP50 | Attack mAP50 | confidence_filter | median_preprocess |
|---|---:|---:|---:|---:|
| 1 | n/a | 0.5511 | 0.5511 | 0.3854 |
| 2 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 3 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 4 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |
| 5 | 0.6002 | 0.5511 | 0.5511 | 0.3854 |

## Training Signal History

The worst_attack identified after each cycle drives DPC-UNet retraining in Colab.

| Cycle | Worst attack | Weakest defense | Recovery |
|---|---|---|---:|
| 1 | n/a | n/a | n/a |
| 2 | pgd | confidence_filter | -5.958 |
| 3 | pgd | confidence_filter | -5.958 |
| 4 | pgd | confidence_filter | -5.958 |
| 5 | pgd | confidence_filter | -5.958 |
