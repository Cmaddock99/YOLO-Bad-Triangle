# Project State

Current architecture reference. See `CLAUDE.md` for development commands.

## Execution Path

```
scripts/run_unified.py run-one / sweep   ← canonical entry
  └── src/lab/runners/run_experiment.py  ← UnifiedExperimentRunner
        ├── Loads configs/default.yaml + --set overrides
        ├── Builds attack plugin → defense plugin → YOLO model
        └── Writes outputs/framework_runs/<run_name>/
              ├── metrics.json       (schema: framework_metrics/v1)
              ├── predictions.jsonl
              └── run_summary.json   (schema: framework_run_summary/v1)
```

The root-level `run_experiment.py` is a compatibility shim — it forwards to `scripts/run_unified.py run-one`. Use `run_unified.py` for all new work.

## Plugin System

**Attacks** (`src/lab/attacks/`): registered via `@register_attack_plugin("name")` in `*_adapter.py` files. Loaded lazily on first use. Implement `BaseAttack.apply(image, model, **kwargs) -> (image, metadata)`.

**Defenses** (`src/lab/defenses/`): same pattern via `@register_defense_plugin("name")`. Implement `BaseDefense.preprocess()` and `BaseDefense.postprocess()`.

**Models** (`src/lab/models/`): `yolo` is the only registered model. Wraps Ultralytics YOLO, normalizes outputs to `PredictionRecord`.

List all available plugins at any time:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

## Registered Attacks

`bim`, `blur`, `deepfool`, `fgsm`, `gaussian_blur`, `ifgsm`, `pgd`

## Registered Defenses

`c_dog`, `c_dog_ensemble`, `confidence_filter`, `median_preprocess`, `none`

(`preprocess_dpc_unet`, `preprocess_median_blur`, `preprocess_ensemble_c_dog` are aliases.)

## Config System

YAML configs in `configs/`. Active configs:

| Config | Purpose |
|---|---|
| `configs/default.yaml` | Default values for all runs |
| `configs/coco_subset500.yaml` | Validation dataset (500 COCO val images) |
| `configs/runtime_profiles.yaml` | Gate behavior profiles (strict / demo) |
| `configs/defense_eval_sweep.yaml` | Reference matrix for defense evaluation |

Override any key with `--set dotted.key=value`. Multiple `--set` flags allowed.

## Output Contracts

Framework run outputs (`outputs/framework_runs/<run_name>/`):
- `metrics.json` — schema `framework_metrics/v1`
- `run_summary.json` — schema `framework_run_summary/v1`
- `predictions.jsonl` — one JSON object per image

Schema files live in `schemas/v1/`.

## Key Module Locations

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
