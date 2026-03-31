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

Why invalid: output must be JSON only; `required_files` cannot be empty — all three required files must be checked.

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

Why invalid: a missing required artifact with `fail` severity cannot coexist with `ready_for_analysis: true`.

## 3) Guessing unseen optional files (invalid)

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
      "path": "outputs/eval_ab_deepfool.json",
      "present": true
    }
  ],
  "consistency_checks": [],
  "issues": [],
  "ready_for_analysis": true
}
```

Why invalid: optional file presence cannot be asserted without direct Glob or Read evidence. If the file was not confirmed to exist, `present` must be `false` or the entry omitted.

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

## 5) Suppressing the clean validation gap for a deployment context (invalid)

```json
{
  "skill": "artifact-contract-checker",
  "run_path": "outputs/framework_runs/yolo26n__deepfool__c_dog",
  "status": "pass",
  "required_files": {
    "metrics.json": true,
    "predictions.jsonl": true,
    "run_summary.json": true
  },
  "optional_files": [],
  "consistency_checks": [
    {
      "name": "prediction_count_alignment",
      "result": "pass",
      "detail": "Counts align."
    }
  ],
  "issues": [],
  "ready_for_analysis": true
}
```

Why invalid: if this artifact set is being reviewed ahead of a deployment decision and A/B eval context is known (CONDITIONAL PASS on finetuned checkpoint), the clean validation gap must appear as a `warn`-level issue. Returning `status: "pass"` with no caveats misleads downstream deployment reasoning. The `clean_validation_present` consistency check must be included and its absence flagged.
