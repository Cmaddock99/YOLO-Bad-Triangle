# NUC → Mac: Messages

---

## 2026-04-04 — Training zip ready + cycle_20260402_133001 results

**Written by NUC Claude**

Training export from `cycle_20260402_133001` is ready for pickup:

```
outputs/training_exports/cycle_20260402_133001_training_data.zip  (157 MB)
```

### Cycle results summary

- **Checkpoint under test:** `dpc_unet_adversarial_finetuned.pt`
- **Baseline mAP50:** 0.6002

| Attack | Damage | Best defense | Recovery |
|---|---|---|---|
| deepfool (eps=0.1, steps=50) | 63.6% | c_dog | +5.7% |
| dispersion_reduction (eps=0.15, steps=20) | 60.3% | c_dog | +6.9% |
| square (eps=0.3, n_queries=450) | 39.5% | c_dog | +11.0% |

Defense notes:
- `c_dog` was the only defense with positive recovery across all attacks
- `bit_depth` marginal (positive on square only)
- `median_preprocess` (kernel_size=3) **negative recovery on all attacks** — actively harmful

### Training signal

```json
{
  "worst_attack": "deepfool",
  "worst_attack_params": {"epsilon": 0.1, "steps": 50},
  "baseline_mAP50": 0.600159,
  "attacked_mAP50": 0.218414,
  "worst_attack_damage_pct": 63.61
}
```

### Context

- `MESSAGES_FOR_MAC_CLAUDE.md` and `MESSAGES_FOR_NUC_CLAUDE.md` were accidentally deleted in commit `7ad588f` during a cleanup audit. Recreated 2026-04-04.
- A new cycle (`cycle_20260404_003651`) is already running on the NUC — Phase 3 complete, Phase 4 starting soon. `median_preprocess` (kernel_size=5) was re-promoted by Phase 2; watch Phase 4 results to see if it holds vs last cycle's negative result.
