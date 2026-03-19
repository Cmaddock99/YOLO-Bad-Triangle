# PROJECT_STATE.md

## DOCUMENT METADATA

- `validated_at_utc`: `2026-03-19T17:55:15Z`
- `validated_against_commit`: `4a11a17`
- `scope_note`: operational state map; keep synced with tests and plugin/runner changes

## CURRENT RUNNER

### Legacy/mainline runners (compatibility wrappers retained)

- `run_experiment.py` (compat wrapper; framework mode forwards to `scripts/run_unified.py run-one`)
- `run_experiment_api.py` (argparse one-run wrapper)
- `scripts/run_framework.py` -> `scripts/run_unified.py sweep` (framework-first path; `--legacy` keeps rollback path)
- Core execution engine: `src/lab/runners/experiment_runner.py` (`ExperimentRunner.run()`)

### Framework-first canonical runner path

- `scripts/run_unified.py` (canonical entrypoint)
- `src/lab/runners/run_experiment.py` (`UnifiedExperimentRunner`)

### Runner overlap assessment

- Compatibility wrappers remain, but canonical framework-first path is now `scripts/run_unified.py`.
- Legacy `ExperimentRunner` remains available for rollback workflows only.
- Legacy entrypoints (`run_experiment.py --legacy`, `scripts/run_framework.py --legacy`, `src/lab/runners/cli.py`)
  are emergency-only and policy-gated via `allow_legacy_runtime(...)`.

### Runtime/config constants source of truth

- `src/lab/config/contracts.py` centralizes:
  - schema IDs (`framework_metrics/v1`, `framework_run_summary/v1`, `legacy_compat_csv/v1`)
  - parity threshold defaults/keys
  - legacy inference defaults (`conf`, `iou`, `imgsz`)
  - canonical runtime path identifiers and compatibility wrapper entrypoint list
  - runtime toggle key paths (`validation.enabled`, `parity.enabled`, `parity.fail_on_mismatch`, `summary.enabled`, `migration.use_legacy_runtime`)
- Existing compatibility constant names remain exported for current callers.

## CURRENT ATTACKS

### Legacy attack implementations (directory-based `Attack.apply(source_dir, output_dir, ...)`)

- `none`, `identity`
- `blur`, `gaussian_blur`
- `gaussian_noise`, `noise`
- `noise_blockwise`, `block_noise`
- `fgsm`
- `fgsm_center_mask`, `fgsm_center`
- `fgsm_edge_mask`, `fgsm_edges`
- `pgd`, `ifgsm`, `bim`
- `eot_pgd`, `pgd_eot`
- `deepfool`
- `deepfool_band_limited`, `deepfool_banded`
- `blur_anisotropic`, `anisotropic_blur`
- `center_mask_blur_noise`, `center_blur_noise`
- `patch_occlusion_affine`, `occlusion_affine`
- `brightness_contrast_noise`, `photometric_noise`

Primary files:
- `src/lab/attacks/base.py`
- `src/lab/attacks/registry.py`
- `src/lab/attacks/*.py` (implementations)

### Framework attack plugins (`BaseAttack` single-image)

- Registry coverage can evolve; validate live plugin availability with:
  - `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --list-plugins`
- Regression coverage reference:
  - `tests/test_framework_attack_plugins.py`

Primary files:
- `src/lab/attacks/base_attack.py`
- `src/lab/attacks/plugin_registry.py`
- `src/lab/attacks/framework_registry.py`

## CURRENT DEFENSES

### Legacy defense implementations (`Defense.apply(source_dir, output_dir, ...)`)

- `none`, `identity`
- `median_blur`, `median`
- `denoise`, `nlm_denoise`

Primary files:
- `src/lab/defenses/base.py`
- `src/lab/defenses/registry.py`
- `src/lab/defenses/none.py`
- `src/lab/defenses/median_blur.py`
- `src/lab/defenses/denoise.py`

### Framework defense plugins (`BaseDefense` preprocess/postprocess)

- Registry coverage can evolve; validate live plugin availability with:
  - `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --list-plugins`
- Regression coverage reference:
  - `tests/test_framework_defense_plugins.py`

Primary files:
- `src/lab/defenses/base_defense.py`
- `src/lab/defenses/plugin_registry.py`
- `src/lab/defenses/framework_registry.py`

## CURRENT MODELS / YOLO USAGE

### Legacy model wrapper

- `src/lab/models/yolo_model.py`
  - loads Ultralytics `YOLO(...)` in `__post_init__`
  - `predict()` delegates to `.predict(...)`
  - `validate()` delegates to `.val(...)`

### Framework model adapter

- `src/lab/models/yolo_adapter.py`
  - wraps legacy `YOLOModel`
  - normalizes predictions into `PredictionRecord`
  - maps validation fields to: `precision`, `recall`, `mAP50`, `mAP50-95`

### Model registries

- `src/lab/models/plugin_registry.py` (decorator registry)
- `src/lab/models/registry.py` (framework builder with lazy import)

## CURRENT METRICS

### Legacy metrics path (global CSV)

- `src/lab/eval/metrics.py` (`append_run_metrics`)
  - parses labels for detection/confidence stats
  - reads validation metrics from run JSONs
  - appends `metrics_summary.csv`
  - generates/updates `experiment_table.md`

Integrity support:
- `scripts/check_metrics_integrity.py`
- `scripts/check_fgsm_sanity.py`

### Framework metrics path (per-run JSON)

- `src/lab/eval/framework_metrics.py`
  - sanitizes non-finite values
  - computes prediction summary stats
  - labels validation status (`missing`, `partial`, `complete`, `error`)

Unified runner emits:
- `metrics.json`
- `predictions.jsonl`
- `resolved_config.yaml`
- `run_summary.json`

## OUTPUT STRUCTURE

### Legacy/mainline output shape

- `outputs/<run_name>/...` (predict artifacts, labels)
- `outputs/<run_name>/val/metrics.json` (if validation on)
- `outputs/_intermediates/<run_name>/attacked/...`
- `outputs/_intermediates/<run_name>/defended/...`
- `outputs/_intermediates/<run_name>/_val_dataset/...`
- `outputs/metrics_summary.csv`
- `outputs/experiment_table.md`
- `outputs/<root>/plots/*.png` (week1/demo artifact scripts)

### Framework output shape

- `outputs/framework_runs/<run_name>/prepared_images/*`
- `outputs/framework_runs/<run_name>/predictions.jsonl`
- `outputs/framework_runs/<run_name>/metrics.json`
- `outputs/framework_runs/<run_name>/resolved_config.yaml`
- `outputs/framework_runs/<run_name>/run_summary.json`

## CONFIG FAMILIES IN USE

### Legacy/active families

- Alias/default family:
  - `configs/experiment_lab.yaml`
- Matrix family:
  - `configs/modular_experiments.yaml`
  - `configs/week1_stabilization_demo_matrix.yaml`
  - `configs/week1_stabilization_matrix.yaml`
  - `configs/five_attack_variants_matrix.yaml`
  - `configs/pgd_eot_quick_matrix.yaml`
  - `configs/pgd_eot_tiny_smoke_matrix.yaml`

### Framework family

- `configs/lab_framework_phase5.yaml` (currently aligned with unified runner)
- `configs/lab_framework_phase3_compat.yaml` (compat config, partially stale)
- `configs/lab_framework_skeleton.yaml` (phase scaffold)
- Canonical runtime path for framework family: `scripts/run_unified.py` (`run-one`/`sweep`)

## DUPLICATED LOGIC / TIGHT COUPLING / FRAGILE AREAS

### Duplicated / overlapping logic

- Multiple CLIs targeting similar outcomes:
  - `run_experiment.py`, `run_experiment_api.py`, `scripts/run_framework.py`, `src/lab/runners/run_experiment.py`
- Two registry systems:
  - legacy attack/defense registries vs framework plugin registries
- Alias behavior split across config and resolver code (not one source of truth).

### Tight coupling

- Gradient attack stack depends on Ultralytics model internals/output format assumptions.
- Runner behavior depends on method-signature inspection for attack model injection (`inspect.signature(...)` path in legacy runner).
- Week1/demo scripts are tightly coupled to legacy runner outputs (`metrics_summary.csv`, fixed artifact names).

### Fragile seams

- Framework registry loading currently hardcoded to specific adapter imports (manual plugin bootstrap).
- Coexisting config schemas are similar conceptually but structurally incompatible.
- Plot auto-detection checks `results/metrics_summary.csv` before `outputs/metrics_summary.csv`, risking stale-source plotting.

## KNOWN WORKING COMMANDS (DETECTED FROM CODE/DOCS)

### Legacy one-command

- `./.venv/bin/python run_experiment.py attack=blur conf=0.25`
- `./.venv/bin/python run_experiment.py --list-attacks`
- `./.venv/bin/python run_experiment.py dry_run=true`

### Framework sweep matrix

- `./.venv/bin/python scripts/run_unified.py sweep --config configs/lab_framework_phase5.yaml --attacks fgsm,pgd`
- `./.venv/bin/python scripts/run_unified.py sweep --config configs/lab_framework_phase5.yaml --attacks fgsm,pgd --runs-root outputs/custom/framework_runs --report-root outputs/custom/framework_reports`

### Week1/demo operational

- `./scripts/run_week1_stabilization.sh --profile week1-demo --mode demo`
- `bash scripts/demo/run_demo_package.sh full-demo --profile week1-demo --output-root outputs/demo-reference`
- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/week1_<timestamp>`

### Unified framework runner

- `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --config configs/lab_framework_phase5.yaml`
- `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --list-plugins`
- `PYTHONPATH=src ./.venv/bin/python src/lab/runners/run_experiment.py --config configs/lab_framework_phase5.yaml attack.name=blur`

## Verified vs Uncertain

### Verified

- Legacy runner is still the active path for week1/demo scripts.
- Unified runner is functional and emits structured JSON artifacts.
- Both legacy and framework metric systems exist concurrently.

### Uncertain / requires runtime confirmation for full certainty

- Legacy wrappers are rollback-only; production operator path remains `scripts/run_unified.py` and framework-mode `run_experiment.py`.
- Whether all framework scaffold configs (`lab_framework_skeleton.yaml`, `lab_framework_phase3_compat.yaml`) are still intended for direct execution.
