# cycle-forensics reference

## Canonical input paths

- `outputs/cycle_history/<cycle_id>.json` — primary source; newest file = latest cycle
- `outputs/cycle_state.json` — current phase, active run, top_attacks, top_defenses
- `outputs/eval_ab_*.json` — checkpoint A/B evaluation context (may not exist)

## Metric formulas (mAP50 only — not confidence, not detection count)

```
damage_pct  = (baseline_mAP50 - attack_mAP50) / baseline_mAP50 * 100
recovery_pct = (defended_mAP50 - attack_mAP50) / (baseline_mAP50 - attack_mAP50) * 100
```

- Negative `recovery_pct` is valid and must be reported — defense is making things worse.
- Use only `validate_*` rows from Phase 4 `validation_results`. Do not use Phase 1/2 smoke run values.
- `validate_baseline` provides `baseline_mAP50`.
- `validate_atk_<attack>` provides `attack_mAP50`.
- `validate_<attack>_<defense>` provides `defended_mAP50`.

## Reference values (cycle_20260329_125124)

| attack | mAP50 (Phase 4) | damage_pct | image_count |
|---|---|---|---|
| baseline | 0.600 | — | 500 |
| deepfool | 0.218 | 63.6% | 500 |
| dispersion_reduction | 0.238 | 60.3% | 50 |
| square | 0.363 | 39.5% | 50 |

| attack | defense | defended_mAP50 | recovery_pct |
|---|---|---|---|
| square | c_dog | 0.389 | +11.0% |
| square | bit_depth | 0.386 | +9.8% |
| square | jpeg_preprocess | 0.377 | +5.8% |
| dispersion_reduction | c_dog | 0.263 | +7.0% |
| dispersion_reduction | bit_depth | 0.232 | -1.7% |
| dispersion_reduction | jpeg_preprocess | 0.201 | -10.1% |
| deepfool | c_dog | 0.240 | +5.7% |
| deepfool | bit_depth | 0.223 | +1.2% |
| deepfool | jpeg_preprocess | 0.166 | -13.6% |

## Anomaly classes

- `missing_pair`: a baseline, attack-only, or attack+defense row is absent — pair cannot be computed.
- `image_count_mismatch`: rows being compared used different image counts — mAP50 values are not directly comparable. In cycle_20260329_125124, square and dispersion_reduction ran at 50 images vs 500 for baseline and deepfool.
- `negative_recovery`: `recovery_pct < 0` — the defense made mAP50 worse under attack than no defense.
- `param_bound_hit`: a tuned parameter converged at its configured min or max — search space may be too narrow. In cycle_20260329_125124, square eps=0.3 equals the configured maximum.
- `conditional_ab_eval`: A/B checkpoint comparison completed only for attacked conditions; clean (no-attack) baseline A/B not yet run. Full deployment readiness cannot be confirmed.
- `missing_data`: a field expected in the cycle history JSON is absent or null.
- `outlier_shift`: a metric jump within the cycle that is unsupported by nearby runs.

## Status guidance

- `ok`: all required pairs present; no comparability-breaking anomalies; rankings are reliable.
- `partial`: usable but not fully comparable (e.g., image count mismatches, one missing pair).
- `insufficient_data`: cannot produce meaningful rankings from available evidence.

## auto_summary false-positive warning

`warnings.json` produced by `generate_auto_summary.py` may contain false-positive `NO_VALIDATION` and `DEFENSE_DEGRADES_PERFORMANCE` entries. Root cause: Phase 1 smoke runs are processed before Phase 4 `validate_*` runs and may shadow them. Do not propagate these warnings without verifying the source row in `validation_results`.

## Notes

- Read-only. Do not execute experiments or modify files.
- Do not infer missing evidence; record unknowns explicitly in JSON fields.
- Do not claim causal explanations unsupported by artifacts.
