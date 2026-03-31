# Bad output examples

## 1) Declaring pass with failed comparability (invalid)

```json
{
  "skill": "parity-judge",
  "status": "pass",
  "inputs": {
    "legacy_root": "outputs/legacy_runs/a",
    "framework_root": "outputs/framework_runs/b",
    "tolerances": {
      "map50": 0.02
    }
  },
  "comparability": {
    "is_comparable": false,
    "issues": [
      "image counts differ and baseline is missing"
    ]
  },
  "metric_deltas": [],
  "artifact_mismatches": [],
  "likely_causes": []
}
```

Why invalid: when comparability fails, status must be `inconclusive`.

## 2) Guessing causes without evidence (invalid)

```json
{
  "skill": "parity-judge",
  "status": "fail",
  "inputs": {
    "legacy_root": "outputs/legacy_runs/a",
    "framework_root": "outputs/framework_runs/b",
    "tolerances": {
      "map50": 0.02
    }
  },
  "comparability": {
    "is_comparable": true,
    "issues": []
  },
  "metric_deltas": [],
  "artifact_mismatches": [],
  "likely_causes": [
    "GPU drift is definitely the reason."
  ]
}
```

Why invalid: no metric or mismatch evidence supports this cause.

## 3) Schema drift (invalid)

```json
{
  "skill": "parity-judge",
  "status": "fail",
  "inputs": {
    "legacy_root": "outputs/legacy_runs/a",
    "framework_root": "outputs/framework_runs/b",
    "tolerances": {
      "map50": 0.02
    }
  },
  "comparability": {
    "is_comparable": true,
    "issues": []
  },
  "delta_summary": "major drift",
  "likely_causes": []
}
```

Why invalid: `metric_deltas` and `artifact_mismatches` are required fields; `delta_summary` is not in schema.

## 4) Extra prose outside JSON (invalid)

Parity check complete. Here is the JSON:
{
  "skill": "parity-judge"
}

Why invalid: output must be JSON only and must match schema.
