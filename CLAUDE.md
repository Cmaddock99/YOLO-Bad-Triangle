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
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/lab_framework_phase5.yaml
```

### Run a sweep
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep --attacks fgsm,pgd
```

### Quick framework smoke test (8 images, no validation)
```bash
PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py \
  --config configs/lab_framework_phase5.yaml \
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

### Shadow parity check (required pre-merge)
```bash
PYTHONPATH=src ./.venv/bin/python run_shadow_parity.py --config configs/parity_test.yaml
```

### System health gate
```bash
PYTHONPATH=src ./.venv/bin/python run_system_health_check.py --parity-config configs/parity_test.yaml
```

### Full migration gates (CI-ready)
```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/run_migration_gates.py \
  --parity-config configs/parity_test.yaml \
  --demo-profile week1-demo \
  --demo-output-root outputs/demo-gate-ci \
  --allow-missing-baseline
```

### Migration status dashboard
```bash
./.venv/bin/python scripts/migration_status.py
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

The compat wrappers (`run_experiment.py`, `run_experiment_api.py`, `scripts/run_framework.py`) all delegate to `scripts/run_unified.py`. Prefer the canonical entry for new work.

### Plugin System

Attacks, defenses, and models each have two registries:
- **`plugin_registry.py`** — decorator-based registry for framework plugins
- **`framework_registry.py`** — builder with lazy imports
- **`registry.py`** — legacy registry (do not extend)

Framework plugins (attacks/defenses) implement `BaseAttack` / `BaseDefense` interfaces that operate on single images. Legacy implementations operate on directories and are adapter-wrapped for framework use (e.g., `fgsm_adapter.py` wraps `fgsm.py`).

### Config System

YAML configs in `configs/` with `--set key=value` dotted-path overrides. Central constants live in `src/lab/config/contracts.py` — this is the source of truth for schema IDs, toggle keys, parity thresholds, and inference defaults.

Key toggles (dotted keys for `--set`):
- `validation.enabled` — enable post-run contract validation
- `parity.enabled` — enable shadow parity check
- `parity.fail_on_mismatch` — fail run on parity mismatch
- `summary.enabled` — enable summary generation
- `migration.use_legacy_runtime` — use legacy runtime (gated by env var)

### Key Module Locations

| Concern | Location |
|---|---|
| Core runner | `src/lab/runners/run_experiment.py` |
| Attack plugins | `src/lab/attacks/` |
| Defense plugins | `src/lab/defenses/` |
| Model adapters | `src/lab/models/` |
| Metrics/eval | `src/lab/eval/` |
| Migration/parity | `src/lab/migration/` |
| Health checks | `src/lab/health_checks/` |
| Reporting | `src/lab/reporting/` |
| Schema IDs & constants | `src/lab/config/contracts.py` |
| CI gate scripts | `scripts/ci/` |
| Ops automation | `scripts/ops/` |
| JSON schemas | `schemas/v1/` |
| SLO contracts | `contracts/migration_contracts.yaml` |

### Output Contracts

Framework path (primary):
```
outputs/framework_runs/<run_name>/
├── metrics.json        # aggregated metrics
├── predictions.jsonl   # per-image predictions
└── run_summary.json    # run metadata
```

Legacy path (rollback only):
```
outputs/metrics_summary.csv
outputs/experiment_table.md
outputs/<run_name>/
```

### Parity Validation

Shadow parity runs both framework and legacy paths on the same input and compares detection/confidence deltas. Default thresholds: ≤5% relative delta for both detections and confidence. Parity reports written to `outputs/shadow_parity/`.

### Run Naming Convention

Use `<model>__<attack>__<defense>` format (e.g., `yolov8n__fgsm__none`) for consistent teammate defense matrix comparisons under `outputs/defense_eval/`.

## Key Documentation

- `PROJECT_STATE.md` — authoritative architecture and runner state
- `READINESS_REPORT.md` — readiness snapshot
- `docs/` — 26 in-depth guides (migration contracts, incident playbooks, hygiene checklists)
- `scripts/demo/README.md` — demo package usage
- `contracts/migration_contracts.yaml` — SLO definitions
