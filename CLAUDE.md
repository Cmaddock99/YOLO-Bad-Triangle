# CLAUDE.md

Guidance for Claude Code when working in this repository.

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
  --workers auto
```

### List plugins
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

### Run tests
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

### Single test file
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests/test_framework_output_contract.py
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

## Notes

- `PYTHONPATH=src` is required. It's set in `.env` but must be explicit for direct script invocations.
- `DPC_UNET_CHECKPOINT_PATH=dpc_unet_final_golden.pt` is set in `.env` — c_dog works without extra env setup.
- The root-level `run_experiment.py` is a legacy shim. Use `scripts/run_unified.py` for all new work.
