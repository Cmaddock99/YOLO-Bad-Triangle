# Bad output examples

## 1) Mixed narrative output (invalid)

Looks mostly good, only a few issues.
{
  "skill": "artifact-contract-checker",
  "run_path": "outputs/framework_runs/x",
  "status": "pass",
  "required_files": {},
  "optional_files": [],
  "consistency_checks": [],
  "issues": [],
  "ready_for_analysis": true
}

Why invalid: output must be JSON only and required_files cannot be empty.

## 2) Ready-for-analysis contradiction (invalid)

```json
{
  "skill": "artifact-contract-checker",
  "run_path": "outputs/framework_runs/x",
  "status": "fail",
  "required_files": {
    "metrics.json": false,
    "predictions.jsonl": true,
    "run_summary.json": true
  },
  "optional_files": [],
  "consistency_checks": [],
  "issues": [
    {
      "severity": "fail",
      "type": "missing_required",
      "detail": "metrics.json missing."
    }
  ],
  "ready_for_analysis": true
}
```

Why invalid: missing required artifact with fail severity cannot be `ready_for_analysis: true`.

## 3) Guessing unseen files (invalid)

```json
{
  "skill": "artifact-contract-checker",
  "run_path": "outputs/framework_runs/x",
  "status": "pass",
  "required_files": {
    "metrics.json": true,
    "predictions.jsonl": true,
    "run_summary.json": true
  },
  "optional_files": [
    {
      "path": "outputs/framework_runs/x/fingerprint.json",
      "present": true
    }
  ],
  "consistency_checks": [],
  "issues": [],
  "ready_for_analysis": true
}
```

Why invalid: optional file presence cannot be asserted without direct evidence.

## 4) Schema drift (invalid)

```json
{
  "skill": "artifact-contract-checker",
  "run_path": "outputs/framework_runs/x",
  "status": "warn",
  "required_files": {
    "metrics.json": true
  },
  "optional_files": [],
  "checks": [],
  "issues": [],
  "ready_for_analysis": true
}
```

Why invalid: `consistency_checks` is required; `checks` is not a valid schema key.
