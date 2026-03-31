# Bad output examples

## 1) Extra prose outside JSON (invalid)

This cycle looked great overall.
{
  "skill": "cycle-forensics",
  "cycle_path": "outputs/cycle_history/cycle_20260329_125124.json",
  "status": "ok",
  "rankings": {
    "attack_damage": [],
    "defense_recovery": []
  },
  "anomalies": [],
  "highlights": []
}

Why invalid: output must be JSON only; no prose before or after the JSON block.

## 2) Guessing missing evidence (invalid)

```json
{
  "skill": "cycle-forensics",
  "cycle_path": "outputs/cycle_history/unknown",
  "status": "ok",
  "rankings": {
    "attack_damage": [
      {
        "attack": "square",
        "damage_pct": 75.0
      }
    ],
    "defense_recovery": []
  },
  "anomalies": [],
  "highlights": [
    "square is strongest even though some rows were missing."
  ]
}
```

Why invalid: claims `ok` status and asserts confidence despite missing evidence; must use `partial` or `insufficient_data` and report `missing_pair` anomalies.

## 3) Schema drift (invalid)

```json
{
  "skill": "cycle-forensics",
  "path": "outputs/cycle_history/cycle_20260329_125124.json",
  "status": "ok",
  "top_attack": "deepfool"
}
```

Why invalid: required keys `cycle_path`, `rankings`, `anomalies`, `highlights` are missing; `path` and `top_attack` are not in schema.

## 4) Overclaiming deployment readiness from attacked-only A/B eval (invalid)

```json
{
  "skill": "cycle-forensics",
  "cycle_path": "outputs/cycle_history/cycle_20260329_125124.json",
  "status": "ok",
  "checkpoint_context": {
    "ab_eval_present": true,
    "clean_validation_present": false,
    "deployment_status": "pass"
  },
  "rankings": {
    "attack_damage": [
      { "attack": "deepfool", "damage_pct": 63.6 }
    ],
    "defense_recovery": [
      { "attack": "deepfool", "defense": "c_dog", "recovery_pct": 5.7 }
    ]
  },
  "anomalies": [],
  "highlights": [
    "Finetuned checkpoint passes A/B eval — ready to deploy."
  ]
}
```

Why invalid: `deployment_status: "pass"` and "ready to deploy" are overclaims. The A/B eval covered only attacked conditions (deepfool, square at Phase 4 params). Clean (no-attack) baseline validation of the finetuned checkpoint has not been run. `deployment_status` must be `"conditional_pass"` and a `conditional_ab_eval` anomaly must be present until clean validation completes.
