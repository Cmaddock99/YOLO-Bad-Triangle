# Bad output examples

## 1) Mixed prose + JSON (invalid)

Top recommendation: run deepfool right away.

```json
{
  "skill": "experiment-planner",
  "status": "ok",
  "planning_basis": {
    "source_path": "outputs/cycle_history/cycle_20260329_125124.json",
    "budget": "max_runs=3",
    "allowed_attacks": ["deepfool"],
    "allowed_defenses": ["c_dog"]
  },
  "queue": [],
  "blocked_by": []
}
```

Why invalid: output must be JSON only; no prose before or after the JSON block.

## 2) Recommending from non-comparable evidence (invalid)

```json
{
  "skill": "experiment-planner",
  "status": "ok",
  "planning_basis": {
    "source_path": "outputs/framework_reports/unknown",
    "budget": "max_runs=5",
    "allowed_attacks": ["deepfool"],
    "allowed_defenses": ["c_dog"]
  },
  "queue": [
    {
      "priority": 1,
      "run_name_hint": "yolo26n__deepfool__c_dog",
      "params": {
        "attack": "deepfool",
        "defense": "c_dog",
        "runner.max_images": 0,
        "validation.enabled": true
      },
      "expected_value": "Guaranteed big gain.",
      "cost_estimate": "low",
      "stop_condition": "Never stop.",
      "risk_note": "None."
    }
  ],
  "blocked_by": []
}
```

Why invalid: evidence path is `unknown` and does not exist; comparability gate not applied; recommendation is overconfident; `cost_estimate: "low"` for a full 500-image deepfool run is wrong (deepfool is ~30s/image = ~4h).

## 3) Skipping the clean validation blocker (invalid)

```json
{
  "skill": "experiment-planner",
  "status": "ok",
  "planning_basis": {
    "source_path": "outputs/cycle_history/cycle_20260329_125124.json",
    "budget": "max_runs=4",
    "allowed_attacks": ["deepfool", "square"],
    "allowed_defenses": ["c_dog"]
  },
  "queue": [
    {
      "priority": 1,
      "run_name_hint": "yolo26n__deepfool__c_dog__eps015",
      "params": {
        "attack": "deepfool",
        "defense": "c_dog",
        "attack.params.epsilon": 0.15,
        "runner.max_images": 500,
        "validation.enabled": true
      },
      "expected_value": "Extend deepfool coverage to harder epsilon.",
      "cost_estimate": "high",
      "stop_condition": "Stop if mAP50 falls below 0.10.",
      "risk_note": "None."
    }
  ],
  "blocked_by": []
}
```

Why invalid: the finetuned checkpoint has a CONDITIONAL PASS — clean (no-attack) baseline A/B is the highest-value pending experiment. Skipping it and going straight to extended attack coverage is incorrect prioritization. Priority 1 must be the clean validation run until that gap is resolved.

## 4) Schema drift (invalid)

```json
{
  "skill": "experiment-planner",
  "plan": [
    "do something"
  ]
}
```

Why invalid: missing all required keys (`status`, `planning_basis`, `queue`, `blocked_by`); `plan` is not a valid schema key.
