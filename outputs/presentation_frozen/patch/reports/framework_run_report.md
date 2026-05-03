# Framework Run Comparison Report

Total discovered framework runs: **14**

Pipeline profile: `yolo11n_patch_eval_v1`
Authoritative metric: `mAP50`

## Run Inventory

| Run | Model | Attack | Artifact | Placement | Defense | Semantics | Validation | mAP50 | Avg conf |
|---|---|---|---|---|---|---|---|---:|---:|
| `patchmatrix__canonical_patch_artifact__largest_person_torso__bit_depth` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `bit_depth` | `attack_then_defense` | `complete` | 0.5738 | 0.8507 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__blind_patch_recover` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `blind_patch_recover` | `attack_then_defense` | `complete` | 0.6094 | 0.8570 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__c_dog` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `c_dog` | `attack_then_defense` | `complete` | 0.5868 | 0.8459 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__jpeg_preprocess` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.5924 | 0.8490 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__median_preprocess` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `median_preprocess` | `attack_then_defense` | `complete` | 0.5541 | 0.8121 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__none` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `none` | `attack_then_defense` | `complete` | 0.5873 | 0.8524 |
| `patchmatrix__canonical_patch_artifact__largest_person_torso__oracle_patch_recover` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `oracle_patch_recover` | `attack_then_defense` | `complete` | 0.6268 | 0.8570 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__bit_depth` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `bit_depth` | `attack_then_defense` | `complete` | 0.7073 | 0.8134 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__blind_patch_recover` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `blind_patch_recover` | `attack_then_defense` | `complete` | 0.6980 | 0.8148 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__c_dog` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `c_dog` | `attack_then_defense` | `complete` | 0.7014 | 0.8249 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__jpeg_preprocess` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `jpeg_preprocess` | `attack_then_defense` | `complete` | 0.6550 | 0.7475 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__median_preprocess` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `median_preprocess` | `attack_then_defense` | `complete` | 0.6693 | 0.7607 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__none` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `none` | `attack_then_defense` | `complete` | 0.6975 | 0.7396 |
| `patchmatrix__canonical_patch_artifact__off_object_fixed__oracle_patch_recover` | `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `oracle_patch_recover` | `attack_then_defense` | `complete` | 0.6986 | 0.8150 |

## Attack Effectiveness

| Model | Seed | Attack | Artifact | Placement | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|---:|
| `yolo` | 42 | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `` |  | `` |  | 0.5873 |  |  |
| `yolo` | 42 | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `` |  | `` |  | 0.6975 |  |  |

## Defense Recovery

| Model | Attack | Artifact | Placement | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |
|---|---|---|---|---|---|---:|---|---:|---:|---:|
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `bit_depth` | `` |  | `` | 0.5873 | 0.5738 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `blind_patch_recover` | `` |  | `` | 0.5873 | 0.6094 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `c_dog` | `` |  | `` | 0.5873 | 0.5868 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `jpeg_preprocess` | `` |  | `` | 0.5873 | 0.5924 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `median_preprocess` | `` |  | `` | 0.5873 | 0.5541 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `largest_person_torso` | `oracle_patch_recover` | `` |  | `` | 0.5873 | 0.6268 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `bit_depth` | `` |  | `` | 0.6975 | 0.7073 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `blind_patch_recover` | `` |  | `` | 0.6975 | 0.6980 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `c_dog` | `` |  | `` | 0.6975 | 0.7014 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `jpeg_preprocess` | `` |  | `` | 0.6975 | 0.6550 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `median_preprocess` | `` |  | `` | 0.6975 | 0.6693 |  |
| `yolo` | `pretrained_patch` | `yolo11n_patch_v2` | `off_object_fixed` | `oracle_patch_recover` | `` |  | `` | 0.6975 | 0.6986 |  |

## Imported Patch Recovery

No imported patch comparisons found.

## Per-Class Detection Drop

No per-class data available (run with validation or inspect predictions.jsonl).