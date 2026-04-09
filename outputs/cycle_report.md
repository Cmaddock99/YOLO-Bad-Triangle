# Cycle Report

Generated from 21 completed cycle(s) in `outputs/cycle_history/`.

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
| 8 | 2026-03-26 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 9 | 2026-03-27 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 10 | 2026-03-27 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 11 | 2026-03-27 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 12 | 2026-03-28 | 0.6002 | 0.2615 | blur+bit_depth | deepfool |
| 13 | 2026-03-28 | 0.6002 | n/a | n/a | n/a |
| 14 | 2026-03-29 | 0.6002 | 0.2403 | deepfool+c_dog | deepfool |
| 15 | 2026-03-30 | 0.6002 | 0.3890 | square+c_dog | dispersion_reduction |
| 16 | 2026-03-31 | 0.6002 | 0.3890 | square+c_dog | dispersion_reduction |
| 17 | 2026-04-01 | 0.6002 | 0.3890 | square+c_dog | dispersion_reduction |
| 18 | 2026-04-04 | 0.6002 | 0.3624 | square+c_dog | dispersion_reduction |
| 19 | 2026-04-05 | 0.6002 | 0.3656 | deepfool+median_preprocess | dispersion_reduction |
| 20 | 2026-04-06 | 0.6002 | 0.3656 | deepfool+median_preprocess | dispersion_reduction |
| 21 | 2026-04-07 | 0.6002 | 0.3656 | deepfool+median_preprocess | dispersion_reduction |

## Comparability Notes

Cycle history includes catalogue eras with different attack/defense sets.
Current trends focus on the latest catalogue; legacy trends are shown separately.
Pipeline semantics are also tracked so post-switch defended runs can be distinguished from older eras.

- Comparable cycles (latest-catalogue aligned): **8**
- Legacy/non-comparable cycles: **13**
- `attack_then_defense` cycles: **4**
- `defense_then_attack` cycles: **0**
- `legacy_unknown` cycles: **17**
- `mixed` cycles: **0**

Treat defended results from the `attack_then_defense` era as the canonical post-switch series.

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
| 8 | 0.6002 | +0.0000 |
| 9 | 0.6002 | +0.0000 |
| 10 | 0.6002 | +0.0000 |
| 11 | 0.6002 | +0.0000 |
| 12 | 0.6002 | +0.0000 |
| 13 | 0.6002 | +0.0000 |
| 14 | 0.6002 | +0.0000 |
| 15 | 0.6002 | +0.0000 |
| 16 | 0.6002 | +0.0000 |
| 17 | 0.6002 | +0.0000 |
| 18 | 0.6002 | +0.0000 |
| 19 | 0.6002 | +0.0000 |
| 20 | 0.6002 | +0.0000 |
| 21 | 0.6002 | +0.0000 |

## Current Catalogue Trends

Defended mAP50 for attack+defense pairs in the latest active catalogue.
Higher = better defense. Baseline mAP50 shown for reference.

### Attack: deepfool

| Cycle | Baseline mAP50 | Attack mAP50 | c_dog | jpeg_preprocess | median_preprocess |
|---|---:|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a | n/a |
| 6 | 0.6002 | 0.2184 | n/a | 0.1837 | n/a |
| 7 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 8 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 9 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 10 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 11 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 12 | 0.6002 | 0.2184 | n/a | 0.1837 | 0.1215 |
| 13 | 0.6002 | n/a | n/a | n/a | n/a |
| 14 | 0.6002 | 0.2184 | 0.2403 | 0.1663 | n/a |
| 15 | 0.6002 | 0.2184 | 0.2403 | 0.1663 | n/a |
| 16 | 0.6002 | 0.2184 | 0.2403 | 0.1663 | n/a |
| 17 | 0.6002 | 0.2184 | 0.2403 | n/a | 0.1522 |
| 18 | 0.6002 | 0.2184 | 0.2065 | 0.3175 | n/a |
| 19 | 0.6002 | 0.2184 | 0.2238 | 0.3175 | 0.3656 |
| 20 | 0.6002 | 0.2184 | 0.2238 | 0.3175 | 0.3656 |
| 21 | 0.6002 | 0.2184 | 0.2238 | 0.3175 | 0.3656 |

### Attack: dispersion_reduction

| Cycle | Baseline mAP50 | Attack mAP50 | c_dog | jpeg_preprocess | median_preprocess |
|---|---:|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a | n/a |
| 6 | 0.6002 | n/a | n/a | n/a | n/a |
| 7 | 0.6002 | n/a | n/a | n/a | n/a |
| 8 | 0.6002 | n/a | n/a | n/a | n/a |
| 9 | 0.6002 | n/a | n/a | n/a | n/a |
| 10 | 0.6002 | n/a | n/a | n/a | n/a |
| 11 | 0.6002 | n/a | n/a | n/a | n/a |
| 12 | 0.6002 | n/a | n/a | n/a | n/a |
| 13 | 0.6002 | n/a | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a | n/a |
| 15 | 0.6002 | 0.2381 | 0.2632 | 0.2015 | n/a |
| 16 | 0.6002 | 0.2381 | 0.2632 | 0.2015 | n/a |
| 17 | 0.6002 | 0.2381 | 0.2632 | n/a | 0.1758 |
| 18 | 0.6002 | 0.2381 | 0.2164 | 0.2040 | n/a |
| 19 | 0.6002 | 0.2381 | 0.2306 | 0.2040 | 0.3082 |
| 20 | 0.6002 | 0.2381 | 0.2306 | 0.2040 | 0.3082 |
| 21 | 0.6002 | 0.2381 | 0.2306 | 0.2040 | 0.3082 |

### Attack: square

| Cycle | Baseline mAP50 | Attack mAP50 | c_dog | jpeg_preprocess | median_preprocess |
|---|---:|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a | n/a |
| 6 | 0.6002 | n/a | n/a | n/a | n/a |
| 7 | 0.6002 | n/a | n/a | n/a | n/a |
| 8 | 0.6002 | n/a | n/a | n/a | n/a |
| 9 | 0.6002 | n/a | n/a | n/a | n/a |
| 10 | 0.6002 | n/a | n/a | n/a | n/a |
| 11 | 0.6002 | n/a | n/a | n/a | n/a |
| 12 | 0.6002 | n/a | n/a | n/a | n/a |
| 13 | 0.6002 | n/a | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a | n/a |
| 15 | 0.6002 | 0.3630 | 0.3890 | 0.3767 | n/a |
| 16 | 0.6002 | 0.3630 | 0.3890 | 0.3767 | n/a |
| 17 | 0.6002 | 0.3630 | 0.3890 | n/a | 0.3336 |
| 18 | 0.6002 | 0.3630 | 0.3624 | 0.3247 | n/a |
| 19 | 0.6002 | 0.3630 | 0.3503 | 0.3247 | 0.2768 |
| 20 | 0.6002 | 0.3630 | 0.3503 | 0.3247 | 0.2768 |
| 21 | 0.6002 | 0.3630 | 0.3503 | 0.3247 | 0.2768 |

## Legacy Catalogue Trends

Historical pairs from older catalogue configurations are listed separately.

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
| 8 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |
| 9 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |
| 10 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |
| 11 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |
| 12 | 0.6002 | 0.2636 | 0.2615 | n/a | 0.2603 | 0.2492 | n/a |
| 13 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 15 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 16 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 17 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 18 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 19 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 20 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |
| 21 | 0.6002 | n/a | n/a | n/a | n/a | n/a | n/a |

### Attack: deepfool

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth | random_resize |
|---|---:|---:|---:|---:|
| 1 | n/a | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a | n/a |
| 3 | 0.6002 | n/a | n/a | n/a |
| 4 | 0.6002 | n/a | n/a | n/a |
| 5 | 0.6002 | n/a | n/a | n/a |
| 6 | 0.6002 | 0.2184 | 0.2276 | 0.1185 |
| 7 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 8 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 9 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 10 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 11 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 12 | 0.6002 | 0.2184 | 0.2276 | n/a |
| 13 | 0.6002 | n/a | n/a | n/a |
| 14 | 0.6002 | 0.2184 | 0.2229 | n/a |
| 15 | 0.6002 | 0.2184 | 0.2229 | n/a |
| 16 | 0.6002 | 0.2184 | 0.2229 | n/a |
| 17 | 0.6002 | 0.2184 | 0.2229 | n/a |
| 18 | 0.6002 | 0.2184 | 0.2290 | n/a |
| 19 | 0.6002 | 0.2184 | n/a | n/a |
| 20 | 0.6002 | 0.2184 | n/a | n/a |
| 21 | 0.6002 | 0.2184 | n/a | n/a |

### Attack: dispersion_reduction

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth |
|---|---:|---:|---:|
| 1 | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a |
| 3 | 0.6002 | n/a | n/a |
| 4 | 0.6002 | n/a | n/a |
| 5 | 0.6002 | n/a | n/a |
| 6 | 0.6002 | n/a | n/a |
| 7 | 0.6002 | n/a | n/a |
| 8 | 0.6002 | n/a | n/a |
| 9 | 0.6002 | n/a | n/a |
| 10 | 0.6002 | n/a | n/a |
| 11 | 0.6002 | n/a | n/a |
| 12 | 0.6002 | n/a | n/a |
| 13 | 0.6002 | n/a | n/a |
| 14 | 0.6002 | n/a | n/a |
| 15 | 0.6002 | 0.2381 | 0.2319 |
| 16 | 0.6002 | 0.2381 | 0.2319 |
| 17 | 0.6002 | 0.2381 | 0.2319 |
| 18 | 0.6002 | 0.2381 | 0.2448 |
| 19 | 0.6002 | 0.2381 | n/a |
| 20 | 0.6002 | 0.2381 | n/a |
| 21 | 0.6002 | 0.2381 | n/a |

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
| 8 | 0.6002 | n/a | n/a | n/a |
| 9 | 0.6002 | n/a | n/a | n/a |
| 10 | 0.6002 | n/a | n/a | n/a |
| 11 | 0.6002 | n/a | n/a | n/a |
| 12 | 0.6002 | n/a | n/a | n/a |
| 13 | 0.6002 | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a |
| 15 | 0.6002 | n/a | n/a | n/a |
| 16 | 0.6002 | n/a | n/a | n/a |
| 17 | 0.6002 | n/a | n/a | n/a |
| 18 | 0.6002 | n/a | n/a | n/a |
| 19 | 0.6002 | n/a | n/a | n/a |
| 20 | 0.6002 | n/a | n/a | n/a |
| 21 | 0.6002 | n/a | n/a | n/a |

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
| 8 | 0.6002 | n/a | n/a | n/a |
| 9 | 0.6002 | n/a | n/a | n/a |
| 10 | 0.6002 | n/a | n/a | n/a |
| 11 | 0.6002 | n/a | n/a | n/a |
| 12 | 0.6002 | n/a | n/a | n/a |
| 13 | 0.6002 | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a |
| 15 | 0.6002 | n/a | n/a | n/a |
| 16 | 0.6002 | n/a | n/a | n/a |
| 17 | 0.6002 | n/a | n/a | n/a |
| 18 | 0.6002 | n/a | n/a | n/a |
| 19 | 0.6002 | n/a | n/a | n/a |
| 20 | 0.6002 | n/a | n/a | n/a |
| 21 | 0.6002 | n/a | n/a | n/a |

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
| 8 | 0.6002 | n/a | n/a | n/a |
| 9 | 0.6002 | n/a | n/a | n/a |
| 10 | 0.6002 | n/a | n/a | n/a |
| 11 | 0.6002 | n/a | n/a | n/a |
| 12 | 0.6002 | n/a | n/a | n/a |
| 13 | 0.6002 | n/a | n/a | n/a |
| 14 | 0.6002 | n/a | n/a | n/a |
| 15 | 0.6002 | n/a | n/a | n/a |
| 16 | 0.6002 | n/a | n/a | n/a |
| 17 | 0.6002 | n/a | n/a | n/a |
| 18 | 0.6002 | n/a | n/a | n/a |
| 19 | 0.6002 | n/a | n/a | n/a |
| 20 | 0.6002 | n/a | n/a | n/a |
| 21 | 0.6002 | n/a | n/a | n/a |

### Attack: square

| Cycle | Baseline mAP50 | Attack mAP50 | bit_depth |
|---|---:|---:|---:|
| 1 | n/a | n/a | n/a |
| 2 | 0.6002 | n/a | n/a |
| 3 | 0.6002 | n/a | n/a |
| 4 | 0.6002 | n/a | n/a |
| 5 | 0.6002 | n/a | n/a |
| 6 | 0.6002 | n/a | n/a |
| 7 | 0.6002 | n/a | n/a |
| 8 | 0.6002 | n/a | n/a |
| 9 | 0.6002 | n/a | n/a |
| 10 | 0.6002 | n/a | n/a |
| 11 | 0.6002 | n/a | n/a |
| 12 | 0.6002 | n/a | n/a |
| 13 | 0.6002 | n/a | n/a |
| 14 | 0.6002 | n/a | n/a |
| 15 | 0.6002 | 0.3630 | 0.3863 |
| 16 | 0.6002 | 0.3630 | 0.3863 |
| 17 | 0.6002 | 0.3630 | 0.3863 |
| 18 | 0.6002 | 0.3630 | 0.3499 |
| 19 | 0.6002 | 0.3630 | n/a |
| 20 | 0.6002 | 0.3630 | n/a |
| 21 | 0.6002 | 0.3630 | n/a |

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
| 8 | deepfool | median_preprocess | -0.134 |
| 9 | deepfool | median_preprocess | -0.134 |
| 10 | deepfool | median_preprocess | -0.134 |
| 11 | deepfool | median_preprocess | -0.134 |
| 12 | deepfool | median_preprocess | -0.134 |
| 13 | n/a | n/a | n/a |
| 14 | deepfool | jpeg_preprocess | -0.073 |
| 15 | deepfool | jpeg_preprocess | -0.073 |
| 16 | deepfool | jpeg_preprocess | -0.073 |
| 17 | deepfool | median_preprocess | -0.065 |
| 18 | square | jpeg_preprocess | -0.017 |
| 19 | square | median_preprocess | -0.032 |
| 20 | square | median_preprocess | -0.032 |
| 21 | square | median_preprocess | -0.032 |
