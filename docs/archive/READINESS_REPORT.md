# Full Repo Readiness Report

## Report Metadata

- `validated_at_utc`: `2026-03-19T17:55:15Z`
- `validated_against_commit`: `4a11a17`
- `scope_note`: readiness snapshot for completed gate + overnight stress run evidence

## Verdict

**GO with caveats** for demo readiness.

- Core health is green across legacy, framework, and demo paths.
- Full-size stress chain is operational but slow enough that an overnight window is required.
- Post-stress smoke checks remain stable.

## Scope Covered

- Legacy runner and matrix flows.
- Framework unified runner, sweep/report flow, and team summary export.
- Demo-facing package commands and artifact generation path.

## Evidence Snapshot

### Phase 1: Baseline Integrity Audit

- Inventory and compatibility map captured in `PROJECT_STATE.md`.
- Entrypoints verified:
  - `run_experiment.py`
  - `scripts/run_framework.py`
  - `src/lab/runners/run_experiment.py`
  - `scripts/demo/run_demo_package.sh`

### Phase 2: Static + Contract Validation

- Full tests passed: `python -m unittest discover -s tests -p 'test_*.py'`
  - Snapshot result at validation time: `Ran 66 tests ... OK`
- Contract checks verified:
  - Legacy: `outputs/metrics_summary.csv` has required columns and rows.
  - Framework per-run: `metrics.json`, `predictions.jsonl`, `run_summary.json`.
  - Reporting: summary CSV/MD and team summary JSON/MD in readiness report roots.

### Phase 3: End-to-End Functional Verification

- Legacy one-run smoke output:
  - `outputs/readiness_legacy/yolo26_legacy_smoke_readiness`
- Legacy matrix output:
  - `outputs/readiness_matrix/metrics_summary.csv`
- Framework one-run smoke output:
  - `outputs/readiness_framework/framework_smoke_readiness/metrics.json`
  - `outputs/readiness_framework/framework_smoke_readiness/predictions.jsonl`
- Framework sweep/report/team outputs:
  - `outputs/readiness_framework_reports/framework_run_summary.csv`
  - `outputs/readiness_framework_reports/framework_run_report.md`
  - `outputs/readiness_framework_reports/team_summary.json`
  - `outputs/readiness_framework_reports/team_summary.md`
- Demo package fast path output:
  - `outputs/demo-reference/metrics_summary.csv`
  - `outputs/demo-reference/plots/robustness-report-card.png`

### Phase 4: Maximal Stress + Recovery

- Long-run stress started in:
  - `outputs/readiness_stress_runs`
  - `outputs/readiness_stress_reports`
- Observed behavior:
  - Baseline full pass completed (500 images).
  - Heavy attack phases progressed slowly (expected long-clock workload).
- Post-stress smoke checks passed:
  - framework short smoke run in `outputs/readiness_post_stress`
  - legacy compatibility listing command
  - environment preflight

## Known Risks (Ranked)

### High Risk

- **Wall-clock duration for full stress chain** can exceed regular session windows.
  - Mitigation: run overnight with timeout + resume + heartbeat monitoring.

### Medium Risk

- `scripts/demo/run_demo_package.sh fast --profile custom` may fail if the selected CSV lacks required FGSM rows.
  - Mitigation: use `--profile week1-demo` for deterministic demo package behavior.

### Low Risk

- Older report directories may not include newer additive artifacts (`team_summary.json`, `team_summary.md`).
  - Mitigation: regenerate reports with current scripts.

## Demo Runbook

### Primary (recommended)

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --preset smoke \
  --attacks fgsm,pgd \
  --runs-root outputs/demo_ready_runs \
  --report-root outputs/demo_ready_reports

bash scripts/demo/run_demo_package.sh fast --profile week1-demo
```

### Fallback (quickest confidence check)

```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/default.yaml \
  --set runner.max_images=8 \
  --set attack.name=blur \
  --set validation.enabled=false

PYTHONPATH=src ./.venv/bin/python scripts/print_summary.py \
  --auto \
  --runs-root outputs/demo_ready_runs
```

## Overnight Stress Command (Long Clock Window)

Use the orchestrated runner for timeout, heartbeat, checkpoint/resume, artifact checks, and post-stress smoke:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_overnight_stress.py \
  --window-hours 10 \
  --resume \
  --runs-root outputs/overnight_stress_runs \
  --report-root outputs/overnight_stress_reports
```

Morning outputs:
- `outputs/overnight_stress_reports/overnight_status.json`
- `outputs/overnight_stress_reports/overnight_heartbeat.jsonl`
- `outputs/overnight_stress_reports/overnight_summary.md`
- `outputs/overnight_stress_reports/overnight_stress.log`

