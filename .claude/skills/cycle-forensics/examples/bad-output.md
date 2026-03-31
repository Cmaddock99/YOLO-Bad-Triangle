# Bad output examples

## 1) Extra prose outside JSON (invalid)

This cycle looked great overall.
{
  "skill": "cycle-forensics",
  "cycle_path": "outputs/framework_reports/20260330_091500",
  "status": "ok",
  "rankings": {
    "attack_damage": [],
    "defense_recovery": []
  },
  "anomalies": [],
  "highlights": []
}

## 2) Guessing missing evidence (invalid)

```json
{
  "skill": "cycle-forensics",
  "cycle_path": "outputs/framework_reports/unknown",
  "status": "ok",
  "rankings": {
    "attack_damage": [
      {
        "attack": "new_attack",
        "damage_pct": 75.0
      }
    ],
    "defense_recovery": []
  },
  "anomalies": [],
  "highlights": [
    "new_attack is definitely strongest even though rows were missing."
  ]
}
```

Why invalid: claims confidence while admitting missing rows; must use `partial` or `insufficient_data`.

## 3) Schema drift (invalid)

```json
{
  "skill": "cycle-forensics",
  "path": "outputs/framework_reports/20260330_091500",
  "status": "ok",
  "top_attack": "deepfool"
}
```

Why invalid: required keys are missing and non-schema keys are added.
