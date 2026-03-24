# Framework Run Comparison Report

Total discovered framework runs: **17**

## Run Inventory

| Run | Model | Attack | Defense | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `none` | `complete` | 0.5244 | 0.7547 |
| `attack_deepfool` | `yolo` | `deepfool` | `none` | `complete` | 0.2541 | 0.7482 |
| `attack_fgsm` | `yolo` | `fgsm` | `none` | `complete` | 0.5192 | 0.7621 |
| `attack_pgd` | `yolo` | `pgd` | `none` | `complete` | 0.5246 | 0.7667 |
| `baseline_none` | `yolo` | `none` | `none` | `complete` | 0.5984 | 0.7648 |
| `defended_blur_c_dog` | `yolo` | `blur` | `c_dog` | `complete` | 0.2579 | 0.7410 |
| `defended_blur_c_dog_ensemble` | `yolo` | `blur` | `c_dog_ensemble` | `complete` | 0.1179 | 0.6897 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `median_preprocess` | `complete` | 0.5082 | 0.7522 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `c_dog` | `complete` | 0.0818 | 0.7092 |
| `defended_deepfool_c_dog_ensemble` | `yolo` | `deepfool` | `c_dog_ensemble` | `complete` | 0.0607 | 0.6860 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `median_preprocess` | `complete` | 0.1964 | 0.7480 |
| `defended_fgsm_c_dog` | `yolo` | `fgsm` | `c_dog` | `complete` | 0.1762 | 0.7440 |
| `defended_fgsm_c_dog_ensemble` | `yolo` | `fgsm` | `c_dog_ensemble` | `complete` | 0.0655 | 0.7051 |
| `defended_fgsm_median_preprocess` | `yolo` | `fgsm` | `median_preprocess` | `complete` | 0.4851 | 0.7592 |
| `defended_pgd_c_dog` | `yolo` | `pgd` | `c_dog` | `complete` | 0.1782 | 0.7308 |
| `defended_pgd_c_dog_ensemble` | `yolo` | `pgd` | `c_dog_ensemble` | `complete` | 0.0684 | 0.6910 |
| `defended_pgd_median_preprocess` | `yolo` | `pgd` | `median_preprocess` | `complete` | 0.4912 | 0.7603 |

## Attack Effectiveness

| Model | Seed | Attack | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | 0.5984 | 0.5244 | 0.0740 | 12.4% |
| `yolo` | 42 | `deepfool` | 0.5984 | 0.2541 | 0.3443 | 57.5% |
| `yolo` | 42 | `fgsm` | 0.5984 | 0.5192 | 0.0792 | 13.2% |
| `yolo` | 42 | `pgd` | 0.5984 | 0.5246 | 0.0738 | 12.3% |

## Defense Recovery

| Model | Attack | Defense | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---:|---:|---:|
| `yolo` | `blur` | `c_dog` | 0.5244 | 0.2579 | -360.4% |
| `yolo` | `blur` | `c_dog_ensemble` | 0.5244 | 0.1179 | -549.6% |
| `yolo` | `blur` | `median_preprocess` | 0.5244 | 0.5082 | -21.9% |
| `yolo` | `deepfool` | `c_dog` | 0.2541 | 0.0818 | -50.1% |
| `yolo` | `deepfool` | `c_dog_ensemble` | 0.2541 | 0.0607 | -56.2% |
| `yolo` | `deepfool` | `median_preprocess` | 0.2541 | 0.1964 | -16.8% |
| `yolo` | `fgsm` | `c_dog` | 0.5192 | 0.1762 | -433.0% |
| `yolo` | `fgsm` | `c_dog_ensemble` | 0.5192 | 0.0655 | -572.7% |
| `yolo` | `fgsm` | `median_preprocess` | 0.5192 | 0.4851 | -43.0% |
| `yolo` | `pgd` | `c_dog` | 0.5246 | 0.1782 | -469.7% |
| `yolo` | `pgd` | `c_dog_ensemble` | 0.5246 | 0.0684 | -618.6% |
| `yolo` | `pgd` | `median_preprocess` | 0.5246 | 0.4912 | -45.3% |