# Team Guide (Beginner + Technical): YOLO Robustness Experiment Lab

This document is written for both:
- people new to ML/engineering workflows, and
- engineers who need implementation details.

If you only read one section, read **Section 3: 10-minute Quick Start**.

For project design and loop closure goals, see `docs/LOOP_DESIGN.md`.

## Templates for new modules

Use these starter docs when creating new components:

- `docs/ATTACK_TEMPLATE.md`: step-by-step template for adding a new attack module.
- `docs/DEFENSE_TEMPLATE.md`: step-by-step template for adding a new defense module.
- `docs/PIPELINE_IN_PLAIN_ENGLISH.md`: plain-language walkthrough of the full experiment flow.

## 1) What this project does (plain English)

This project helps you answer:

**“How does YOLO object detection performance change when images are attacked and then optionally defended?”**

In each run, the framework:
1. chooses a model + dataset + settings,
2. optionally distorts images with an **attack**,
3. optionally cleans images with a **defense**,
4. runs YOLO prediction (and optional validation),
5. writes results and summary metrics.

Core code lives in `src/lab`.

## 2) Key terms (quick glossary)

- **Model**: the YOLO weights file (default: `yolo26n.pt` via `model=yolo26`).
- **Dataset**: images + labels config (default points to COCO subset).
- **Attack**: a transformation that makes images harder (blur, noise, deepfool-like).
- **Defense**: a preprocessing step intended to recover signal (median blur, denoise).
- **Confidence threshold (`conf`)**: minimum score for predicted boxes.
- **IoU threshold (`iou`)**: overlap threshold used in NMS/evaluation logic.
- **Validation**: optional mAP/precision/recall scoring pass.
- **Run**: one full experiment execution with one configuration.

## 3) 10-minute quick start (recommended path)

## Step 0: Use the project environment

Use the repo virtual environment to avoid missing package issues:

- `./.venv/bin/python --version`
- `./.venv/bin/pip install -r requirements.txt` (if needed)

## Step 1: Verify framework configuration without heavy compute

Dry run resolves config only:

- `PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml --dry-run`

You should see a resolved summary and runner config.

## Step 2: Run a small framework test experiment

- `PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml --set attack.name=blur --set runner.max_images=12 --set validation.enabled=false`

## Step 3: Check outputs

Look at:
- output run folder under `outputs/framework_runs/<run_name>/...` (or configured output root)
- `predictions.jsonl`, `metrics.json`, `run_summary.json`, `resolved_config.yaml`
- validation fields inside `metrics.json.validation` when enabled

That is enough to prove your environment and workflow are working.

## 4) Which command should I use?

Use this table (framework-first):

- **Single run with overrides**
  Use: `PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml --set attack.name=fgsm`

- **Multi-attack × multi-defense sweep**
  Use: `PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --attacks fgsm,pgd --defenses c_dog,median_preprocess --preset full --validation-enabled`

- **Automated cycle (recommended for iterative tuning)**
  Use: `PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --loop` — runs all 4 phases continuously, tracks warm-start params, writes training signal. See `docs/LOOP_DESIGN.md`.

- **List all available plugins**
  Use: `PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins`

## 5) Typical usage examples

## A) Single run with attack + defense

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=deepfool \
  --set defense.name=c_dog \
  --set validation.enabled=true
```

## B) Multi-attack × multi-defense sweep

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool,blur \
  --defenses c_dog,c_dog_ensemble,median_preprocess,jpeg_preprocess,bit_depth \
  --preset full \
  --workers auto \
  --validation-enabled
```

## C) Smoke test (fast, 8 images)

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,blur \
  --defenses median_preprocess \
  --preset smoke
```

## D) FGSM epsilon sweep

```bash
for eps in 0.002 0.004 0.008 0.016; do
  PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
    --config configs/default.yaml \
    --set attack.name=fgsm \
    --set attack.params.epsilon=${eps} \
    --set runner.run_name=fgsm_eps${eps}
done
```

## E) Automated cycle loop

```bash
PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --loop
```

Runs 4-phase cycles continuously: characterize → matrix → tune → validate. Results accumulate in `outputs/cycle_history/`. See `docs/LOOP_DESIGN.md` for full documentation.

## 6) What happens inside one run?

Pipeline:

`CLI/YAML settings → UnifiedExperimentRunner → attack plugin → defense plugin → YOLO predict/validate → outputs written`

More detail:
1. `scripts/run_unified.py run-one` loads `configs/default.yaml` + `--set` overrides.
2. `UnifiedExperimentRunner` builds the attack, defense, and YOLO model from registered plugins.
3. Attack plugin's `apply(image)` is called per image.
4. Defense plugin's `preprocess(image)` is called before prediction; `postprocess(predictions)` after.
5. `YOLOModel` runs prediction and optional mAP50 validation.
6. Outputs written to `outputs/framework_runs/<run_name>/` (metrics.json, predictions.jsonl, run_summary.json).

## 7) Output files and how to read them

Each run writes to `outputs/framework_runs/<run_name>/`:
- `metrics.json` — detection counts, avg confidence, mAP50 (schema: `framework_metrics/v1`)
- `predictions.jsonl` — per-image predictions
- `run_summary.json` — run metadata (attack, defense, model, config)

Sweep reports land in `outputs/framework_reports/<sweep_id>/`:
- `framework_run_report.md` — attack effectiveness + defense recovery table
- `framework_run_summary.csv` — same data as CSV
- `team_summary.json/.md` — high-level summary

Longitudinal tracking across cycles:
- `outputs/cycle_history/*.json` — one file per completed cycle
- `outputs/cycle_report.md` — trend table across all cycles (auto-generated)

## 8) Project layout (quick map)

- `src/lab/attacks/` — attack plugins (`*_adapter.py` files, registered via `@register_attack_plugin`)
- `src/lab/defenses/` — defense plugins (`*_adapter.py` files, registered via `@register_defense_plugin`)
- `src/lab/models/` — YOLO model wrapper
- `src/lab/runners/` — `UnifiedExperimentRunner` and CLI utilities
- `src/lab/eval/` — metrics parsing, prediction schema, derived metrics
- `src/lab/reporting/` — sweep report generation
- `configs/` — YAML configs (`default.yaml`, `coco_subset500.yaml`)
- `scripts/` — all user-facing scripts
- `docs/` — documentation

### Canonical entrypoints

- `scripts/run_unified.py run-one` — single run with `--set` overrides
- `scripts/sweep_and_report.py` — multi-attack × multi-defense sweep
- `scripts/auto_cycle.py --loop` — automated 4-phase robustness cycle

Where to add new modules:
- Attacks: `src/lab/attacks/<name>_adapter.py` (see `docs/ATTACK_TEMPLATE.md`)
- Defenses: `src/lab/defenses/<name>_adapter.py` (see `docs/DEFENSE_TEMPLATE.md`)

## 9) Known gotchas (important)

- Always use `PYTHONPATH=src ./.venv/bin/python` — not plain `python`. See `CLAUDE.md`.
- `attack.name=none` and `defense.name=none` are valid explicit values.
- Missing/empty metrics usually means YOLO produced no label files during the run.
- Validation metrics only appear when `--validation-enabled` (sweep) or `--set validation.enabled=true` (single run).

## 10) How to extend the framework (developer notes)

### Add a new attack

1. Create `src/lab/attacks/<name>_adapter.py` subclassing `BaseAttack`.
2. Implement `apply(self, image: np.ndarray, model=None, **kwargs) -> (np.ndarray, dict)`.
3. Decorate with `@register_attack_plugin("your_name")`.
4. Follow `docs/ATTACK_TEMPLATE.md` for the full checklist.

### Add a new defense

1. Create `src/lab/defenses/<name>_adapter.py` subclassing `BaseDefense`.
2. Implement `preprocess(image, **kwargs)` and `postprocess(predictions, **kwargs)`.
3. Decorate with `@register_defense_plugin("your_name")`.
4. Follow `docs/DEFENSE_TEMPLATE.md` for the full checklist.

### Key module locations

See `PROJECT_STATE.md` for a concise module map or `CLAUDE.md` for the canonical reference.

## 11) Recommended team workflow

1. Activate `.venv`: `source .venv/bin/activate`.
2. Verify environment: `PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py`.
3. Smoke test: `PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml --set attack.name=blur --set runner.max_images=4`.
4. Check outputs in `outputs/framework_runs/`.
5. Run a full sweep and review `outputs/framework_reports/`.
6. For iterative robustness improvement, run `scripts/auto_cycle.py --loop` and track `outputs/cycle_report.md`.
