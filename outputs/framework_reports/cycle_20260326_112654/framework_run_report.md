# Framework Run Comparison Report

Total discovered framework runs: **72**

## Comparability Warning

Discovered runs span multiple pipeline semantics.
Defense recovery rows below include only runs recorded with `attack_then_defense` semantics.
Legacy or unknown-era defended runs remain in inventory but are excluded from recovery comparisons.

- `attack_then_defense` runs: **0**
- `defense_then_attack` runs: **0**
- `legacy_unknown` runs: **72**

## Run Inventory

| Run | Model | Attack | Artifact | Placement | Defense | Semantics | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---|---|---|---:|---:|
| `attack_blur` | `yolo` | `blur` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7566 |
| `attack_deepfool` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7268 |
| `attack_eot_pgd` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7785 |
| `attack_fgsm` | `yolo` | `fgsm` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7763 |
| `attack_pgd` | `yolo` | `pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7463 |
| `attack_square` | `yolo` | `square` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7433 |
| `baseline_none` | `yolo` | `none` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7623 |
| `consistency_atk_deepfool` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7315 |
| `consistency_deepfool_bit_depth` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7211 |
| `consistency_deepfool_c_dog` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7637 |
| `consistency_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7895 |
| `consistency_deepfool_median_preprocess` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7450 |
| `defended_blur_bit_depth` | `yolo` | `blur` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7493 |
| `defended_blur_c_dog` | `yolo` | `blur` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7475 |
| `defended_blur_jpeg_preprocess` | `yolo` | `blur` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7564 |
| `defended_blur_median_preprocess` | `yolo` | `blur` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7510 |
| `defended_deepfool_bit_depth` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7235 |
| `defended_deepfool_c_dog` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7609 |
| `defended_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.8256 |
| `defended_deepfool_median_preprocess` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7791 |
| `defended_eot_pgd_bit_depth` | `yolo` | `eot_pgd` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7831 |
| `defended_eot_pgd_c_dog` | `yolo` | `eot_pgd` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7285 |
| `defended_eot_pgd_jpeg_preprocess` | `yolo` | `eot_pgd` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7650 |
| `defended_eot_pgd_median_preprocess` | `yolo` | `eot_pgd` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7735 |
| `tune_atk_blur_001` | `yolo` | `blur` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7260 |
| `tune_atk_blur_002` | `yolo` | `blur` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7626 |
| `tune_atk_blur_003` | `yolo` | `blur` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7239 |
| `tune_atk_deepfool_001` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7605 |
| `tune_atk_deepfool_002` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.8321 |
| `tune_atk_deepfool_003` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7529 |
| `tune_atk_deepfool_004` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7602 |
| `tune_atk_deepfool_005` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7885 |
| `tune_atk_deepfool_best` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7605 |
| `tune_atk_eot_pgd_001` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7919 |
| `tune_atk_eot_pgd_002` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.8399 |
| `tune_atk_eot_pgd_003` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.8035 |
| `tune_atk_eot_pgd_004` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.8137 |
| `tune_atk_eot_pgd_005` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7463 |
| `tune_atk_eot_pgd_006` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.7837 |
| `tune_atk_eot_pgd_007` | `yolo` | `eot_pgd` | `` | `` | `none` | `legacy_unknown` | `missing` |  | 0.8076 |
| `tune_def_bit_depth_001` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7705 |
| `tune_def_bit_depth_002` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.8208 |
| `tune_def_bit_depth_003` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.8119 |
| `tune_def_bit_depth_004` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7546 |
| `tune_def_bit_depth_005` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `missing` |  | 0.7705 |
| `tune_def_c_dog_001` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.9044 |
| `tune_def_c_dog_002` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7226 |
| `tune_def_c_dog_003` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.7939 |
| `tune_def_c_dog_004` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `missing` |  | 0.8349 |
| `tune_def_jpeg_preprocess_001` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7537 |
| `tune_def_jpeg_preprocess_002` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.8682 |
| `tune_def_jpeg_preprocess_003` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.8205 |
| `tune_def_jpeg_preprocess_004` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7915 |
| `tune_def_jpeg_preprocess_005` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `missing` |  | 0.7537 |
| `tune_def_median_preprocess_001` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.8619 |
| `tune_def_median_preprocess_002` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.8682 |
| `tune_def_median_preprocess_003` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7686 |
| `tune_def_median_preprocess_004` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.9108 |
| `tune_def_median_preprocess_005` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.8619 |
| `tune_def_median_preprocess_006` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.7957 |
| `tune_def_median_preprocess_007` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `missing` |  | 0.8682 |
| `validate_atk_blur` | `yolo` | `blur` | `` | `` | `none` | `legacy_unknown` | `complete` | 0.2629 | 0.7346 |
| `validate_atk_deepfool` | `yolo` | `deepfool` | `` | `` | `none` | `legacy_unknown` | `complete` | 0.2188 | 0.7551 |
| `validate_baseline` | `yolo` | `none` | `` | `` | `none` | `legacy_unknown` | `complete` | 0.5984 | 0.7648 |
| `validate_blur_bit_depth` | `yolo` | `blur` | `` | `` | `bit_depth` | `legacy_unknown` | `complete` | 0.2631 | 0.7338 |
| `validate_blur_c_dog` | `yolo` | `blur` | `` | `` | `c_dog` | `legacy_unknown` | `complete` | 0.1763 | 0.7155 |
| `validate_blur_jpeg_preprocess` | `yolo` | `blur` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `complete` | 0.2605 | 0.7314 |
| `validate_blur_median_preprocess` | `yolo` | `blur` | `` | `` | `median_preprocess` | `legacy_unknown` | `complete` | 0.2173 | 0.7412 |
| `validate_deepfool_bit_depth` | `yolo` | `deepfool` | `` | `` | `bit_depth` | `legacy_unknown` | `complete` | 0.2222 | 0.7367 |
| `validate_deepfool_c_dog` | `yolo` | `deepfool` | `` | `` | `c_dog` | `legacy_unknown` | `complete` | 0.1280 | 0.7355 |
| `validate_deepfool_jpeg_preprocess` | `yolo` | `deepfool` | `` | `` | `jpeg_preprocess` | `legacy_unknown` | `complete` | 0.1967 | 0.7485 |
| `validate_deepfool_median_preprocess` | `yolo` | `deepfool` | `` | `` | `median_preprocess` | `legacy_unknown` | `complete` | 0.0649 | 0.6975 |

## Attack Effectiveness

| Model | Seed | Attack | Artifact | Placement | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `fgsm` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `square` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `eot_pgd` | `` | `` | `untargeted_conf_suppression` |  | `` |  |  |  |  |
| `yolo` | 42 | `blur` | `` | `` | `` |  | `` |  | 0.2629 |  |  |
| `yolo` | 42 | `deepfool` | `` | `` | `untargeted_conf_suppression` |  | `` |  | 0.2188 |  |  |

## Defense Recovery

Defended runs from legacy or unknown pipeline eras are excluded from this table to avoid mixing incomparable recovery semantics.

No defended runs found. Run with `--defenses` to enable defense sweep.

## Imported Patch Recovery

No imported patch comparisons found.

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
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 21 | 51.2% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 3 | 25.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 0 | 1 |  |
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
| `yolo` | 42 | `deepfool` | 50 | broccoli | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |
| `yolo` | 42 | `blur` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 43 | 1 | 97.7% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 2 | 33.3% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 0 | 100.0% |
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
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 29 | frisbee | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 2 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 31 | snowboard | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 1 | 75.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 0 | person | 43 | 2 | 95.3% |
| `yolo` | 42 | `eot_pgd` | 2 | car | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 4 | airplane | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 5 | bus | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 7 | truck | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 11 | stop sign | 1 | 1 | 0.0% |
| `yolo` | 42 | `eot_pgd` | 14 | bird | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 15 | cat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 20 | elephant | 0 | 1 |  |
| `yolo` | 42 | `eot_pgd` | 21 | bear | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 22 | zebra | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 28 | suitcase | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 30 | skis | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 35 | baseball glove | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 38 | tennis racket | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 40 | wine glass | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 45 | bowl | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 46 | banana | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 56 | chair | 4 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 59 | bed | 2 | 1 | 50.0% |
| `yolo` | 42 | `eot_pgd` | 60 | dining table | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 62 | tv | 3 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 63 | laptop | 2 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 66 | keyboard | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `eot_pgd` | 74 | clock | 1 | 0 | 100.0% |
| `yolo` | 42 | `eot_pgd` | 77 | teddy bear | 2 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 0 | person | 43 | 287 | -567.4% |
| `yolo` | 42 | `blur` | 2 | car | 3 | 15 | -400.0% |
| `yolo` | 42 | `blur` | 3 | motorcycle | 0 | 4 |  |
| `yolo` | 42 | `blur` | 4 | airplane | 2 | 4 | -100.0% |
| `yolo` | 42 | `blur` | 5 | bus | 4 | 13 | -225.0% |
| `yolo` | 42 | `blur` | 6 | train | 0 | 4 |  |
| `yolo` | 42 | `blur` | 7 | truck | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 8 | boat | 0 | 2 |  |
| `yolo` | 42 | `blur` | 10 | fire hydrant | 0 | 3 |  |
| `yolo` | 42 | `blur` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 12 | parking meter | 0 | 3 |  |
| `yolo` | 42 | `blur` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 15 | cat | 1 | 5 | -400.0% |
| `yolo` | 42 | `blur` | 16 | dog | 0 | 5 |  |
| `yolo` | 42 | `blur` | 17 | horse | 0 | 3 |  |
| `yolo` | 42 | `blur` | 18 | sheep | 0 | 11 |  |
| `yolo` | 42 | `blur` | 20 | elephant | 0 | 9 |  |
| `yolo` | 42 | `blur` | 21 | bear | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 22 | zebra | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 23 | giraffe | 0 | 4 |  |
| `yolo` | 42 | `blur` | 25 | umbrella | 0 | 4 |  |
| `yolo` | 42 | `blur` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 27 | tie | 0 | 5 |  |
| `yolo` | 42 | `blur` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 29 | frisbee | 0 | 7 |  |
| `yolo` | 42 | `blur` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `blur` | 32 | sports ball | 0 | 5 |  |
| `yolo` | 42 | `blur` | 33 | kite | 0 | 2 |  |
| `yolo` | 42 | `blur` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 35 | baseball glove | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 36 | skateboard | 0 | 1 |  |
| `yolo` | 42 | `blur` | 37 | surfboard | 0 | 4 |  |
| `yolo` | 42 | `blur` | 38 | tennis racket | 2 | 3 | -50.0% |
| `yolo` | 42 | `blur` | 39 | bottle | 0 | 2 |  |
| `yolo` | 42 | `blur` | 40 | wine glass | 4 | 2 | 50.0% |
| `yolo` | 42 | `blur` | 41 | cup | 2 | 6 | -200.0% |
| `yolo` | 42 | `blur` | 45 | bowl | 1 | 9 | -800.0% |
| `yolo` | 42 | `blur` | 46 | banana | 1 | 5 | -400.0% |
| `yolo` | 42 | `blur` | 47 | apple | 2 | 4 | -100.0% |
| `yolo` | 42 | `blur` | 48 | sandwich | 0 | 1 |  |
| `yolo` | 42 | `blur` | 49 | orange | 0 | 10 |  |
| `yolo` | 42 | `blur` | 50 | broccoli | 0 | 3 |  |
| `yolo` | 42 | `blur` | 51 | carrot | 0 | 2 |  |
| `yolo` | 42 | `blur` | 52 | hot dog | 0 | 3 |  |
| `yolo` | 42 | `blur` | 53 | pizza | 0 | 8 |  |
| `yolo` | 42 | `blur` | 54 | donut | 0 | 2 |  |
| `yolo` | 42 | `blur` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 56 | chair | 4 | 6 | -50.0% |
| `yolo` | 42 | `blur` | 57 | couch | 0 | 3 |  |
| `yolo` | 42 | `blur` | 58 | potted plant | 2 | 1 | 50.0% |
| `yolo` | 42 | `blur` | 59 | bed | 2 | 4 | -100.0% |
| `yolo` | 42 | `blur` | 60 | dining table | 2 | 8 | -300.0% |
| `yolo` | 42 | `blur` | 61 | toilet | 0 | 6 |  |
| `yolo` | 42 | `blur` | 62 | tv | 3 | 9 | -200.0% |
| `yolo` | 42 | `blur` | 63 | laptop | 2 | 12 | -500.0% |
| `yolo` | 42 | `blur` | 64 | mouse | 1 | 3 | -200.0% |
| `yolo` | 42 | `blur` | 65 | remote | 0 | 2 |  |
| `yolo` | 42 | `blur` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `blur` | 67 | cell phone | 0 | 4 |  |
| `yolo` | 42 | `blur` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `blur` | 72 | refrigerator | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 74 | clock | 1 | 2 | -100.0% |
| `yolo` | 42 | `blur` | 77 | teddy bear | 2 | 1 | 50.0% |
| `yolo` | 42 | `deepfool` | 0 | person | 43 | 117 | -172.1% |
| `yolo` | 42 | `deepfool` | 1 | bicycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 2 | car | 3 | 3 | 0.0% |
| `yolo` | 42 | `deepfool` | 3 | motorcycle | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 4 | airplane | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 5 | bus | 4 | 4 | 0.0% |
| `yolo` | 42 | `deepfool` | 6 | train | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 7 | truck | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 9 | traffic light | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 10 | fire hydrant | 0 | 5 |  |
| `yolo` | 42 | `deepfool` | 11 | stop sign | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 14 | bird | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 15 | cat | 1 | 4 | -300.0% |
| `yolo` | 42 | `deepfool` | 16 | dog | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 17 | horse | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 18 | sheep | 0 | 6 |  |
| `yolo` | 42 | `deepfool` | 19 | cow | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 20 | elephant | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 21 | bear | 1 | 4 | -300.0% |
| `yolo` | 42 | `deepfool` | 22 | zebra | 1 | 13 | -1200.0% |
| `yolo` | 42 | `deepfool` | 23 | giraffe | 0 | 6 |  |
| `yolo` | 42 | `deepfool` | 26 | handbag | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 27 | tie | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 28 | suitcase | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 29 | frisbee | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 30 | skis | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 32 | sports ball | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 33 | kite | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 34 | baseball bat | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 35 | baseball glove | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 36 | skateboard | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 37 | surfboard | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 38 | tennis racket | 2 | 5 | -150.0% |
| `yolo` | 42 | `deepfool` | 40 | wine glass | 4 | 1 | 75.0% |
| `yolo` | 42 | `deepfool` | 41 | cup | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 45 | bowl | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 46 | banana | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 47 | apple | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 50 | broccoli | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 51 | carrot | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 53 | pizza | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 55 | cake | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 56 | chair | 4 | 2 | 50.0% |
| `yolo` | 42 | `deepfool` | 57 | couch | 0 | 4 |  |
| `yolo` | 42 | `deepfool` | 58 | potted plant | 2 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 59 | bed | 2 | 4 | -100.0% |
| `yolo` | 42 | `deepfool` | 60 | dining table | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 61 | toilet | 0 | 3 |  |
| `yolo` | 42 | `deepfool` | 62 | tv | 3 | 1 | 66.7% |
| `yolo` | 42 | `deepfool` | 63 | laptop | 2 | 3 | -50.0% |
| `yolo` | 42 | `deepfool` | 64 | mouse | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 65 | remote | 0 | 1 |  |
| `yolo` | 42 | `deepfool` | 66 | keyboard | 1 | 1 | 0.0% |
| `yolo` | 42 | `deepfool` | 69 | oven | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 72 | refrigerator | 1 | 0 | 100.0% |
| `yolo` | 42 | `deepfool` | 74 | clock | 1 | 3 | -200.0% |
| `yolo` | 42 | `deepfool` | 75 | vase | 0 | 2 |  |
| `yolo` | 42 | `deepfool` | 77 | teddy bear | 2 | 2 | 0.0% |