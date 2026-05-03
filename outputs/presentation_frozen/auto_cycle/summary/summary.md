# Auto Summary Report

**Runs root:** `/Users/lurch/ml-labs/YOLO-Bad-Triangle/outputs/framework_runs/cycle_20260326_112654`  
**Total runs discovered:** 72

## Warnings

- **MULTIPLE_BASELINES**: 2 no-attack/no-defense runs found; 'baseline_none' selected (first alphabetically). Runs with different image counts or validation status may produce misleading comparisons.
- **ATTACK_BELOW_NOISE**: Attack 'blur' shows < 5% confidence suppression — may be within noise or misconfigured.
- **ATTACK_BELOW_NOISE**: Attack 'deepfool' shows < 5% confidence suppression — may be within noise or misconfigured.
- **ATTACK_BELOW_NOISE**: Attack 'eot_pgd' shows < 5% confidence suppression — may be within noise or misconfigured.
- **ATTACK_BELOW_NOISE**: Attack 'fgsm' shows < 5% confidence suppression — may be within noise or misconfigured.
- **ATTACK_BELOW_NOISE**: Attack 'pgd' shows < 5% confidence suppression — may be within noise or misconfigured.
- **ATTACK_BELOW_NOISE**: Attack 'square' shows < 5% confidence suppression — may be within noise or misconfigured.

## Baseline

| Run | Model | Seed | Total det | Avg conf | mAP50 |
|---|---|---:|---:|---:|---:|
| `baseline_none` | `yolo` | 42 | 100.0 | 0.7623 | n/a |

## Attack Effectiveness

| Model | Attack | Objective | mAP50 drop | Effectiveness | Det drop | Det drop CI (95%) | Conf drop | Conf drop CI (95%) |
|---|---|---|---:|---:|---:|---|---:|---|
| `yolo` | `blur` | `` | n/a | n/a | 27.0% | [14.4%, 40.8%] | 0.6% | [-3.6%, 6.2%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 78.0% | [67.0%, 86.9%] | 3.5% | [-5.8%, 12.6%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 21.0% | [6.9%, 37.1%] | -1.6% | [-9.4%, 2.3%] |
| `yolo` | `fgsm` | `untargeted_conf_suppression` | n/a | n/a | 19.0% | [11.3%, 28.3%] | -1.4% | [-7.1%, 3.3%] |
| `yolo` | `pgd` | `untargeted_conf_suppression` | n/a | n/a | 11.0% | [3.2%, 19.3%] | 1.6% | [-4.3%, 5.4%] |
| `yolo` | `square` | `` | n/a | n/a | 9.0% | [-2.0%, 19.3%] | 1.9% | [-5.2%, 3.8%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 62.0% | [67.0%, 86.9%] | 3.1% | [-5.8%, 12.6%] |
| `yolo` | `blur` | `` | n/a | n/a | 94.0% | [57.9%, 84.2%] | 3.6% | [-5.2%, 15.3%] |
| `yolo` | `blur` | `` | n/a | n/a | 95.0% | [58.8%, 87.5%] | -0.0% | [-6.4%, 12.2%] |
| `yolo` | `blur` | `` | n/a | n/a | 89.0% | [21.4%, 62.5%] | 3.8% | [-3.3%, 18.5%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [26.7%, 85.3%] | 0.2% | [-1.0%, 11.2%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 94.0% | [42.9%, 88.5%] | -7.0% | [-9.7%, 4.1%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 91.0% | [23.5%, 76.5%] | 0.9% | [-11.7%, 13.2%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [26.7%, 85.3%] | 0.2% | [-2.0%, 11.2%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 93.0% | [35.7%, 87.1%] | -2.6% | [-7.2%, 10.0%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [26.7%, 85.3%] | 0.2% | [-1.0%, 11.2%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [25.0%, 85.3%] | -3.0% | [-7.6%, 8.3%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [25.0%, 83.9%] | -7.8% | [-10.5%, 2.4%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 91.0% | [38.1%, 73.3%] | -4.1% | [-11.4%, 0.9%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 93.0% | [31.2%, 87.1%] | -5.1% | [-10.6%, 6.6%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 90.0% | [16.7%, 72.4%] | 1.6% | [-3.3%, 16.9%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 92.0% | [30.8%, 79.0%] | -2.1% | [-9.7%, 14.2%] |
| `yolo` | `eot_pgd` | `untargeted_conf_suppression` | n/a | n/a | 93.0% | [31.2%, 87.9%] | -4.5% | [-9.0%, 9.0%] |
| `yolo` | `blur` | `` | n/a | n/a | -440.0% | [54.9%, 76.2%] | 2.8% | [-1.6%, 12.4%] |
| `yolo` | `deepfool` | `untargeted_conf_suppression` | n/a | n/a | -147.0% | [70.2%, 89.5%] | 0.7% | [-4.8%, 10.0%] |

## Defense Recovery

No defended runs found.

## Per-Class Vulnerability

| Model | Attack | Class | Baseline | Attacked | Drop | Defended | Recovery |
|---|---|---|---:|---:|---:|---:|---:|
| `yolo` | `blur` | person | 43 | 31 | 27.9% | 32 | 8.3% |
| `yolo` | `blur` | car | 3 | 2 | 33.3% | 2 | 0.0% |
| `yolo` | `blur` | airplane | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `blur` | bus | 4 | 3 | 25.0% | 5 | 200.0% |
| `yolo` | `blur` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | bird | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | cat | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | zebra | 1 | 3 | -200.0% | 1 | 100.0% |
| `yolo` | `blur` | handbag | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | suitcase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `blur` | baseball bat | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | baseball glove | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | tennis racket | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `blur` | wine glass | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `blur` | cup | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `blur` | bowl | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | banana | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | apple | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `blur` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | chair | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `blur` | potted plant | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `blur` | bed | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `blur` | dining table | 2 | 3 | -50.0% | 2 | 100.0% |
| `yolo` | `blur` | tv | 3 | 3 | 0.0% | 3 | n/a |
| `yolo` | `blur` | laptop | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | person | 43 | 10 | 76.7% | 20 | 30.3% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 1 | 75.0% | 1 | 0.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `eot_pgd` | person | 43 | 38 | 11.6% | 38 | 0.0% |
| `yolo` | `eot_pgd` | car | 3 | 5 | -66.7% | 5 | -0.0% |
| `yolo` | `eot_pgd` | airplane | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `eot_pgd` | bus | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | dog | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | snowboard | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `eot_pgd` | baseball bat | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | baseball glove | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 3 | -50.0% | 3 | -0.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 5 | -25.0% | 5 | -0.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 3 | 25.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `eot_pgd` | dining table | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `eot_pgd` | tv | 3 | 2 | 33.3% | 1 | -100.0% |
| `yolo` | `eot_pgd` | laptop | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | keyboard | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | cell phone | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `eot_pgd` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | person | 43 | 37 | 14.0% | None | n/a |
| `yolo` | `fgsm` | car | 3 | 5 | -66.7% | None | n/a |
| `yolo` | `fgsm` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `fgsm` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | bird | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | zebra | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | skis | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `fgsm` | baseball bat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | tennis racket | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `fgsm` | wine glass | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `fgsm` | cup | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `fgsm` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | chair | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `fgsm` | potted plant | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `fgsm` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | dining table | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | tv | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `fgsm` | laptop | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `fgsm` | mouse | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | keyboard | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | refrigerator | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | teddy bear | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `pgd` | person | 43 | 42 | 2.3% | None | n/a |
| `yolo` | `pgd` | car | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `pgd` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | bird | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | zebra | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `pgd` | handbag | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | suitcase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | baseball bat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | baseball glove | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | tennis racket | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `pgd` | wine glass | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | apple | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | chair | 4 | 5 | -25.0% | None | n/a |
| `yolo` | `pgd` | potted plant | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `pgd` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | dining table | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `pgd` | tv | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `pgd` | laptop | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `pgd` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | keyboard | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `pgd` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `pgd` | teddy bear | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `square` | person | 43 | 43 | 0.0% | None | n/a |
| `yolo` | `square` | car | 3 | 4 | -33.3% | None | n/a |
| `yolo` | `square` | airplane | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `square` | bus | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `square` | truck | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | stop sign | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | bird | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | cat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | bear | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | zebra | 1 | 3 | -200.0% | None | n/a |
| `yolo` | `square` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | baseball bat | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | tennis racket | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `square` | wine glass | 4 | 4 | 0.0% | None | n/a |
| `yolo` | `square` | cup | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `square` | knife | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | bowl | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | chair | 4 | 3 | 25.0% | None | n/a |
| `yolo` | `square` | potted plant | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `square` | bed | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `square` | dining table | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `square` | tv | 3 | 2 | 33.3% | None | n/a |
| `yolo` | `square` | laptop | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `square` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | keyboard | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | oven | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `square` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `square` | vase | 0 | 1 | n/a | None | n/a |
| `yolo` | `square` | teddy bear | 2 | 2 | 0.0% | None | n/a |
| `yolo` | `deepfool` | person | 43 | 21 | 51.2% | 20 | -4.5% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 3 | 25.0% | 2 | -100.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 1 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | broccoli | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 2 | 50.0% | 1 | -50.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 1 | 50.0% | 3 | 200.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `blur` | person | 43 | 2 | 95.3% | 32 | 73.2% |
| `yolo` | `blur` | car | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `blur` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bus | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `blur` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | cat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | skis | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `blur` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | baseball glove | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | cup | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | banana | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | apple | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | chair | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | potted plant | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `blur` | dining table | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | tv | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `blur` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | refrigerator | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | person | 43 | 2 | 95.3% | 32 | 73.2% |
| `yolo` | `blur` | car | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `blur` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bus | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `blur` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | cat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | skis | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `blur` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | baseball glove | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | cup | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | banana | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | apple | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | chair | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | potted plant | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `blur` | dining table | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | tv | 3 | 1 | 66.7% | 3 | 100.0% |
| `yolo` | `blur` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | refrigerator | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | person | 43 | 1 | 97.7% | 32 | 73.8% |
| `yolo` | `blur` | car | 3 | 0 | 100.0% | 2 | 66.7% |
| `yolo` | `blur` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bus | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `blur` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | cat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | zebra | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | suitcase | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | skis | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `blur` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | baseball glove | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | wine glass | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | cup | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | banana | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | apple | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `blur` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | chair | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `blur` | potted plant | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `blur` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `blur` | dining table | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `blur` | tv | 3 | 2 | 33.3% | 3 | 100.0% |
| `yolo` | `blur` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | sports ball | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 1 | 75.0% | 1 | 0.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | sports ball | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `deepfool` | sports ball | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 2 | 95.3% | 20 | 43.9% |
| `yolo` | `deepfool` | car | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `deepfool` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | bird | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `deepfool` | zebra | 1 | 0 | 100.0% | 2 | 200.0% |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | sports ball | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tennis racket | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `deepfool` | wine glass | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 0 | 100.0% | 1 | 25.0% |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `deepfool` | dining table | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `deepfool` | tv | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | frisbee | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 2 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 2 | 50.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | clock | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | snowboard | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 1 | 75.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 1 | 50.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 1 | 75.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | person | 43 | 2 | 95.3% | 38 | 87.8% |
| `yolo` | `eot_pgd` | car | 3 | 0 | 100.0% | 5 | 166.7% |
| `yolo` | `eot_pgd` | airplane | 2 | 0 | 100.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | bus | 4 | 0 | 100.0% | 2 | 50.0% |
| `yolo` | `eot_pgd` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `eot_pgd` | bird | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | cat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | elephant | 0 | 1 | n/a | None | n/a |
| `yolo` | `eot_pgd` | bear | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | zebra | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | suitcase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | skis | 3 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | tennis racket | 2 | 0 | 100.0% | 3 | 150.0% |
| `yolo` | `eot_pgd` | wine glass | 4 | 0 | 100.0% | 5 | 125.0% |
| `yolo` | `eot_pgd` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bowl | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | banana | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | chair | 4 | 0 | 100.0% | 4 | 100.0% |
| `yolo` | `eot_pgd` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | bed | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `eot_pgd` | dining table | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | tv | 3 | 0 | 100.0% | 1 | 33.3% |
| `yolo` | `eot_pgd` | laptop | 2 | 0 | 100.0% | 1 | 50.0% |
| `yolo` | `eot_pgd` | mouse | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | keyboard | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `eot_pgd` | clock | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `eot_pgd` | teddy bear | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | person | 43 | 287 | -567.4% | 32 | 104.5% |
| `yolo` | `blur` | car | 3 | 15 | -400.0% | 2 | 108.3% |
| `yolo` | `blur` | motorcycle | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | airplane | 2 | 4 | -100.0% | 2 | 100.0% |
| `yolo` | `blur` | bus | 4 | 13 | -225.0% | 5 | 88.9% |
| `yolo` | `blur` | train | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | truck | 1 | 3 | -200.0% | None | n/a |
| `yolo` | `blur` | boat | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | fire hydrant | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | stop sign | 1 | 3 | -200.0% | 1 | 100.0% |
| `yolo` | `blur` | parking meter | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | bird | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | cat | 1 | 5 | -400.0% | 1 | 100.0% |
| `yolo` | `blur` | dog | 0 | 5 | n/a | None | n/a |
| `yolo` | `blur` | horse | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | sheep | 0 | 11 | n/a | None | n/a |
| `yolo` | `blur` | elephant | 0 | 9 | n/a | None | n/a |
| `yolo` | `blur` | bear | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `blur` | zebra | 1 | 3 | -200.0% | 1 | 100.0% |
| `yolo` | `blur` | giraffe | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | umbrella | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | handbag | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | tie | 0 | 5 | n/a | None | n/a |
| `yolo` | `blur` | suitcase | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `blur` | frisbee | 0 | 7 | n/a | None | n/a |
| `yolo` | `blur` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `blur` | sports ball | 0 | 5 | n/a | None | n/a |
| `yolo` | `blur` | kite | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | baseball bat | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | baseball glove | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `blur` | skateboard | 0 | 1 | n/a | None | n/a |
| `yolo` | `blur` | surfboard | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | tennis racket | 2 | 3 | -50.0% | 1 | 200.0% |
| `yolo` | `blur` | bottle | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | wine glass | 4 | 2 | 50.0% | 2 | 0.0% |
| `yolo` | `blur` | cup | 2 | 6 | -200.0% | 2 | 100.0% |
| `yolo` | `blur` | bowl | 1 | 9 | -800.0% | 1 | 100.0% |
| `yolo` | `blur` | banana | 1 | 5 | -400.0% | 1 | 100.0% |
| `yolo` | `blur` | apple | 2 | 4 | -100.0% | 1 | 150.0% |
| `yolo` | `blur` | sandwich | 0 | 1 | n/a | None | n/a |
| `yolo` | `blur` | orange | 0 | 10 | n/a | None | n/a |
| `yolo` | `blur` | broccoli | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | carrot | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | hot dog | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | pizza | 0 | 8 | n/a | None | n/a |
| `yolo` | `blur` | donut | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `blur` | chair | 4 | 6 | -50.0% | 2 | 200.0% |
| `yolo` | `blur` | couch | 0 | 3 | n/a | None | n/a |
| `yolo` | `blur` | potted plant | 2 | 1 | 50.0% | 1 | 0.0% |
| `yolo` | `blur` | bed | 2 | 4 | -100.0% | 2 | 100.0% |
| `yolo` | `blur` | dining table | 2 | 8 | -300.0% | 2 | 100.0% |
| `yolo` | `blur` | toilet | 0 | 6 | n/a | None | n/a |
| `yolo` | `blur` | tv | 3 | 9 | -200.0% | 3 | 100.0% |
| `yolo` | `blur` | laptop | 2 | 12 | -500.0% | None | n/a |
| `yolo` | `blur` | mouse | 1 | 3 | -200.0% | None | n/a |
| `yolo` | `blur` | remote | 0 | 2 | n/a | None | n/a |
| `yolo` | `blur` | keyboard | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `blur` | cell phone | 0 | 4 | n/a | None | n/a |
| `yolo` | `blur` | oven | 1 | 0 | 100.0% | 1 | 100.0% |
| `yolo` | `blur` | refrigerator | 1 | 2 | -100.0% | 1 | 100.0% |
| `yolo` | `blur` | clock | 1 | 2 | -100.0% | None | n/a |
| `yolo` | `blur` | teddy bear | 2 | 1 | 50.0% | 2 | 100.0% |
| `yolo` | `deepfool` | person | 43 | 117 | -172.1% | 20 | 131.1% |
| `yolo` | `deepfool` | bicycle | 0 | 3 | n/a | None | n/a |
| `yolo` | `deepfool` | car | 3 | 3 | 0.0% | None | n/a |
| `yolo` | `deepfool` | motorcycle | 0 | 3 | n/a | None | n/a |
| `yolo` | `deepfool` | airplane | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `deepfool` | bus | 4 | 4 | 0.0% | 2 | n/a |
| `yolo` | `deepfool` | train | 0 | 4 | n/a | None | n/a |
| `yolo` | `deepfool` | truck | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | traffic light | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | fire hydrant | 0 | 5 | n/a | None | n/a |
| `yolo` | `deepfool` | stop sign | 1 | 3 | -200.0% | 1 | 100.0% |
| `yolo` | `deepfool` | bird | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | cat | 1 | 4 | -300.0% | None | n/a |
| `yolo` | `deepfool` | dog | 0 | 2 | n/a | 1 | 50.0% |
| `yolo` | `deepfool` | horse | 0 | 2 | n/a | None | n/a |
| `yolo` | `deepfool` | sheep | 0 | 6 | n/a | None | n/a |
| `yolo` | `deepfool` | cow | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | elephant | 0 | 2 | n/a | None | n/a |
| `yolo` | `deepfool` | bear | 1 | 4 | -300.0% | 1 | 100.0% |
| `yolo` | `deepfool` | zebra | 1 | 13 | -1200.0% | 2 | 91.7% |
| `yolo` | `deepfool` | giraffe | 0 | 6 | n/a | None | n/a |
| `yolo` | `deepfool` | handbag | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | tie | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `deepfool` | suitcase | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | frisbee | 0 | 3 | n/a | None | n/a |
| `yolo` | `deepfool` | skis | 3 | 1 | 66.7% | 1 | 0.0% |
| `yolo` | `deepfool` | sports ball | 0 | 3 | n/a | None | n/a |
| `yolo` | `deepfool` | kite | 0 | 2 | n/a | None | n/a |
| `yolo` | `deepfool` | baseball bat | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | baseball glove | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | skateboard | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `deepfool` | surfboard | 0 | 2 | n/a | 1 | 50.0% |
| `yolo` | `deepfool` | tennis racket | 2 | 5 | -150.0% | 1 | 133.3% |
| `yolo` | `deepfool` | wine glass | 4 | 1 | 75.0% | 1 | 0.0% |
| `yolo` | `deepfool` | cup | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bowl | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | banana | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | apple | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | broccoli | 0 | 2 | n/a | 1 | 50.0% |
| `yolo` | `deepfool` | carrot | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | pizza | 0 | 4 | n/a | None | n/a |
| `yolo` | `deepfool` | cake | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | chair | 4 | 2 | 50.0% | 1 | -50.0% |
| `yolo` | `deepfool` | couch | 0 | 4 | n/a | None | n/a |
| `yolo` | `deepfool` | potted plant | 2 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | bed | 2 | 4 | -100.0% | 1 | 150.0% |
| `yolo` | `deepfool` | dining table | 2 | 3 | -50.0% | 3 | -0.0% |
| `yolo` | `deepfool` | toilet | 0 | 3 | n/a | None | n/a |
| `yolo` | `deepfool` | tv | 3 | 1 | 66.7% | None | n/a |
| `yolo` | `deepfool` | laptop | 2 | 3 | -50.0% | None | n/a |
| `yolo` | `deepfool` | mouse | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | remote | 0 | 1 | n/a | None | n/a |
| `yolo` | `deepfool` | keyboard | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `deepfool` | oven | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | refrigerator | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `deepfool` | clock | 1 | 3 | -200.0% | None | n/a |
| `yolo` | `deepfool` | vase | 0 | 2 | n/a | None | n/a |
| `yolo` | `deepfool` | teddy bear | 2 | 2 | 0.0% | 2 | n/a |
