# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLO-Bad-Triangle is an adversarial robustness lab for YOLO object detection. It runs attacks against YOLO models, applies defenses, and measures recovery via mAP50 and detection confidence. All execution goes through the framework-first path.

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

Always use `./.venv/bin/python` and `PYTHONPATH=src` for all framework code.

## Common Commands

### Single run
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=my_run
```

### Sweep
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool \
  --defenses c_dog,median_preprocess \
  --preset full \
  --workers auto \
  --validation-enabled
```

Key sweep flags:

| Flag | Description |
|---|---|
| `--attacks all` / `--defenses all` | Every registered plugin |
| `--preset smoke` / `--preset full` | 8 images vs all 500 |
| `--workers N` / `--workers auto` | Parallel subprocesses — use `--workers 1` on single-GPU to avoid OOM |
| `--validation-enabled` | Compute mAP50 after each run |
| `--resume` | Skip runs that already completed |
| `--skip-errors` | Continue on failure, report at end |

### List plugins
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

### Run tests
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# or
pytest -q
```

### Single test file
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests/test_framework_output_contract.py
```

### Lint and type-check
```bash
ruff check src tests scripts
mypy src tests scripts
```

### CI output validation
```bash
python scripts/ci/validate_outputs.py --output-root outputs/framework_runs/<run_name>
```

## Architecture

### Execution path

```
scripts/run_unified.py run-one / sweep   ← canonical entry
  └── src/lab/runners/run_experiment.py  ← UnifiedExperimentRunner
        ├── Loads YAML config + --set overrides
        ├── Builds attack → defense → YOLO model
        └── Writes outputs/framework_runs/<run_name>/
              ├── metrics.json
              ├── predictions.jsonl
              └── run_summary.json
```

### Plugin system

Attacks and defenses register via decorator in `*_adapter.py` files:
- `src/lab/attacks/framework_registry.py` — attack registry + lazy loader
- `src/lab/defenses/framework_registry.py` — defense registry + lazy loader

Plugins implement `BaseAttack.apply(image, model) -> (image, meta)` or `BaseDefense.preprocess/postprocess`.

### Config system

YAML files in `configs/` with dotted-path `--set` overrides. Source of truth for constants: `src/lab/config/contracts.py`.

Key `--set` toggles:
- `validation.enabled` — enable mAP50 validation after run
- `summary.enabled` — enable summary generation
- `runner.max_images` — limit images processed (0 = all)

### Key module locations

| Concern | Location |
|---|---|
| Core runner | `src/lab/runners/run_experiment.py` |
| Attack plugins | `src/lab/attacks/` |
| Defense plugins | `src/lab/defenses/` |
| Model adapters | `src/lab/models/` |
| Metrics / eval | `src/lab/eval/` |
| Health checks | `src/lab/health_checks/` |
| Reporting | `src/lab/reporting/` |
| Schema IDs + constants | `src/lab/config/contracts.py` |
| CI gate scripts | `scripts/ci/` |
| JSON schemas | `schemas/v1/` |

## Output Contracts

```
outputs/framework_runs/<run_name>/
├── metrics.json        # schema: framework_metrics/v1
├── predictions.jsonl   # per-image predictions
└── run_summary.json    # schema: framework_run_summary/v1
```

## Run Naming Convention

Use `<model>__<attack>__<defense>` (e.g. `yolo26n__fgsm__c_dog`) for defense matrix comparisons under `outputs/defense_eval/`.

## Framework-first constraints

These are hard rules — do not work around them:

1. **No new registries.** Reuse the existing ones: `src/lab/{runners,attacks,defenses,models}/framework_registry.py`.
2. **No ad-hoc entrypoints.** All lab workflows go through `scripts/run_unified.py` or `scripts/sweep_and_report.py`.
3. **No duplicate contracts.** Schema definitions live only in `schemas/v1/` and `src/lab/config/contracts.py`.
4. **Keep CI gates aligned.** Output validation must stay consistent with `scripts/ci/validate_outputs.py` and `src/lab/health_checks/`.

**Preferred change pattern:**
- Add derived metrics to `src/lab/eval/derived_metrics.py`, not inline in scripts.
- Add or update report tables in `src/lab/reporting/framework_comparison.py`, not new one-off builders.
- Update tests under `tests/` whenever behavior or output contracts change.

**Adding a new attack or defense:** follow the templates in `docs/ATTACK_TEMPLATE.md` and `docs/DEFENSE_TEMPLATE.md`.

## Notes

- `PYTHONPATH=src` is required. It's set in `.env` but must be explicit for direct script invocations.
- `DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt` is set in `.env` — `c_dog` and `c_dog_ensemble` work without extra env setup.
- The experiment runner implementation lives in `src/lab/runners/run_experiment.py`; invoke it only through `scripts/run_unified.py` or `scripts/sweep_and_report.py`.
- Colab runs: open `colab_sweep.ipynb` on a T4 GPU runtime. Clear notebook outputs before committing to keep diffs small.
