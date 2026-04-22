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

## Maintenance Posture

- Single-maintainer repository as of 2026-04-21
- Prioritize stable entrypoints, reproducible outputs, and archive clarity over team onboarding flow
- Keep compatibility names such as `team_summary.*` stable until they are intentionally migrated
- Prefer `operator`, `maintainer`, `local machine`, or `current workspace` wording in new docs instead of `teammate`

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

scripts/run_unified.py sweep
  -> --profile yolo11n_lab_v1
  -> scripts/sweep_and_report.py (compatibility backend)
  -> repeated run_experiment.py invocations
  -> framework report generation
  -> optional `team_summary.*` generation (legacy name; still supported)

scripts/auto_cycle.py
  -> --profile yolo11n_lab_v1
  -> Phase 1 / Phase 2 / report regeneration use scripts/run_unified.py sweep
  -> report regeneration intentionally requests only the local/core report set
     (framework CSV/Markdown + local dashboard)
  -> manual sweeps may still enable optional extras; the loop does not request them
  -> scripts/sweep_and_report.py remains the compatibility backend behind that public sweep surface
  -> profile-defined attack/defense catalogs
  -> ranking / tuning / validation
```

There is no root-level `run_experiment.py` compatibility shim in the current
tree. Use `scripts/run_unified.py` for the public runtime surface. Keep
`scripts/sweep_and_report.py` for backend compatibility and direct legacy calls.

`Adversarial_Patch` is an external research/artifact workspace. It is not part
of the canonical runtime surface and is not a second orchestration path.

Local full-quality command: `python scripts/ci/run_repo_quality_gate.py --lane ci`.
`scripts/check_environment.py` remains a separate local-machine prerequisite
check and is not part of CI parity yet.
The repo quality bar, review rubric, and retroactive audit commands now live in
`CODE_QUALITY_STANDARD.md`, and root `AGENTS.md` is the short default contract
for coding agents.

## Runtime Surface Classification

- Core runtime: `scripts/run_unified.py run-one|sweep`
- Compatibility backend: `scripts/sweep_and_report.py`
- Optional maintained workflow implementations: `scripts/automation/`, `scripts/training/`, `scripts/reporting/`, `scripts/demo/`
- Supported compatibility entrypoints: root `scripts/*.py` workflow wrappers
- Supported compatibility shims: old flat adapter paths under `lab.attacks`, `lab.defenses`, and `lab.models`
- Supported compatibility facade: `lab.reporting` umbrella imports
- Manual utility: `scripts/check_environment.py`

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

Preferred-name inventory helpers now live in `lab.plugins.core` and
`lab.plugins.extra`. The old registries remain the execution path for now, and
raw alias availability still lives under `lab.attacks`, `lab.defenses`, and
`lab.models`.

Execution registries now load through `lab.plugins.core.*` and
`lab.plugins.extra.*` bootstrap packages. The old adapter modules remain the
implementation location, and both core and extra packages are still enabled by
default.

The registries now also support a core-only execution mode via
`include_extra=False`, and `lab.plugins.core` exposes build/list helpers for
that mode. Current runtime call sites still default to full-surface loading.

Canonical profiled runtime paths now use core-only plugin loading. Manual-only
and incompatible configs still enable extra plugins automatically, and `all`
expansion on canonical profiled sweeps now means the profile-approved core set.

Extra adapter implementations now live under `lab.plugins.extra.*`. The old
flat module paths remain compatibility shims, and support/helper modules still
remain in the flat packages for now.

Core adapter implementations now live under `lab.plugins.core.*`. The old flat
module paths remain compatibility shims, and flat `lab.attacks`,
`lab.defenses`, and `lab.models` still retain bases, registries, and
helper/support modules for now.

The automation implementations now live in `scripts/automation/`. The root
`scripts/*.py` automation paths remain compatibility wrappers, and the public
commands are unchanged.

The training implementations now live in `scripts/training/`. The root
`scripts/*.py` training entrypoints remain compatibility wrappers, and the
public commands are unchanged.

The reporting CLIs now live in `scripts/reporting/`, and the demo CLI now
lives in `scripts/demo/`. The root `scripts/*.py` paths remain compatibility
wrappers, and the public commands are unchanged.

`lab.reporting` umbrella imports remain compatibility-only. New code should
prefer `lab.reporting.framework`, `lab.reporting.local`, and
`lab.reporting.aggregate`.

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
- `outputs/framework_reports/<sweep_id>/team_summary.json` (legacy compatibility name)
- `outputs/framework_reports/<sweep_id>/team_summary.md` (legacy compatibility name)
- `outputs/framework_reports/<sweep_id>/dashboard.html`

Authoritative canonical sweep outputs are the framework CSV/Markdown report
plus the local dashboard under the explicit report root. `team_summary.*`,
`failure_gallery.html`, and `outputs/dashboard.html` remain optional extras.
Defaults still preserve the current behavior; the new CLI flags only make that
boundary explicit as extraction prep.

Cycle outputs:

- `outputs/cycle_history/*.json`
- `outputs/cycle_report.md`
- `outputs/cycle_report.csv`
- `outputs/dashboard.html` as a compatibility mirror of the latest generated dashboard

Schema files live in `schemas/v1/`. Runtime constants live in
`src/lab/config/contracts.py`.

Reporting now has stable namespaces at `lab.reporting.framework`,
`lab.reporting.local`, and `lab.reporting.aggregate`. The umbrella
`lab.reporting` remains compatibility-only. The remaining report-generation
logic now lives under those namespace packages, and the
`scripts/generate_*.py` entrypoints are thin CLI wrappers.

## Reporting selection rules

Warnings and concise summaries prefer `reporting_context.authority=authoritative`
rows when both authoritative and diagnostic rows exist for the same comparison.
Diagnostic-only smoke reports are still valid diagnostic artifacts; they should
not be interpreted as proof that Phase 4 validation is missing.

For `yolo11n_lab_v1`, authoritative rows are keyed to `mAP50`. `mAP50-95`
remains diagnostic-only in v1.
