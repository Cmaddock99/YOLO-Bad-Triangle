# Team Guide

This is the quickest accurate onboarding doc for a teammate joining the repo.

## What this project is

YOLO-Bad-Triangle is an adversarial robustness experiment lab for YOLO object
detection. The goal is not just to run attacks, but to produce results that are
comparable, reproducible, and easy to hand to another teammate.

## Use these commands first

If you need to create the local environment from scratch, use:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Verify the environment

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

### Dry-run a config

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --dry-run
```

### Run one smoke test

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=blur \
  --set runner.max_images=8 \
  --set runner.run_name=smoke_blur
```

### Run a sweep

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool \
  --defenses c_dog,median_preprocess \
  --preset smoke
```

### Run quality checks

```bash
./.venv/bin/ruff check src tests scripts
./.venv/bin/mypy
./.venv/bin/pytest -q
```

## Canonical entrypoints

- Single run: `scripts/run_unified.py run-one`
- Sweep: `scripts/sweep_and_report.py`
- Closed loop: `scripts/auto_cycle.py --loop`

Prefer these over ad hoc scripts when you are doing normal repository work.

## What gets written

Single run:

- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/run_summary.json`
- `outputs/framework_runs/<run_name>/resolved_config.yaml`

Sweep:

- `outputs/framework_reports/<sweep_id>/framework_run_report.md`
- `outputs/framework_reports/<sweep_id>/framework_run_summary.csv`
- `outputs/framework_reports/<sweep_id>/team_summary.json`
- `outputs/framework_reports/<sweep_id>/team_summary.md`

Cycle history:

- `outputs/cycle_history/*.json`
- `outputs/cycle_report.md`
- `outputs/cycle_report.csv`

## Current implementation detail that matters

The runner currently applies transforms in this order:

`attack.apply -> defense.preprocess -> model.predict -> defense.postprocess`

That order is written into run artifacts together with
`semantic_order=attack_then_defense`. If you are interpreting "defense
recovery" numbers, this is now the canonical behavior to compare against.

## Plugin locations

- Attacks: `src/lab/attacks/`
- Defenses: `src/lab/defenses/`
- Models: `src/lab/models/`
- Runner: `src/lab/runners/run_experiment.py`
- Reporting: `src/lab/reporting/`
- Schemas: `schemas/v1/`

List live plugin names with:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

## Current defense catalog nuance

`c_dog_ensemble` is still registered, but the current auto-cycle catalog does
not include it. Do not assume "registered" and "used by auto_cycle" mean the
same thing.

## When you extend the repo

### Add an attack

1. Create a `*_adapter.py` file under `src/lab/attacks/`.
2. Register it with `@register_attack_plugin(...)`.
3. Smoke-test it with `scripts/run_unified.py run-one`.

### Add a defense

1. Create a `*_adapter.py` file under `src/lab/defenses/`.
2. Register it with `@register_defense_plugin(...)`.
3. Smoke-test it with `scripts/run_unified.py run-one`.

Templates:

- `docs/ATTACK_TEMPLATE.md`
- `docs/DEFENSE_TEMPLATE.md`

## Supporting docs

- Root `README.md` for the short canonical workflow
- `PROJECT_STATE.md` for the current repo map
- `docs/PIPELINE_IN_PLAIN_ENGLISH.md` for the layman's explanation
- `docs/LOOP_DESIGN.md` for cycle automation and longitudinal reporting
