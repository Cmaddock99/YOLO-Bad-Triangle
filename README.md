# YOLO-Bad-Triangle

Framework-first lab for **attack → defend → evaluate** runs on Ultralytics YOLO models: perturb images (attacks), optionally harden inputs or outputs (defenses), run detection, and emit contract-shaped artifacts under `outputs/framework_runs/`.

This public repository contains the code used for a capstone on adversarial robustness for YOLO-based object detection. Historical experiment outputs, notebooks, presentation materials, and private paper-support artifacts are intentionally kept out of the public repo.

## Quick start

Requires **Python 3.11** by default; **Python 3.13** is also supported (see [`requirements.txt`](requirements.txt)).

```bash
python3.11 -m venv .venv  # preferred; python3.13 also supported
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=src       # Windows: set PYTHONPATH=src
python scripts/run_unified.py run-one \
  --config configs/ci_demo.yaml \
  --set runner.output_root=outputs/framework_runs/local \
  --set runner.run_name=demo
```

The CI demo uses the same config shape as [`.github/workflows/ci.yml`](.github/workflows/ci.yml) / [`scripts/ci/run_repo_quality_gate.py`](scripts/ci/run_repo_quality_gate.py): [`configs/ci_demo.yaml`](configs/ci_demo.yaml) with a tiny image budget.

For matrix sweeps and HTML reports:

```bash
python scripts/run_unified.py sweep --help
```

Canonical single-run engine: [`src/lab/runners/run_experiment.py`](src/lab/runners/run_experiment.py) (`UnifiedExperimentRunner`). Entrypoints: [`scripts/run_unified.py`](scripts/run_unified.py), [`scripts/sweep_and_report.py`](scripts/sweep_and_report.py).

## Attack, defend, and “fortify”

| Layer | What runs it | Notes |
|--------|----------------|--------|
| **Attack** | `attack.apply` in the runner | Registered via [`src/lab/attacks/framework_registry.py`](src/lab/attacks/framework_registry.py) (plugins under `lab.plugins.core/extra.attacks`). |
| **Defend** | `defense.preprocess` / `defense.postprocess` | [`src/lab/defenses/framework_registry.py`](src/lab/defenses/framework_registry.py). |
| **Model** | `model.predict` | [`src/lab/models/framework_registry.py`](src/lab/models/framework_registry.py). |
| **Fortify (training / cycles)** | Outside the per-image runner | Phased automation in [`scripts/automation/auto_cycle.py`](scripts/automation/auto_cycle.py); training helpers under [`scripts/training/`](scripts/training/). This is the closest end-to-end “strengthen the stack” loop; it is **not** a third transform inside `UnifiedExperimentRunner`. |

**Pipeline order (runner):** `attack.apply` → `defense.preprocess` → `model.predict` → `defense.postprocess` ([`src/lab/config/contracts.py`](src/lab/config/contracts.py), `CURRENT_PIPELINE_TRANSFORM_ORDER`). The runner always uses this order; `defense_then_attack` exists for **reporting and cycle metadata** (`LEGACY_PIPELINE_TRANSFORM_ORDER`), not as a selectable runner mode today.

**`fortify_mode` in profiles:** Required in [`configs/pipeline_profiles.yaml`](configs/pipeline_profiles.yaml) and merged into resolved config ([`src/lab/config/profiles.py`](src/lab/config/profiles.py)). It describes **how the lab intends to use** ranking/tuning/validation (e.g. via `auto_cycle`); it does **not** toggle transforms inside a single `run-one` invocation.

## Plugins vs compatibility shims

Canonical implementations live under [`src/lab/plugins/`](src/lab/plugins/) (`core` vs `extra`). Many modules under [`src/lab/attacks/`](src/lab/attacks/) are **thin re-exports** (e.g. `fgsm_adapter.py` → `lab.plugins.core.attacks.fgsm_adapter`) so older import paths keep working. Prefer `lab.plugins…` for new code.

## Quality gates

- Tests: `pytest -q` from repo root with `PYTHONPATH=src`.
- Artifact + schema gate: [`scripts/ci/validate_outputs.py`](scripts/ci/validate_outputs.py) (metrics, run summary, legacy CSV, **predictions.jsonl** line records, and optional **`framework_run_summary.csv`** under `--framework-report-dir` when passed with `--require-schema`).

## `outputs/` and version control

Runs write under `outputs/framework_runs/`, sweeps under `outputs/framework_reports/`, and automation under paths like `outputs/cycle_*`. In the public repo these are treated as **generated local artifacts**, not committed deliverables. [`scripts/ci/check_tracked_outputs.py`](scripts/ci/check_tracked_outputs.py) enforces that policy.

## Dev dependencies

```bash
pip install -r requirements-dev.txt
```

Then `ruff`, `mypy`, and full CI-parity checks are available via [`scripts/ci/run_repo_quality_gate.py`](scripts/ci/run_repo_quality_gate.py) (`--lane ci`).
