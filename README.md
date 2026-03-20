# YOLO-Bad-Triangle

Repository for adversarial robustness experimentation with a framework-first execution path:

- **Framework path** for modular runs, JSON artifacts, and reporting.
- **Legacy runtime** is rollback-only and disabled by default (`USE_LEGACY_RUNTIME=false`).

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

### Framework compatibility smoke

```bash
./.venv/bin/python run_experiment.py --list-attacks
```

### Framework one-run smoke (canonical)

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/lab_framework_phase5.yaml \
  --set runner.run_name=framework_smoke \
  --set attack.name=blur \
  --set validation.enabled=false \
  --set runner.max_images=8
```

> **Advanced / low-level:** You can also invoke the runner directly via
> `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --config ...`
> but `scripts/run_unified.py run-one` is the preferred entry for all new work.

### Framework sweep + reporting smoke

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --preset smoke \
  --attacks fgsm,pgd \
  --runs-root outputs/demo_ready_runs \
  --report-root outputs/demo_ready_reports \
  --legacy-output-root outputs/demo_ready_compat
```

### Unified wrapper surface (framework-first)

```bash
./.venv/bin/python scripts/run_unified.py sweep --attacks fgsm,pgd
```

### Reproducible teammate defense matrix (`c_dog`)

Use a consistent output layout and run naming convention so all teammate defense tests are comparable:

- Output root: `outputs/defense_eval`
- Run name format: `<model>__<attack>__<defense>`
- Models:
  - YOLOv8: `yolov8n.pt`
  - YOLO26: `yolo26n.pt`

Baseline vs `c_dog` (no attack):

```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set model.params.model=yolov8n.pt \
  --set attack.name=none \
  --set defense.name=none \
  --set runner.output_root=outputs/defense_eval \
  --set runner.run_name=yolov8n__none__none

PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set model.params.model=yolov8n.pt \
  --set attack.name=none \
  --set defense.name=c_dog \
  --set defense.params.checkpoint_path=/Users/lurch/Downloads/dpc_unet_final_golden.pt \
  --set defense.params.timestep=50 \
  --set defense.params.color_order=bgr \
  --set defense.params.scaling=zero_one \
  --set defense.params.normalize=true \
  --set defense.params.device=cpu \
  --set runner.output_root=outputs/defense_eval \
  --set runner.run_name=yolov8n__none__c_dog

PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set model.params.model=yolo26n.pt \
  --set attack.name=none \
  --set defense.name=none \
  --set runner.output_root=outputs/defense_eval \
  --set runner.run_name=yolo26n__none__none

PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set model.params.model=yolo26n.pt \
  --set attack.name=none \
  --set defense.name=c_dog \
  --set defense.params.checkpoint_path=/Users/lurch/Downloads/dpc_unet_final_golden.pt \
  --set defense.params.timestep=50 \
  --set defense.params.color_order=bgr \
  --set defense.params.scaling=zero_one \
  --set defense.params.normalize=true \
  --set defense.params.device=cpu \
  --set runner.output_root=outputs/defense_eval \
  --set runner.run_name=yolo26n__none__c_dog
```

Optional attack extension (repeat per model):

```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
  --set model.params.model=yolo26n.pt \
  --set attack.name=fgsm \
  --set defense.name=c_dog \
  --set defense.params.checkpoint_path=/Users/lurch/Downloads/dpc_unet_final_golden.pt \
  --set defense.params.timestep=50 \
  --set defense.params.color_order=bgr \
  --set defense.params.scaling=zero_one \
  --set defense.params.normalize=true \
  --set defense.params.device=cpu \
  --set runner.output_root=outputs/defense_eval \
  --set runner.run_name=yolo26n__fgsm__c_dog
```

Interpretation checklist for teammate defense modules:

- `Clean impact`: compare `<model>__none__none` vs `<model>__none__<defense>`; reject if clean detection quality drops materially.
- `Attack recovery`: compare `<model>__<attack>__none` vs `<model>__<attack>__<defense>`; require measurable recovery in detections/confidence.
- `Cross-model consistency`: require directionally similar behavior on YOLOv8 and YOLO26 before broader rollout.
- `Stability`: confirm no non-finite outputs, shape changes, or run-time errors in `metrics.json` and `run_summary.json`.
- `Decision rule`: mark defense `GO` only if clean degradation is acceptable and attack recovery is consistent on both model families.

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
- optional strict legacy-compatible views from framework runs:
  - `metrics_summary.csv`
  - `experiment_table.md`

## 4) Validation and Quality Gates

Run full automated tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Recommended demo preflight:

```bash
bash scripts/demo/run_demo_package.sh fast --profile week1-demo
```

### Demo Profile Behavior

Runtime gate behavior is profile-driven via `configs/runtime_profiles.yaml`.

- `strict` (and alias `week1-stress`) is fail-fast:
  - incomplete FGSM sweep fails,
  - baseline metrics equal to FGSM metrics fails.
- `demo` / `fast-demo` (and alias `week1-demo`) are warning-tolerant:
  - incomplete FGSM sweep emits a warning and continues,
  - baseline equals FGSM emits a warning and continues.

These warning paths are acceptable in demo mode because demo/package workflows prioritize observability and artifact continuity during rehearsals, while strict profiles remain the enforcement path for CI-grade integrity checks.

Individual gates:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/check_contract_ownership.py
PYTHONPATH=src ./.venv/bin/python scripts/ci/check_demo_gate.py --profile week1-demo --output-root outputs/demo-gate-ci
PYTHONPATH=src ./.venv/bin/python scripts/ci/check_artifact_gate.py --output-root outputs/demo-gate-ci
PYTHONPATH=src ./.venv/bin/python scripts/ci/validate_output_schemas.py \
  --framework-run-dir outputs/framework_runs/<run_name> \
  --legacy-compat-csv outputs/demo-gate-ci/metrics_summary.csv
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
- Demo script package usage: `scripts/demo/README.md`
- Versioned schemas: `schemas/v1/`
- Additional docs: `docs/`

## 7) Recommended Operator Path

- Canonical primary path: `scripts/run_unified.py`.
- Fallback for demo rehearsals: `scripts/demo/run_demo_package.sh`.
- Use **framework runner + sweep/report scripts** for modular robustness analysis.

