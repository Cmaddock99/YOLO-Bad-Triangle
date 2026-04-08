# YOLO Robustness Lab: Design and Delivery Status

Last updated: 2026-04-02

This document summarizes the current implemented system, not the historical
refactor path.

## Problem statement

Build a repeatable experiment lab to measure how YOLO object detection quality
changes under configurable attacks and optional defenses, while keeping outputs
structured enough for reliable comparison and reporting.

## Current implemented capabilities

| Area | Status | Notes |
|---|---|---|
| Single config-driven run | Implemented | `scripts/run_unified.py run-one` |
| Multi-attack and multi-defense sweep | Implemented | `scripts/sweep_and_report.py` |
| Structured run outputs | Implemented | `metrics.json`, `predictions.jsonl`, `run_summary.json`, `resolved_config.yaml`; checkpointed defenses also record defense-model provenance in `run_summary.json` under `provenance.defense_checkpoints` |
| Structured report outputs | Implemented | markdown, CSV, team summary |
| Plugin-based attacks and defenses | Implemented | registries under `src/lab/attacks/` and `src/lab/defenses/` |
| Output contract validation | Implemented | `scripts/ci/validate_outputs.py`, `schemas/v1/` |
| Closed-loop cycle automation | Implemented | `scripts/auto_cycle.py` |
| Full determinism across all external libraries | Partial | seed is recorded, but complete determinism is not guaranteed |

## Current repository map

| Concern | Location |
|---|---|
| Canonical single-run CLI | `scripts/run_unified.py` |
| Canonical sweep CLI | `scripts/sweep_and_report.py` |
| Core runner | `src/lab/runners/run_experiment.py` |
| CLI/config helpers | `src/lab/runners/cli_utils.py` |
| Attack registries and adapters | `src/lab/attacks/` |
| Defense registries and adapters | `src/lab/defenses/` |
| Model adapters | `src/lab/models/` |
| Metrics and prediction schemas | `src/lab/eval/` |
| Reporting | `src/lab/reporting/` |
| Artifact health checks | `src/lab/health_checks/` |
| Contracts and schema IDs | `src/lab/config/contracts.py` |
| JSON schemas | `schemas/v1/` |

## Runtime behavior

The current runner writes the following transform order into its artifacts:

`attack.apply -> defense.preprocess -> model.predict -> defense.postprocess`

Current artifacts also record `semantic_order=attack_then_defense`. That is the
behavior being measured by current reports, and it is the canonical post-switch
semantics for defended comparisons.

## Canonical commands

### Single run

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm
```

### Sweep

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd \
  --defenses c_dog,median_preprocess \
  --preset smoke
```

### Quality gates

```bash
./.venv/bin/ruff check src tests scripts
./.venv/bin/mypy
./.venv/bin/pytest -q
```

## Historical note

Older documents, handoff notes, and generated reports may mention removed paths
such as `scripts/run_framework.py`, `configs/experiment_lab.yaml`, or a root
`run_experiment.py` shim. Those are not current entrypoints.
