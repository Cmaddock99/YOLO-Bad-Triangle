# YOLO-Bad-Triangle

Repository for adversarial robustness experimentation with two maintained execution paths:

- **Legacy path** for demo-critical week1/operator flows.
- **Framework path** for modular runs, JSON artifacts, and reporting.

This guide is the primary onboarding entrypoint for running, validating, and reviewing the project safely.

## Document Metadata

- `validated_at_utc`: `2026-03-19T17:55:15Z`
- `validated_against_commit`: `4a11a17`
- `scope_note`: operational onboarding + command surface overview, not a design-spec replacement

## 1) Environment Setup

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quick environment check:

```bash
./.venv/bin/python scripts/check_environment.py
```

## 2) Fast Start Commands

### Legacy compatibility smoke

```bash
./.venv/bin/python run_experiment.py --list-attacks
```

### Framework one-run smoke

```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set runner.run_name=framework_smoke \
  --set attack.name=blur \
  --set validation.enabled=false \
  --set runner.max_images=8
```

### Framework sweep + reporting smoke

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --preset smoke \
  --attacks fgsm,pgd \
  --runs-root outputs/demo_ready_runs \
  --report-root outputs/demo_ready_reports
```

## 3) Output Contracts

### Legacy path outputs

- `outputs/metrics_summary.csv`
- `outputs/experiment_table.md`
- `outputs/<run_name>/...` (labels/artifacts, optional validation outputs)

### Framework path outputs

- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/run_summary.json`
- Optional additive artifacts:
  - `parity_report.json`
  - `experiment_summary.json`

### Framework reporting outputs

- `framework_run_summary.csv`
- `framework_run_report.md`
- `team_summary.json`
- `team_summary.md`

## 4) Validation and Quality Gates

Run full automated tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Recommended demo preflight:

```bash
bash scripts/demo/run_demo_package.sh fast --profile week1-demo
```

## 5) Overnight Stress Run

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_overnight_stress.py \
  --window-hours 10 \
  --resume \
  --runs-root outputs/overnight_stress_runs \
  --report-root outputs/overnight_stress_reports
```

Monitor commands:

```bash
tail -f outputs/overnight_stress_reports/overnight_heartbeat.jsonl
tail -f outputs/overnight_stress_reports/overnight_stress.log
python -m json.tool outputs/overnight_stress_reports/overnight_status.json
```

## 6) Documentation Index

- Project state and architecture: `PROJECT_STATE.md`
- Readiness result snapshot: `READINESS_REPORT.md`
- Demo script package usage: `scripts/demo/README.md`
- Hygiene review checklist and findings: `docs/REPO_HYGIENE_CHECKLIST.md`, `docs/REPO_HYGIENE_REVIEW.md`
- Additional reports and runbooks: `docs/`

## 7) Recommended Operator Path

- Use **legacy scripts** for week1 demo-critical rehearsals.
- Use **framework runner + sweep/report scripts** for modular robustness analysis.
- Keep changes additive and avoid modifying legacy behavior unless explicitly intended.

