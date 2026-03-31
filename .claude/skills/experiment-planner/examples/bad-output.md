# Bad output examples

## 1) Mixed prose + JSON (invalid)

Top recommendation: run deepfool right away.

```json
{
  "skill": "experiment-planner",
  "status": "ok",
  "planning_basis": {
    "source_path": "outputs/framework_reports/20260330_091500",
    "budget": "max_runs=3",
    "allowed_attacks": ["fgsm"],
    "allowed_defenses": ["c_dog"]
  },
  "queue": [],
  "blocked_by": []
}
```

Why invalid: output must be JSON only.

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

Why invalid: evidence path unknown and recommendation is overconfident despite no comparability gate.

## 3) Guessing missing evidence (invalid)

```json
{
  "skill": "experiment-planner",
  "status": "ok",
  "planning_basis": {
    "source_path": "outputs/framework_reports/unknown_cycle",
    "budget": "max_runs=4",
    "allowed_attacks": ["fgsm"],
    "allowed_defenses": ["c_dog"]
  },
  "queue": [
    {
      "priority": 1,
      "run_name_hint": "yolo26n__fgsm__c_dog",
      "params": {
        "attack": "fgsm",
        "defense": "c_dog",
        "runner.max_images": 500,
        "validation.enabled": true
      },
      "expected_value": "Guaranteed recovery jump based on likely trend.",
      "cost_estimate": "medium",
      "stop_condition": "Stop only if GPU fails.",
      "risk_note": "No risk."
    }
  ],
  "blocked_by": []
}
```

Why invalid: this guesses outcomes despite missing reliable evidence and no blocker signaling.

## 4) Schema drift (invalid)

```json
{
  "skill": "experiment-planner",
  "plan": [
    "do something"
  ]
}
```

Why invalid: missing required keys and wrong structure.
