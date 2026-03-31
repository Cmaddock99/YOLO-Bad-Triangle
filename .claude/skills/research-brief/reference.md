# research-brief reference

## Metric formulas (same as cycle-forensics)

```
damage_pct   = (baseline_mAP50 - attack_mAP50) / baseline_mAP50 * 100
recovery_pct = (defended_mAP50 - attack_mAP50) / (baseline_mAP50 - attack_mAP50) * 100
```

Use Phase 4 `validate_*` rows only. Phase 1/2 smoke runs are not comparable.

## Cross-cycle trend guidance

- A trend requires at least 2 data points. With 1 cycle, write `"insufficient data for trend"`.
- Param trajectories: compare `best_attack_params` across cycles. If the same param is at its bound across multiple cycles, flag it.
- Recovery trends: if a defense is consistently recovering less than 5% across cycles, that is a real signal.
- Baseline drift: if `validate_baseline` mAP50 is shifting cycle-over-cycle, note it — may indicate dataset or model config changes.

## Checkpoint status

- `outputs/eval_ab_clean.json` — written by `evaluate_checkpoint.py --attack none`. Contains `delta_mAP50` and `verdict` for the clean (no-attack) A/B comparison.
- If absent: `clean_validation_complete: false`, `deployment_recommendation: "not_evaluated"`.
- If present and `delta_mAP50 >= -0.001`: `deployment_recommendation: "deploy"`.
- If present and `delta_mAP50 < -0.001`: `deployment_recommendation: "do_not_deploy"`.
- Do not recommend deployment based on attacked-only A/B results — those are CONDITIONAL PASS only.

## recommended_next priority order

1. Clean checkpoint A/B if not yet done (highest priority until resolved)
2. Resolve image count mismatches (run slow attacks at full 500 images)
3. Expand search bounds for any attack hitting a param boundary
4. Deepen the best-performing attack×defense pair
5. Any attack or defense with consistently anomalous results worth investigating

## Status guidance

- `ok`: at least 3 cycles with complete Phase 4 validation; checkpoint status known.
- `partial`: fewer than 3 complete cycles, or missing Phase 4 data in some cycles.
- `insufficient_data`: fewer than 2 cycles, or no Phase 4 validation data at all.
