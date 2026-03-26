# Framework Run Comparison Report

Total discovered framework runs: **7**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `missing` |  | 0.7566 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `missing` |  | 0.7268 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `none` | `missing` |  | 0.7785 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `missing` |  | 0.7763 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `missing` |  | 0.7463 |
| `attack_square` | `yolo` | `square` | `none` | `missing` |  | 0.7433 |
| `baseline_none` | `yolo` | `none` | `none` | `missing` |  | 0.7623 |

## Attack Effectiveness

| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` |  | `` |  |  |  |  |

## Defense Recovery

No defended runs found. Run with `--defenses` to enable defense sweep.

## Per-Class Detection Drop

| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |
|---|---:|---|---:|---|---:|---:|---:|
| `yolo` | 42 | `blur` | 0 | person | 43 | 31 | 27.9% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 10 | 76.7% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 38 | 11.6% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 5 | -66.7% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 16 | dog | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 31 | snowboard | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 5 | -25.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 67 | cell phone | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 0 | person | 43 | 37 | 14.0% |
| `yolo` | 42 | `fgsm` | 2 | car | 3 | 5 | -66.7% |
| `yolo` | 42 | `fgsm` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 30 | skis | 3 | 2 | 33.3% |
| `yolo` | 42 | `fgsm` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `fgsm` | 40 | wine glass | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 41 | cup | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `fgsm` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `fgsm` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `fgsm` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 60 | dining table | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `fgsm` | 63 | laptop | 2 | 2 | 0.0% |
| `yolo` | 42 | `fgsm` | 64 | mouse | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `fgsm` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 0 | person | 43 | 42 | 2.3% |
| `yolo` | 42 | `pgd` | 2 | car | 3 | 3 | 0.0% |
| `yolo` | 42 | `pgd` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 22 | zebra | 1 | 2 | -100.0% |
| `yolo` | 42 | `pgd` | 26 | handbag | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 40 | wine glass | 4 | 3 | 25.0% |
| `yolo` | 42 | `pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 47 | apple | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 56 | chair | 4 | 5 | -25.0% |
| `yolo` | 42 | `pgd` | 58 | potted plant | 2 | 3 | -50.0% |
| `yolo` | 42 | `pgd` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 60 | dining table | 2 | 2 | 0.0% |
| `yolo` | 42 | `pgd` | 62 | tv | 3 | 3 | 0.0% |
| `yolo` | 42 | `pgd` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 0 | person | 43 | 43 | 0.0% |
| `yolo` | 42 | `square` | 2 | car | 3 | 4 | -33.3% |
| `yolo` | 42 | `square` | 4 | airplane | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `square` | 7 | truck | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 15 | cat | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `square` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `square` | 34 | baseball bat | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 38 | tennis racket | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 40 | wine glass | 4 | 4 | 0.0% |
| `yolo` | 42 | `square` | 41 | cup | 2 | 3 | -50.0% |
| `yolo` | 42 | `square` | 43 | knife | 0 | 1 |  |
| `yolo` | 42 | `square` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `square` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 56 | chair | 4 | 3 | 25.0% |
| `yolo` | 42 | `square` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 59 | bed | 2 | 2 | 0.0% |
| `yolo` | 42 | `square` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `square` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `square` | 63 | laptop | 2 | 1 | 50.0% |
| `yolo` | 42 | `square` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `square` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `square` | 75 | vase | 0 | 1 |  |
| `yolo` | 42 | `square` | 77 | teddy bear | 2 | 2 | 0.0% |