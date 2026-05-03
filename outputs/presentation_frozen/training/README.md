# Frozen Training Snapshot

This directory contains the current signal-driven training outcome for `cycle_20260326_112654`.

- `training_manifest.json`
  - Canonical verdict and artifact metadata for the run.
- `clean_gate_result.json`
  - Baseline-vs-candidate A/B result on clean `c_dog` evaluation.
- `attack_gate_result.json`
  - Baseline-vs-candidate A/B result on `deepfool + c_dog`.

Important:

- Both gates passed only within the repo's configured `-0.005` mAP50 tolerance band.
- The candidate checkpoint was not auto-promoted.
- Manual promotion is required if you decide to replace `dpc_unet_adversarial_finetuned.pt`.
