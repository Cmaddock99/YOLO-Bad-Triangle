# Auto Summary Report

**Runs root:** `/Users/lurch/ml-labs/YOLO-Bad-Triangle/outputs/demo_audit/20260501T044919Z/runs`  
**Total runs discovered:** 3

## Warnings

- **LOW_ATTACK_COUNT**: Only 1 attack run(s) found; comparison results may be incomplete.
- **ATTACK_BELOW_NOISE**: Attack 'fgsm' shows < 5% mAP50 drop — may be within noise or misconfigured.
- **DEFENSE_DEGRADES_PERFORMANCE**: Defense 'median_preprocess' against attack 'fgsm' degrades performance beyond the attack alone (recovery=-9.000). Defense may be misconfigured or incompatible with this attack.

## Baseline

| Run | Model | Seed | Total det | Avg conf | mAP50 |
|---|---|---:|---:|---:|---:|
| `baseline_none` | `yolo` | 42 | 31.0 | 0.6316 | 0.7082 |

## Attack Effectiveness

| Model | Attack | Objective | mAP50 drop | Effectiveness | Det drop | Det drop CI (95%) | Conf drop | Conf drop CI (95%) |
|---|---|---|---:|---:|---:|---|---:|---|
| `yolo` | `fgsm` | `untargeted_conf_suppression` | -0.5% | -0.7% | 3.2% | [-8.1%, 25.0%] | 5.9% | [-16.1%, 16.8%] |

## Defense Recovery

| Model | Attack | Defense | mAP50 (atk) | mAP50 (def) | mAP50 recovery | Det recovery |
|---|---|---|---:|---:|---:|---:|
| `yolo` | `fgsm` | `median_preprocess` | 0.7132 | 0.6639 | 991.6% | -900.0% |

## Per-Class Vulnerability

| Model | Attack | Class | Baseline | Attacked | Drop | Defended | Recovery |
|---|---|---|---:|---:|---:|---:|---:|
| `yolo` | `fgsm` | person | 6 | 5 | 16.7% | 4 | -100.0% |
| `yolo` | `fgsm` | truck | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | stop sign | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | bear | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | skis | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | baseball glove | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | bottle | 1 | 1 | 0.0% | None | n/a |
| `yolo` | `fgsm` | chair | 3 | 4 | -33.3% | 2 | 200.0% |
| `yolo` | `fgsm` | potted plant | 4 | 4 | 0.0% | 2 | n/a |
| `yolo` | `fgsm` | bed | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | dining table | 0 | 1 | n/a | 1 | -0.0% |
| `yolo` | `fgsm` | tv | 2 | 3 | -50.0% | 2 | 100.0% |
| `yolo` | `fgsm` | oven | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | refrigerator | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | book | 2 | 2 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | clock | 1 | 1 | 0.0% | 1 | n/a |
| `yolo` | `fgsm` | vase | 1 | 0 | 100.0% | None | n/a |
| `yolo` | `fgsm` | teddy bear | 3 | 3 | 0.0% | 2 | n/a |
