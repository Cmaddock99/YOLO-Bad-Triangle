# Project State

## Current Phase

**YOLOv8 Direction A: COMPLETE** (verdict: PAUSE c_dog, 2026-04-09)
- Closure record: `docs/analysis/direction_a_closure_20260409.md`
- c_dog checkpoint (`dpc_unet_adversarial_finetuned.pt`) is YOLOv8-specific; do not use for YOLOv11 training

**One Real Pipeline v1: IMPLEMENTED**
- Canonical runtime home: `YOLO-Bad-Triangle`
- Canonical profile: `yolo11n_lab_v1`
- Canonical model: `yolo11n.pt`
- Canonical authority metric: **mAP50**
- Canonical fortify mode: attack/defense ranking + parameter tuning + validation inside `scripts/auto_cycle.py`
- Digital and printable patch work remain out of the canonical v1 ranked/tuned loop
- Future patch support must enter as a profile-aware attack extension, not as a second runner

---

Current architecture reference for the repository as it exists today.

## Canonical execution path

```text
scripts/run_unified.py run-one
  -> --profile yolo11n_lab_v1
  -> src/lab/runners/run_experiment.py
     -> attack registry
     -> defense registry
     -> model adapter
     -> metrics / reporting artifacts

scripts/sweep_and_report.py
  -> --profile yolo11n_lab_v1
  -> repeated run_experiment.py invocations
  -> framework report generation
  -> optional team summary generation

scripts/auto_cycle.py
  -> --profile yolo11n_lab_v1
  -> profile-defined attack/defense catalogs
  -> ranking / tuning / validation
```

There is no root-level `run_experiment.py` compatibility shim in the current
tree. Use `scripts/run_unified.py` and `scripts/sweep_and_report.py`.

`Adversarial_Patch` is an external research/artifact workspace. It is not part
of the canonical runtime surface and is not a second orchestration path.

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
- Current adapters:
  - `yolo` — handles all ultralytics YOLO architectures (YOLOv8, YOLOv11, etc.) via `from ultralytics import YOLO`
  - `faster_rcnn` (alias: `torchvision_frcnn`)
- `yolo` supports prediction and validation.
- `faster_rcnn` supports prediction and returns a `not_supported` validation stub.
- YOLOv11 requires no new adapter — `yolo11n_lab_v1` resolves `model.params.model: yolo11n.pt`.

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

## Canonical v1 profile catalogs

### Attacks

`blur`, `deepfool`, `dispersion_reduction`, `eot_pgd`, `fgsm`, `pgd`, `square`

### Defenses

`bit_depth`, `jpeg_preprocess`, `median_preprocess`

Manual-only defenses under `yolo11n_lab_v1`:

`c_dog`, `c_dog_ensemble`, `confidence_filter`, `random_resize`

## Important configs

- `configs/default.yaml` - default single-run config
- `configs/ci_demo.yaml` - tiny CI-safe run
- `configs/coco_subset500.yaml` - validation dataset config
- `configs/pipeline_profiles.yaml` - canonical pipeline profiles and compatibility rules
- `configs/defense_eval_sweep.yaml` - reference matrix config, not the canonical runner input

## Output contracts

Framework run outputs:

- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/run_summary.json`
- `outputs/framework_runs/<run_name>/resolved_config.yaml`
- `outputs/framework_runs/<run_name>/experiment_summary.json` when `summary.enabled=true`

Run summaries now also carry:

- `pipeline_profile`
- `authoritative_metric`
- `profile_compatibility`

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

## Reporting selection rules

Warnings and concise summaries prefer `reporting_context.authority=authoritative`
rows when both authoritative and diagnostic rows exist for the same comparison.
Diagnostic-only smoke reports are still valid diagnostic artifacts; they should
not be interpreted as proof that Phase 4 validation is missing.

For `yolo11n_lab_v1`, authoritative rows are keyed to `mAP50`. `mAP50-95`
remains diagnostic-only in v1.
