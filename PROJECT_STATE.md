# Project State

Current architecture reference for the repository as it exists today.

## Canonical execution path

```text
scripts/run_unified.py run-one
  -> src/lab/runners/run_experiment.py
     -> attack registry
     -> defense registry
     -> model adapter
     -> metrics / reporting artifacts

scripts/sweep_and_report.py
  -> repeated run_experiment.py invocations
  -> framework report generation
  -> optional team summary generation
```

There is no root-level `run_experiment.py` compatibility shim in the current
tree. Use `scripts/run_unified.py` and `scripts/sweep_and_report.py`.

## Current transform order

The runner currently records this transform order in `metrics.json` and
`run_summary.json`:

`attack.apply -> defense.preprocess -> model.predict -> defense.postprocess`

Current artifacts also record `semantic_order=attack_then_defense` so reports
can distinguish this canonical era from older legacy outputs.

## Plugin system

### Attacks

- Location: `src/lab/attacks/`
- Registration: `@register_attack_plugin(...)` in `*_adapter.py`
- Base contract: `BaseAttack.apply(image, model, **kwargs) -> (image, metadata)`

### Defenses

- Location: `src/lab/defenses/`
- Registration: `@register_defense_plugin(...)` in `*_adapter.py`
- Base contract: `BaseDefense.preprocess(...)` and `BaseDefense.postprocess(...)`

### Models

- Location: `src/lab/models/`
- Current primary model adapter: `yolo`

List live plugin names with:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

## Registered attacks

`blur`, `cw`, `deepfool`, `dispersion_reduction`, `eot_pgd`, `fgsm`,
`fgsm_center_mask`, `fgsm_edge_mask`, `jpeg_attack`, `pgd`, `square`

## Registered defenses

`bit_depth`, `c_dog`, `c_dog_ensemble`, `confidence_filter`,
`jpeg_preprocess`, `median_preprocess`, `none`, `random_resize`

## Active auto-cycle catalogs

### Attacks

`blur`, `deepfool`, `dispersion_reduction`, `eot_pgd`, `fgsm`, `pgd`, `square`

### Defenses

`bit_depth`, `c_dog`, `jpeg_preprocess`, `median_preprocess`

`c_dog_ensemble` remains registered but is currently excluded from
`scripts/auto_cycle.py` ranking and tuning.

## Important configs

- `configs/default.yaml` - default single-run config
- `configs/ci_demo.yaml` - tiny CI-safe run
- `configs/coco_subset500.yaml` - validation dataset config
- `configs/runtime_profiles.yaml` - profile aliases and runtime guardrails
- `configs/defense_eval_sweep.yaml` - reference matrix config, not the canonical runner input

## Output contracts

Framework run outputs:

- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/run_summary.json`
- `outputs/framework_runs/<run_name>/resolved_config.yaml`

Report outputs:

- `outputs/framework_reports/<sweep_id>/framework_run_report.md`
- `outputs/framework_reports/<sweep_id>/framework_run_summary.csv`
- `outputs/framework_reports/<sweep_id>/team_summary.json`
- `outputs/framework_reports/<sweep_id>/team_summary.md`

Cycle outputs:

- `outputs/cycle_history/*.json`
- `outputs/cycle_report.md`
- `outputs/cycle_report.csv`
- `outputs/dashboard.html`

Schema files live in `schemas/v1/`. Runtime constants live in
`src/lab/config/contracts.py`.
