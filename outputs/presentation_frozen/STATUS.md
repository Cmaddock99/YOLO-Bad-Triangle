# Presentation Frozen Status

This directory is the fixed artifact snapshot for presentation assembly.

## Safe To Present

- `core_demo/`
  - Source bundle: `outputs/demo_audit/20260501T044919Z`
  - Use this to support the claim that the end-to-end benchmark pipeline runs and emits structured artifacts.

- `auto_cycle/`
  - Selected cycle bundle: `cycle_20260326_112654`
  - Use `auto_cycle/reports/`, `auto_cycle/summary/`, and `auto_cycle/history/selected_cycle.json` as the main cycle evidence.
  - `cycle_state.json` and `cycle_training_signal.json` now match the selected cycle.

- `patch/`
  - Imported patch evaluation runs and reports are frozen here.
  - Use this to support imported-patch benchmarking, placement-mode coverage, and validation-enabled mAP50 comparisons.

- `training/`
  - Signal-driven training artifacts for `cycle_20260326_112654` are frozen here.
  - Use `training_manifest.json`, `clean_gate_result.json`, and `attack_gate_result.json` to support the claim that the manual retraining workflow completed end-to-end.

## Caveats

- `training/` passed both repo gates only within the configured tolerance band.
  - Clean gate delta mAP50: `-0.003199`
  - Attack gate delta mAP50: `-0.001591`
  - Final verdict: `passed_both_manual_promotion_required`
  - Promotion is still manual; the baseline checkpoint has not been replaced.
