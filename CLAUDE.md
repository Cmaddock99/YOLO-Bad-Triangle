# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLO-Bad-Triangle is an adversarial robustness experimentation framework for YOLO object detection models. It uses a **framework-first** execution path with JSON artifacts, while the legacy runtime is rollback-only and disabled by default (`USE_LEGACY_RUNTIME=false`).

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./.venv/bin/python scripts/check_environment.py
```

Always use `./.venv/bin/python` and set `PYTHONPATH=src` when running framework code.

## Common Commands

### Run a single experiment (canonical)
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml
```

### Run a sweep
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep --attacks fgsm,pgd
```

### Quick framework smoke test (8 images, no validation)
```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/default.yaml \
  --set runner.run_name=framework_smoke \
  --set attack.name=blur \
  --set validation.enabled=false \
  --set runner.max_images=8
```

### Run all tests
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

### Run a single test file
```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests/test_framework_output_contract.py
```

## Architecture

### Execution Path (Framework-First)

```
run_experiment.py (compat wrapper)
  └── scripts/run_unified.py run-one / sweep  ← canonical entry
        └── src/lab/runners/run_experiment.py  ← UnifiedExperimentRunner
              ├── Loads YAML config + --set overrides
              ├── Applies attack plugin → defense plugin → YOLO model
              └── Writes outputs/framework_runs/<run_name>/
                    ├── metrics.json       (schema: framework_metrics/v1)
                    ├── predictions.jsonl  (per-image JSONL)
                    └── run_summary.json   (schema: framework_run_summary/v1)
```

The compat wrapper `run_experiment.py` delegates to `scripts/run_unified.py`. Prefer the canonical entry for new work.

### Plugin System

Attacks and defenses each have one framework registry:
- **`framework_registry.py`** — combined decorator registry + lazy adapter loader (single source of truth)
- **`registry.py`** — legacy registry (do not extend)

Models use a separate `plugin_registry.py` + `registry.py` pair.

Framework plugins (attacks/defenses) implement `BaseAttack` / `BaseDefense` interfaces that operate on single images. Legacy implementations operate on directories and are adapter-wrapped for framework use (e.g., `fgsm_adapter.py` wraps `fgsm.py`).

### Config System

YAML configs in `configs/` with `--set key=value` dotted-path overrides. Central constants live in `src/lab/config/contracts.py` — this is the source of truth for schema IDs, toggle keys, parity thresholds, and inference defaults.

Key toggles (dotted keys for `--set`):
- `validation.enabled` — enable post-run contract validation
- `summary.enabled` — enable summary generation

### Key Module Locations

| Concern | Location |
|---|---|
| Core runner | `src/lab/runners/run_experiment.py` |
| Attack plugins | `src/lab/attacks/` |
| Defense plugins | `src/lab/defenses/` |
| Model adapters | `src/lab/models/` |
| Metrics/eval | `src/lab/eval/` |
| Health checks | `src/lab/health_checks/` |
| Reporting | `src/lab/reporting/` |
| Schema IDs & constants | `src/lab/config/contracts.py` |
| CI gate scripts | `scripts/ci/` |
| JSON schemas | `schemas/v1/` |

### Output Contracts

Framework path (primary):
```
outputs/framework_runs/<run_name>/
├── metrics.json        # aggregated metrics
├── predictions.jsonl   # per-image predictions
└── run_summary.json    # run metadata
```

### Run Naming Convention

Use `<model>__<attack>__<defense>` format (e.g., `yolov8n__fgsm__none`) for consistent teammate defense matrix comparisons under `outputs/defense_eval/`.

## Key Documentation

- `PROJECT_STATE.md` — authoritative architecture and runner state
- `docs/` — in-depth guides
- `scripts/demo/README.md` — demo package usage
