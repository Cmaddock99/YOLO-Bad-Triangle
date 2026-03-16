# Week1 Live Demo Runbook

This is the canonical operator guide for your live team demo.

Use this runbook instead of piecing commands from multiple docs.

## 1) Demo intent

- Show end-to-end pipeline execution (preflight -> run -> checks -> artifacts).
- Show current baseline vs FGSM behavior.
- Keep a fallback path ready if runtime/environment issues happen.

## 2) One-time setup (before demo day)

From repo root:

- `./scripts/setup_env.sh`
- `./setup_assets.sh`
- `./.venv/bin/python scripts/check_environment.py`

## 3) Demo modes

- `demo` mode (recommended live): continues after FGSM-collapse sanity failure and prints warning.
- `strict` mode (engineering verification): aborts if FGSM sanity fails.

## 4) Live command sequence (primary path)

### Step A - Recommended presentation run (tuned FGSM eps range)

Use this tuned sweep for the clearest live trend on current environment
(`epsilon = 0.0005`, `0.006`, `0.01`):

- `./scripts/run_week1_stabilization.sh --profile week1-demo --mode demo`

### Step B - Reference stress-test run (original week1 matrix)

- `./scripts/run_week1_stabilization.sh --profile week1-stress --mode demo`

The script now:

1. runs preflight environment checks,
2. runs matrix experiments,
3. checks metrics integrity,
4. applies FGSM sanity gate (warn/continue in demo mode),
5. generates:
   - `metrics_summary.csv`
   - `experiment_table.md`
   - `plots/map50-by-attack.png`
   - `plots/precision-recall-by-attack.png`
   - `plots/baseline-vs-fgsm-metrics.png`
   - `plots/fgsm-epsilon-trend.png`
   - `plots/robustness-report-card.png`
   - `plots/robustness-report-card-by-epsilon.png`

## 5) Deterministic artifact command

If you already have a run folder and want to regenerate only visuals:

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/week1_<timestamp>`

Or by explicit CSV:

- `bash scripts/generate_week1_demo_artifacts.sh --csv outputs/week1_<timestamp>/metrics_summary.csv`

## 6) Runtime checkpoints (what to watch live)

- After preflight: all checks in `scripts/check_environment.py` must pass.
- After run: `metrics_summary.csv` exists with 4 rows (baseline + 3 FGSM by default matrix).
- After sanity: if fail in demo mode, continue and present as stress-test collapse.
- After plotting: all six plot PNGs are present under `<output_root>/plots`.

## 7) Fallback path (if live run fails)

Known-good baseline:

- `docs/WEEK1_DEMO_BASELINE.md`
- `outputs/demo-reference`

Fallback presentation command (regenerate plots if needed):

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/demo-reference`

## 8) Speaking track

- "This pipeline runs from config through attack/defense transforms, YOLO validation, and metric aggregation."
- "Baseline remains healthy; FGSM behavior depends strongly on epsilon regime."
- "Original week1 eps values act as a stress test and can collapse metrics."
- "Lower-epsilon probe is implemented, but on current runs it still collapses; fixing FGSM calibration/implementation is next."

## 9) 2-minute pre-meeting checklist

- Terminal open at repo root.
- `.venv` and assets already validated.
- One fallback output root ready (`outputs/demo-reference`).
- Runbook open.
- Latest command copied and ready to paste.

## 10) Rehearsal gate (timing + quality)

Run at least one full rehearsal before the meeting:

- `time ./scripts/run_week1_stabilization.sh --profile week1-demo --mode demo`

Expected runtime windows on current machine profile (CPU, 500-image subset):

- Preflight checks: `< 1 min`
- Matrix compute + validation: `8-12 min`
- Integrity + sanity + table/plot generation: `< 1 min`
- End-to-end total target: `9-12 min`

Most recent measured rehearsal:

- `docs/WEEK1_DEMO_REHEARSAL_LOG.md` (`real 574.15s`, `9m 34s`)

Hard gate for live readiness:

- `metrics_summary.csv` exists and has expected run count.
- `experiment_table.md` exists in same output root.
- All six plot files exist in `<output_root>/plots`.
- Script prints final output pointers without manual path hunting.

If any gate fails, switch to fallback presentation path:

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/demo-reference`
