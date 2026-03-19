# Wrapper Verification Report

Date: 2026-03-19  
Checkpoint: `/Users/lurch/Downloads/dpc_unet_final_golden.pt`  
Scope: Thorough reverse-engineering verification for provisional framework-side defense use.

## Executive Decision

Decision: **NO-GO for default/canonical integration**  
Classification: **Experimental candidate only (blocked)**  

Reason: While loadability, stability, and reproducibility checks passed, downstream detector checks show the wrapper **reduces** confidence and detections on both clean and attacked inputs in the tested configuration.

## Artifacts Produced

- `outputs/wrapper_verification/checkpoint_contract.json`
- `outputs/wrapper_verification/input_sweep_details.csv`
- `outputs/wrapper_verification/input_sweep_summary.json`
- `outputs/wrapper_verification/timestep_probe.csv`
- `outputs/wrapper_verification/timestep_probe_summary.json`
- `outputs/wrapper_verification/distance_repro_details.csv`
- `outputs/wrapper_verification/distance_repro_summary.json`
- `outputs/wrapper_verification/downstream_matrix/downstream_matrix.csv`
- `outputs/wrapper_verification/downstream_matrix/downstream_matrix_summary.json`

## Step Results

## 1) Checkpoint Contract + Loadability

- strict load with inferred DPC-UNet architecture: **PASS**
- missing keys: none
- unexpected keys: none
- state dict tensors: `48`
- parameters: `492,483`
- SHA256: `6d875e201e6845d50134d858ca7f3dd7cda89e6cf99829ce4380a067e788b250`

## 2) Input Convention Sweep

All 8 tested combos were finite and shape-preserving.

Best candidate by low distortion + low saturation:

- `color=bgr | scaling=zero_one | normalize=1`
  - mean L2 RMSE: `68.84`
  - saturation mean: `0.00232`

## 3) Timestep Probe (raw + normalized equivalents)

Config used:

- `color_order=bgr`, `scaling=zero_one`, `normalize=true`

Top stable candidates by detector confidence:

- timestep `50.0`: mean conf `0.6606`, mean L2 RMSE `65.83`
- timestep `999.0`: mean conf `0.6606`, mean L2 RMSE `65.72`
- timestep `10.0`: mean conf `0.6560`, mean L2 RMSE `68.30`

Selected operating point for downstream checks: **timestep = 50**

## 4) Identity-Distance + Reproducibility

Config:

- `color_order=bgr`, `scaling=zero_one`, `normalize=true`, `timestep=50`
- images: `64`, repeats: `3`

Results:

- all finite: **true**
- reproducible all images: **true**
- max unique output hashes per image: `1`
- mean L2 RMSE over images: `66.45`
- min/max L2 RMSE over images: `45.40` / `114.27`

## 5) Downstream Mini Matrix (Most Important)

Subset size: `16` images  
Attacks tested: `fgsm`, `pgd`, `deepfool`

Clean baseline delta with wrapper:

- confidence delta: `-0.0437`
- detections delta: `-37`

Attacked-case deltas with wrapper (vs attack-only):

- FGSM: confidence delta `-0.0128`, detections delta `-37`
- PGD: confidence delta `-0.0379`, detections delta `-38`
- DeepFool: confidence delta `-0.0213`, detections delta `-36`

Interpretation:

- Wrapper decreases confidence and detections in both clean and attacked cases for tested settings.
- No evidence of attack recovery advantage in this battery.

## 6) Provisional Framework Integration Hook

Implemented framework-side provisional defense:

- `src/lab/defenses/preprocess_dpc_unet_adapter.py`

Adapter guardrails:

- fail on missing checkpoint
- fail on non-finite output
- fail on output shape mismatch
- identity postprocess with metadata

Framework smoke run with adapter succeeded:

- run: `outputs/wrapper_verification/wrapper_adapter_smoke`
- outputs present: `predictions.jsonl`, `metrics.json`, `run_summary.json`, `resolved_config.yaml`

Legacy safety check:

- legacy runner path still executes unchanged (compat smoke pass).

## Validation Gate Summary

- Runner executes without crash: **PASS**
- Framework artifacts exist and non-empty: **PASS**
- Metrics finite/null with valid validation status: **PASS**
- Legacy path unchanged: **PASS**
- Output naming/path contracts preserved: **PASS**
- Downstream effectiveness gate (attack recovery without clean collapse): **FAIL**

## Go/No-Go Decision

**NO-GO** for making this wrapper a default defense at this time.

Allowed status:

- Keep as **provisional experimental defense plugin** for further investigation.

Blocked actions:

- Do not promote to canonical/default configs.
- Do not claim robustness improvement without teammate contract + improved downstream evidence.

## Recommended Next Actions

1. Obtain teammate wrapper contract details (normalization, timestep semantics, expected pre/post transforms).
2. Re-run the same battery with teammate-confirmed settings.
3. If still negative, treat checkpoint as incompatible for this detector/domain and halt integration.
