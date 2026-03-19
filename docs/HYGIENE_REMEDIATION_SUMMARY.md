# Hygiene Remediation Summary

This summary captures the completed risk-phased hygiene remediation pass.

## 1) Before/After Risk Table

| Area | Before | After | Evidence |
|---|---|---|---|
| Documentation onboarding and consistency | Medium risk (no single top-level onboarding path, drift risk across docs) | Low risk (canonical `README.md`, metadata stamps, doc cross-linking) | `README.md`, `PROJECT_STATE.md`, `READINESS_REPORT.md`, `scripts/demo/README.md` |
| Reporting baseline selection | High risk (team summary baseline could match `attack=none` but defended rows) | Low risk (baseline requires none-like attack and none-like defense) | `src/lab/reporting/team_summary.py`, `tests/test_framework_reporting.py` |
| None-like name normalization across reporting/CLI | High risk (inconsistent handling of `none`/`identity`/empty) | Low risk (shared normalization helper used across modules) | `src/lab/reporting/name_normalization.py`, `scripts/print_summary.py`, `src/lab/reporting/framework_comparison.py` |
| Missing-data interpretation messaging | Medium risk (could imply robustness with insufficient metrics) | Low risk (explicit insufficient-data interpretation) | `src/lab/reporting/experiment_summary.py`, `tests/test_framework_reporting.py` |
| JSON read error handling in core/reporting paths | High risk (broad exception swallowing) | Medium risk (typed exceptions and explicit warnings/errors in key paths) | `src/lab/runners/run_experiment.py`, `src/lab/reporting/framework_comparison.py` |
| CLI failure ergonomics | Medium risk (uncaught tracebacks for common operator errors) | Low risk (top-level error wrappers in key scripts) | `src/lab/runners/run_experiment.py`, `scripts/sweep_and_report.py`, `scripts/run_overnight_stress.py` |
| Destructive overwrite behavior in legacy runner | High risk (implicit cleanup always allowed) | Medium risk (config-controlled safety via `clean_existing_runs`, default kept for compatibility) | `src/lab/runners/experiment_runner.py`, `tests/test_runner_validation_dataset.py` |
| Regression confidence after changes | Medium risk | Low risk (targeted + full-suite + e2e checks all passed) | test and smoke commands below |

## 2) Exact Verification Commands

Run from repo root.

### A. Targeted reporting and normalization tests

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_framework_reporting.py'
```

### B. Framework/reporting smoke path

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --preset smoke \
  --attacks fgsm \
  --runs-root outputs/hygiene_phaseB_runs \
  --report-root outputs/hygiene_phaseB_reports
```

Validate generated team summary artifacts:

```bash
python - <<'PY'
import json
from pathlib import Path
root = Path("outputs/hygiene_phaseB_reports")
payload = json.loads((root / "team_summary.json").read_text(encoding="utf-8"))
print("keys:", sorted(payload.keys()))
print("md_nonempty:", bool((root / "team_summary.md").read_text(encoding="utf-8").strip()))
PY
```

### C. Full regression suite

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

### D. Legacy and framework command-path smoke checks

```bash
./.venv/bin/python run_experiment.py --list-attacks
```

```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set runner.output_root=outputs/hygiene_phaseC_framework \
  --set runner.run_name=framework_phaseC_smoke \
  --set runner.max_images=4 \
  --set attack.name=blur \
  --set validation.enabled=false \
  --set summary.enabled=false
```

### E. Overnight orchestrator dry-run check

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_overnight_stress.py \
  --dry-run \
  --window-hours 1 \
  --resume \
  --runs-root outputs/hygiene_phaseC_overnight_runs \
  --report-root outputs/hygiene_phaseC_overnight_reports
```

### F. Demo path smoke check

```bash
bash scripts/demo/run_demo_package.sh fast --profile week1-demo
```

### G. Contract/checkup quick script

```bash
python - <<'PY'
import csv, json
from pathlib import Path
root = Path(".")
checks = []
legacy_csv = root / "outputs/metrics_summary.csv"
checks.append(("legacy_csv_exists", legacy_csv.is_file()))
if legacy_csv.is_file():
    with legacy_csv.open(newline="", encoding="utf-8") as f:
        fields = set(next(csv.reader(f), []))
    req = {"run_name", "attack", "defense", "images_with_detections", "total_detections"}
    checks.append(("legacy_csv_required_cols", req.issubset(fields)))

phaseb = root / "outputs/hygiene_phaseB_reports"
for name in ["framework_run_summary.csv", "framework_run_report.md", "team_summary.json", "team_summary.md"]:
    checks.append((f"phaseB_{name}", (phaseb / name).is_file()))

phasec_metric = root / "outputs/hygiene_phaseC_framework/framework_phaseC_smoke/metrics.json"
checks.append(("phaseC_framework_metrics", phasec_metric.is_file()))

overnight_status = root / "outputs/overnight_stress_reports/overnight_status.json"
if overnight_status.is_file():
    status = json.loads(overnight_status.read_text(encoding="utf-8"))
    checks.append(("overnight_completed_clean", status.get("final_status") == "completed_clean"))

overall = True
for name, ok in checks:
    overall = overall and ok
    print(name, "PASS" if ok else "FAIL")
print("OVERALL", "PASS" if overall else "FAIL")
PY
```

## 3) Weekly Monitoring Checklist

Use this once per week (or before major demo/release windows).

### Code and test health

- [ ] Run full test suite (`unittest discover`) and confirm green.
- [ ] Run targeted reporting tests (`test_framework_reporting.py`).
- [ ] Confirm no new broad `except Exception` in operational paths.

### Runtime and contracts

- [ ] Run framework smoke (`run_experiment.py` unified path).
- [ ] Run sweep/report smoke (`sweep_and_report.py --preset smoke`).
- [ ] Validate output artifacts exist and parse:
  - `framework_run_summary.csv`
  - `framework_run_report.md`
  - `team_summary.json`
  - `team_summary.md`
- [ ] Confirm legacy CSV contract still intact (`outputs/metrics_summary.csv` columns).

### Operational readiness

- [ ] Run `scripts/check_environment.py`.
- [ ] Run demo fast package (`run_demo_package.sh fast --profile week1-demo`).
- [ ] Run overnight orchestrator in dry-run mode and confirm status/summary outputs.

### Documentation hygiene

- [ ] Confirm `README.md` command examples still match current script flags.
- [ ] Refresh metadata stamps (`validated_at_utc`, `validated_against_commit`) in state/readiness docs.
- [ ] Ensure docs point to canonical sources and remove stale duplicated statements.

