# Auto Summary Report

**Runs root:** `/home/lurch/YOLO-Bad-Triangle/outputs/framework_runs/cycle_20260430_135845`  
**Total runs discovered:** 92

## Baseline

| Run | Model | Seed | Total det | Avg conf | mAP50 |
|---|---|---:|---:|---:|---:|
| `validate_baseline` | `yolo` | 42 | 1576.0 | 0.7498 | 0.5765 |

## Attack Effectiveness

| Model | Attack | Objective | mAP50 drop | Effectiveness | Det drop | Det drop CI (95%) | Conf drop | Conf drop CI (95%) |
|---|---|---|---:|---:|---:|---|---:|---|
| `yolo` | `blur` | `` | n/a | n/a | 17.9% | not computed | 1.7% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 68.8% | not computed | 6.8% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 49.1% | not computed | 3.1% | not computed |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 61.6% | not computed | 1.7% | not computed |
| `yolo` | `fgsm` | `untargeted_conf_suppression` | n/a | n/a | 15.2% | not computed | -0.3% | not computed |
| `yolo` | `pgd` | `untargeted_conf_suppression` | n/a | n/a | 11.6% | not computed | 0.3% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 16.1% | not computed | 0.9% | not computed |
| `yolo` | `square` | `` | n/a | n/a | -24.1% | not computed | 0.9% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 97.3% | not computed | 10.4% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 100.0% | not computed | n/a | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 100.0% | not computed | n/a | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 53.6% | not computed | -3.0% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 76.8% | not computed | 6.8% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 84.8% | not computed | -0.8% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 83.9% | not computed | 2.8% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 96.4% | not computed | -0.1% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 100.0% | not computed | n/a | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 81.2% | not computed | 0.7% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 95.5% | not computed | 5.8% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 94.6% | not computed | 5.9% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 95.5% | not computed | 5.8% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 65.2% | not computed | -3.4% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 75.9% | not computed | 0.4% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 75.9% | not computed | -2.2% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 75.0% | not computed | 0.0% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 82.1% | not computed | 0.3% | not computed |
| `yolo` | `dispersion_reduction` | `` | n/a | n/a | 92.9% | not computed | 1.6% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 87.5% | not computed | 1.2% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 92.0% | not computed | -0.4% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 92.9% | not computed | -4.3% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 92.9% | not computed | -4.3% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 82.1% | not computed | -4.2% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 82.1% | not computed | -1.7% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 82.1% | not computed | -3.4% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 83.9% | not computed | -2.8% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 81.2% | not computed | 1.0% | not computed |
| `yolo` | `square` | `` | n/a | n/a | 82.1% | not computed | 1.2% | not computed |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | 54.0% | 93.7% | 100.0% | not computed | n/a | not computed |
| `yolo` | `dispersion_reduction` | `` | 40.4% | 70.1% | 98.9% | not computed | 3.8% | not computed |
| `yolo` | `square` | `` | 17.7% | 30.8% | 94.0% | not computed | 4.9% | not computed |

## Defense Recovery

| Model | Attack | Defense | mAP50 (atk) | mAP50 (def) | mAP50 recovery | Det recovery |
|---|---|---|---:|---:|---:|---:|
| `yolo` | `deepfool` | `bit_depth` | n/a | n/a | n/a | 2.6% |
| `yolo` | `deepfool` | `jpeg_preprocess` | n/a | n/a | n/a | 16.9% |
| `yolo` | `deepfool` | `median_preprocess` | n/a | n/a | n/a | 35.1% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -1.8% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | 3.6% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | 16.4% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | 0.0% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | 0.0% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -66.7% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -50.9% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -411.1% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -52.7% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -416.7% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -54.5% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -422.2% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -49.1% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -427.8% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -52.7% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -416.7% |
| `yolo` | `dispersion_reduction` | `bit_depth` | n/a | n/a | n/a | -54.5% |
| `yolo` | `square` | `bit_depth` | n/a | n/a | n/a | -416.7% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | -45.5% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | -427.8% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | -58.2% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | -438.9% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | -45.5% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | -427.8% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | -56.4% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | -422.2% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | n/a | n/a | n/a | -54.5% |
| `yolo` | `square` | `jpeg_preprocess` | n/a | n/a | n/a | -416.7% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | -47.3% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -427.8% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | -40.0% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -444.4% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | -72.7% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -483.3% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | -92.7% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -511.1% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | n/a | n/a | n/a | -47.3% |
| `yolo` | `square` | `median_preprocess` | n/a | n/a | n/a | -427.8% |
| `yolo` | `deepfool` | `bit_depth` | 0.0363 | 0.0359 | -0.1% | 0.0% |
| `yolo` | `deepfool` | `jpeg_preprocess` | 0.0363 | 0.0304 | -1.1% | 0.0% |
| `yolo` | `deepfool` | `median_preprocess` | 0.0363 | 0.0248 | -2.1% | 0.0% |
| `yolo` | `dispersion_reduction` | `bit_depth` | 0.1725 | 0.1858 | 3.3% | 0.3% |
| `yolo` | `dispersion_reduction` | `jpeg_preprocess` | 0.1725 | 0.1679 | -1.1% | 0.8% |
| `yolo` | `dispersion_reduction` | `median_preprocess` | 0.1725 | 0.2892 | 28.9% | 2.4% |
| `yolo` | `square` | `bit_depth` | 0.3991 | 0.4013 | 1.3% | 0.1% |
| `yolo` | `square` | `jpeg_preprocess` | 0.3991 | 0.3109 | -49.8% | -1.2% |
| `yolo` | `square` | `median_preprocess` | 0.3991 | 0.3280 | -40.1% | 0.9% |

## Per-Class Vulnerability

| Model | Attack | Class | Baseline | Attacked | Drop | Defended | Recovery |
|---|---|---|---:|---:|---:|---:|---:|
| `yolo` | `blur` | person | 50 | 41 | 18.0% | None | n/a |
| `yolo` | `blur` | car | 6 | 5 | 16.7% | None | n/a |
| `yolo` | `blur` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `blur` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | zebra | 1 | 3 | -200.0% | None | n/a |
| `yolo` | `blur` | handbag | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | suitcase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | skis | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | tennis racket | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `blur` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | wine glass | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `blur` | cup | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `blur` | knife | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | bowl | 0 | 1 | n/a | None | n/a |
| `yolo` | `blur` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | apple | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `blur` | sandwich | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | chair | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `blur` | potted plant | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `blur` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `blur` | dining table | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `blur` | tv | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `blur` | laptop | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | keyboard | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `blur` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | refrigerator | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | vase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 21 | 58.0% | 23 | 6.9% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 1 | 75.0% | 2 | 33.3% |
| `yolo` | `deepfool` | train | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | umbrella | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | tennis racket | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 1 | 75.0% | 1 | 0.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 3 | -50.0% | 3 | -0.0% |
| `yolo` | `deepfool` | dining table | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 32 | 36.0% | 33 | 5.6% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | bus | 4 | 3 | 25.0% | 3 | 0.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 2 | -100.0% | 2 | -0.0% |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bowl | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bed | 2 | 2 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | dining table | 3 | 2 | 33.3% | 2 | 0.0% |
| `yolo` | `dispersion_reduction` | toilet | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 50 | 24 | 52.0% | None | n/a |
| `yolo` | `eot_pgd` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `eot_pgd` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | potted plant | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `eot_pgd` | dining table | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `eot_pgd` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | vase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | person | 50 | 49 | 2.0% | None | n/a |
| `yolo` | `fgsm` | car | 6 | 4 | 33.3% | None | n/a |
| `yolo` | `fgsm` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `fgsm` | truck | 0 | 1 | n/a | None | n/a |
| `yolo` | `fgsm` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | zebra | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | skis | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | tennis racket | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `fgsm` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | wine glass | 4 | 4 | 0.0% | None | n/a |
| `yolo` | `fgsm` | cup | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | knife | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | apple | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | cake | 0 | 1 | n/a | None | n/a |
| `yolo` | `fgsm` | chair | 3 | 4 | -33.3% | None | n/a |
| `yolo` | `fgsm` | potted plant | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | dining table | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | tv | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | laptop | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | mouse | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | keyboard | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `fgsm` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | refrigerator | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | vase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | teddy bear | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | person | 50 | 50 | 0.0% | None | n/a |
| `yolo` | `pgd` | car | 6 | 2 | 66.7% | None | n/a |
| `yolo` | `pgd` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `pgd` | truck | 0 | 1 | n/a | None | n/a |
| `yolo` | `pgd` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | zebra | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | skis | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `pgd` | tennis racket | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `pgd` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | wine glass | 4 | 4 | 0.0% | None | n/a |
| `yolo` | `pgd` | cup | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `pgd` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | spoon | 0 | 1 | n/a | None | n/a |
| `yolo` | `pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | apple | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `pgd` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | chair | 3 | 4 | -33.3% | None | n/a |
| `yolo` | `pgd` | couch | 0 | 1 | n/a | None | n/a |
| `yolo` | `pgd` | potted plant | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `pgd` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | dining table | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `pgd` | tv | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `pgd` | laptop | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | mouse | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | keyboard | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `pgd` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | refrigerator | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `pgd` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | vase | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `pgd` | teddy bear | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `square` | person | 50 | 47 | 6.0% | 47 | 0.0% |
| `yolo` | `square` | car | 6 | 4 | 33.3% | 4 | 0.0% |
| `yolo` | `square` | airplane | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | bus | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | bird | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | handbag | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 2 | -100.0% | 2 | -0.0% |
| `yolo` | `square` | tennis racket | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 4 | 0.0% | 4 | n/a |
| `yolo` | `square` | cup | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `square` | knife | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | donut | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `square` | chair | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | potted plant | 3 | 2 | 33.3% | 2 | 0.0% |
| `yolo` | `square` | bed | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | dining table | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | tv | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | laptop | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 72 | -44.0% | 47 | 113.6% |
| `yolo` | `square` | car | 6 | 4 | 33.3% | 4 | 0.0% |
| `yolo` | `square` | airplane | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | bus | 4 | 3 | 25.0% | 2 | -100.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | bird | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | handbag | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | tie | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 2 | -100.0% | 2 | -0.0% |
| `yolo` | `square` | skateboard | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | surfboard | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | tennis racket | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 4 | 0.0% | 4 | n/a |
| `yolo` | `square` | cup | 3 | 3 | 0.0% | 1 | n/a |
| `yolo` | `square` | knife | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | broccoli | 0 | 5 | n/a | None | n/a |
| `yolo` | `square` | donut | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `square` | chair | 3 | 4 | -33.3% | 3 | 100.0% |
| `yolo` | `square` | couch | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | potted plant | 3 | 2 | 33.3% | 2 | 0.0% |
| `yolo` | `square` | bed | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | dining table | 3 | 4 | -33.3% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 4 | -33.3% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | sink | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | person | 50 | 2 | 96.0% | 23 | 43.8% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | umbrella | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 0 | 100.0% | 23 | 46.0% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 0 | 100.0% | 23 | 46.0% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 25 | 50.0% | 23 | -8.0% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | tennis racket | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `deepfool` | bottle | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `deepfool` | potted plant | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 3 | 200.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 3 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | laptop | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 19 | 62.0% | 23 | 12.9% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 3 | 200.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 10 | 80.0% | 23 | 32.5% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | couch | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 3 | 200.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 10 | 80.0% | 23 | 32.5% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | sports ball | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 3 | 200.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 2 | 96.0% | 23 | 43.8% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | person | 50 | 0 | 100.0% | 23 | 46.0% |
| `yolo` | `deepfool` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `deepfool` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | potted plant | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | dining table | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 15 | 70.0% | 33 | 51.4% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 4 | 92.0% | 33 | 63.0% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 4 | 92.0% | 33 | 63.0% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 4 | 92.0% | 33 | 63.0% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 21 | 58.0% | 33 | 41.4% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 3 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 19 | 62.0% | 33 | 45.2% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 19 | 62.0% | 33 | 45.2% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 20 | 60.0% | 33 | 43.3% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 16 | 68.0% | 33 | 50.0% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 50 | 5 | 90.0% | 33 | 62.2% |
| `yolo` | `dispersion_reduction` | car | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `dispersion_reduction` | bus | 4 | 0 | 100.0% | 3 | 75.0% |
| `yolo` | `dispersion_reduction` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `dispersion_reduction` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bottle | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `dispersion_reduction` | cup | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `dispersion_reduction` | potted plant | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dining table | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `dispersion_reduction` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | laptop | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | person | 50 | 3 | 94.0% | 47 | 93.6% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 1 | 66.7% | 2 | 50.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | person | 50 | 2 | 96.0% | 47 | 93.8% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 1 | 66.7% | 2 | 50.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | teddy bear | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | person | 50 | 1 | 98.0% | 47 | 93.9% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 1 | 66.7% | 2 | 50.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | refrigerator | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | person | 50 | 1 | 98.0% | 47 | 93.9% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 1 | 66.7% | 2 | 50.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | refrigerator | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | person | 50 | 3 | 94.0% | 47 | 93.6% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 3 | 0.0% | 2 | n/a |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 4 | 92.0% | 47 | 93.5% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 3 | 0.0% | 2 | n/a |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 4 | 92.0% | 47 | 93.5% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 3 | 0.0% | 2 | n/a |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 4 | 92.0% | 47 | 93.5% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | potted plant | 3 | 1 | 66.7% | 2 | 50.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 2 | 96.0% | 47 | 93.8% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | potted plant | 3 | 5 | -66.7% | 2 | 150.0% |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `square` | person | 50 | 2 | 96.0% | 47 | 93.8% |
| `yolo` | `square` | car | 6 | 0 | 100.0% | 4 | 66.7% |
| `yolo` | `square` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `square` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | tie | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | skis | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `square` | tennis racket | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | bottle | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | wine glass | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `square` | cup | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `square` | knife | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | sandwich | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `square` | potted plant | 3 | 3 | 0.0% | 2 | n/a |
| `yolo` | `square` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `square` | dining table | 3 | 0 | 100.0% | 3 | 100.0% |
| `yolo` | `square` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `square` | laptop | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `square` | teddy bear | 2 | 3 | -50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 606 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bicycle | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | car | 74 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | motorcycle | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 18 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | train | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | truck | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | boat | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | traffic light | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | fire hydrant | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | parking meter | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bench | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bird | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | horse | 23 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sheep | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cow | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | elephant | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | zebra | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | giraffe | 10 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | backpack | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | umbrella | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | frisbee | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sports ball | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | kite | 14 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball bat | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skateboard | 11 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | surfboard | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bottle | 28 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | wine glass | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cup | 40 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | fork | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | knife | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | spoon | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sandwich | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | orange | 18 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | broccoli | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | carrot | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | hot dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | pizza | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | donut | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 64 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | couch | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | potted plant | 16 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | dining table | 25 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | toilet | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tv | 22 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | remote | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 14 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cell phone | 19 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | sink | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | book | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | vase | 10 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | person | 606 | 10 | 98.3% | 12 | 0.3% |
| `yolo` | `dispersion_reduction` | bicycle | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | car | 74 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | motorcycle | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | airplane | 9 | 2 | 77.8% | 2 | 0.0% |
| `yolo` | `dispersion_reduction` | bus | 18 | 1 | 94.4% | 2 | 5.9% |
| `yolo` | `dispersion_reduction` | train | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | truck | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | boat | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | traffic light | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | fire hydrant | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | stop sign | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `dispersion_reduction` | parking meter | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bench | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bird | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cat | 13 | 1 | 92.3% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | horse | 23 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | sheep | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cow | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | elephant | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bear | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | zebra | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | giraffe | 10 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | backpack | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | umbrella | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tie | 17 | 1 | 94.1% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | suitcase | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | frisbee | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skis | 7 | 1 | 85.7% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | sports ball | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | kite | 14 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | baseball bat | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | baseball glove | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | skateboard | 11 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | surfboard | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tennis racket | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bottle | 28 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | wine glass | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cup | 40 | 1 | 97.5% | 1 | 0.0% |
| `yolo` | `dispersion_reduction` | fork | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | knife | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | spoon | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bowl | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | banana | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | apple | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | sandwich | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | orange | 18 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | broccoli | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | carrot | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | hot dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | pizza | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | donut | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cake | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | chair | 64 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | couch | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | potted plant | 16 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | bed | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | dining table | 25 | 0 | 100.0% | 1 | 4.0% |
| `yolo` | `dispersion_reduction` | toilet | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | tv | 22 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | laptop | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | mouse | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | remote | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | keyboard | 14 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | cell phone | 19 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | oven | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | sink | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | refrigerator | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | book | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | clock | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | vase | 10 | 0 | 100.0% | None | n/a |
| `yolo` | `dispersion_reduction` | teddy bear | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | person | 606 | 54 | 91.1% | 56 | 0.4% |
| `yolo` | `square` | bicycle | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | car | 74 | 3 | 95.9% | 3 | 0.0% |
| `yolo` | `square` | motorcycle | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | airplane | 9 | 1 | 88.9% | 2 | 12.5% |
| `yolo` | `square` | bus | 18 | 3 | 83.3% | 3 | 0.0% |
| `yolo` | `square` | train | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | truck | 7 | 1 | 85.7% | None | n/a |
| `yolo` | `square` | boat | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `square` | traffic light | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | fire hydrant | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | stop sign | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `square` | parking meter | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bench | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bird | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cat | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | horse | 23 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | sheep | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cow | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | elephant | 15 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bear | 4 | 1 | 75.0% | 1 | 0.0% |
| `yolo` | `square` | zebra | 26 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | giraffe | 10 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | backpack | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | umbrella | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | tie | 17 | 2 | 88.2% | 2 | 0.0% |
| `yolo` | `square` | suitcase | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | frisbee | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | skis | 7 | 1 | 85.7% | 1 | 0.0% |
| `yolo` | `square` | snowboard | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `square` | sports ball | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | kite | 14 | 7 | 50.0% | 7 | 0.0% |
| `yolo` | `square` | baseball bat | 6 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | baseball glove | 7 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | skateboard | 11 | 1 | 90.9% | 1 | 0.0% |
| `yolo` | `square` | surfboard | 13 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | tennis racket | 17 | 1 | 94.1% | 1 | 0.0% |
| `yolo` | `square` | bottle | 28 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | wine glass | 15 | 3 | 80.0% | 2 | -8.3% |
| `yolo` | `square` | cup | 40 | 2 | 95.0% | 2 | 0.0% |
| `yolo` | `square` | fork | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | knife | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | spoon | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | bowl | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | banana | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | apple | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | sandwich | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | orange | 18 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | broccoli | 13 | 1 | 92.3% | 1 | 0.0% |
| `yolo` | `square` | carrot | 8 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | hot dog | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | pizza | 17 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | donut | 12 | 0 | 100.0% | 2 | 16.7% |
| `yolo` | `square` | cake | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `square` | chair | 64 | 1 | 98.4% | 1 | 0.0% |
| `yolo` | `square` | couch | 15 | 1 | 93.3% | 1 | 0.0% |
| `yolo` | `square` | potted plant | 16 | 1 | 93.8% | 1 | 0.0% |
| `yolo` | `square` | bed | 15 | 2 | 86.7% | 2 | 0.0% |
| `yolo` | `square` | dining table | 25 | 2 | 92.0% | 2 | 0.0% |
| `yolo` | `square` | toilet | 12 | 1 | 91.7% | None | n/a |
| `yolo` | `square` | tv | 22 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | laptop | 24 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | mouse | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | remote | 4 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 14 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cell phone | 19 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | oven | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | sink | 5 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | refrigerator | 9 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | book | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | clock | 12 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | vase | 10 | 1 | 90.0% | 1 | 0.0% |
| `yolo` | `square` | teddy bear | 7 | 0 | 100.0% | 1 | 14.3% |
