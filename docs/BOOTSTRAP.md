# YOLO-Bad-Triangle — Complete Teammate Bootstrap

> Every statement in this document is anchored in the actual repository.
> File references are provided in the Evidence Appendix (Section 14).
> If something can't be verified from the repo, it is labelled **not verified**.

---

## 1. Executive Overview

**What it is.** A Python framework for adversarial robustness experiments on YOLO object
detection. You take a model, throw attacks at it, measure how much mAP50 drops, test whether
preprocessing defenses recover any of that loss, and optionally retrain the defense model using
the worst-observed attack as a training signal.

**What it is not.** A training framework for the detection model itself. YOLO weights are
treated as fixed artifacts. The only model trained here is the DPC-UNet defense (`c_dog`).

**Core loop** (`scripts/auto_cycle.py:1–44`):

```
Phase 1  Characterize   all attacks vs no defense, 32 images (slow attacks image-capped)
Phase 2  Matrix         top-N attacks × all defenses, 32 images
Phase 3  Tune           coordinate-descent over attack + defense params, 16 images
Phase 4  Validate       full 500-image run with mAP50 — the only authoritative metric
```

**Current transform order** (`src/lab/config/contracts.py:47–52`):

```
attack.apply → defense.preprocess → model.predict → defense.postprocess
```

Stored in artifacts as `semantic_order=attack_then_defense`. Legacy runs used
`defense_then_attack` — these are **not comparable** to current outputs.

**Current maturity.** Active production loop. Dedicated compute node (NUC). 264+ tests passing.
Schemas, contracts, CI all in place. Multiple remediation audits completed. Several deprecated
paths still exist in the codebase and are clearly identified in Section 9.

**What a new teammate needs to know immediately:**

1. Use `scripts/run_unified.py run-one` — never invoke `src/lab/runners/run_experiment.py` directly
2. Python must be **exactly 3.11** — a failed 3.12 venv (`.venv-py312-backup/`) exists as evidence
3. mAP50 from Phase 4 is the only number to quote — Phases 1–3 proxy metrics are for ranking only
4. `outputs/` is partially gitignored — verify with `.gitignore` before assuming anything is tracked

---

## 2. Start Here (One-Page Version)

### Read first

| File | Why |
|------|-----|
| `docs/FRESH_CLONE_SETUP.md` | First — what is and isn't in git, how to get the machine running |
| `docs/PIPELINE_IN_PLAIN_ENGLISH.md` | What a single run actually does, step by step |
| `PROJECT_STATE.md` | Current canonical plugin lists, output contracts, execution path |
| `CLAUDE.md` | Code review rules, PR discipline, high-risk surfaces — read before any PR |

### Install

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env   # edit: set DPC_UNET_CHECKPOINT_PATH if using c_dog
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

### First command

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=smoke_fgsm \
  --set runner.max_images=4
```

Then inspect `outputs/framework_runs/smoke_fgsm/` — you should see four files:
`metrics.json`, `predictions.jsonl`, `run_summary.json`, `resolved_config.yaml`.

### Folders that matter most

| Folder | Priority |
|--------|----------|
| `src/lab/` | All library code — attacks, defenses, runner, eval, reporting |
| `scripts/` | All user-facing entrypoints |
| `configs/` | All YAML configs |
| `schemas/v1/` | JSON schemas for every artifact |
| `tests/` | 264+ tests — run before and after every change |

### Ignore at first

- `notebooks/` — Colab training, not needed for daily dev
- `scripts/ops/` — contains only `.pyc` files; source was removed
- `SPEC.md`, `REMEDIATION_PLAN.md` — historical documents from a prior audit cycle
- `.venv-py312-backup/` — dead Python 3.12 environment, never activate

### First-week priorities

1. `pytest -q` — verify green
2. Run the smoke run above, inspect outputs
3. `scripts/sweep_and_report.py --list-plugins` — see all registered plugins
4. Read `scripts/auto_cycle.py` header + the `ALL_ATTACKS` / `ALL_DEFENSES` constants (lines 1–110)
5. Read `src/lab/config/contracts.py` top to bottom — every canonical constant lives here

---

## 3. Repo Map

```
YOLO-Bad-Triangle/
├── src/lab/                        ★ core library
│   ├── attacks/                    attack plugins (11 registered)
│   │   ├── framework_registry.py   registers the PluginRegistry + AdapterLoader for attacks
│   │   ├── base_attack.py          BaseAttack ABC  →  apply(image, model) → (image, meta)
│   │   └── *_adapter.py            one file per attack; decorator self-registers on import
│   ├── defenses/                   defense plugins (8 registered)
│   │   ├── framework_registry.py   same pattern as attacks
│   │   ├── base_defense.py         BaseDefense ABC  →  preprocess / postprocess hooks
│   │   └── *_adapter.py
│   ├── models/                     model adapters (yolo, faster_rcnn)
│   ├── eval/                       metrics, validation, prediction schema
│   │   ├── framework_metrics.py    summarize_prediction_metrics, validation_status, mAP50
│   │   └── prediction_schema.py    PredictionRecord TypedDict
│   ├── reporting/                  comparison, summaries, warnings
│   │   ├── framework_comparison.py FrameworkRunRecord dataclass → CSV rows
│   │   └── warnings.py             evaluate_warnings() with all warning codes
│   ├── runners/                    ★ the runner pipeline
│   │   ├── run_experiment.py       ★ DO NOT invoke directly; called by run_unified.py
│   │   ├── run_intent.py           ★ fingerprinting, skip-logic, 3-artifact check
│   │   └── cli_utils.py            YAML loading, --set override parsing
│   ├── config/contracts.py         ★ ALL canonical constants (schema IDs, enums, pipeline order)
│   ├── core/
│   │   ├── plugin_registry.py      generic decorator registry (PluginRegistry[T])
│   │   └── adapter_loader.py       lazy *_adapter.py discovery via pkgutil.iter_modules
│   └── health_checks/              artifact gate + schema validation helpers
│
├── scripts/                        ★ user-facing entrypoints
│   ├── run_unified.py              ★ CANONICAL: run-one + sweep subcommands
│   ├── sweep_and_report.py         compatibility backend for run_unified.py sweep
│   ├── auto_cycle.py               ★ CANONICAL: 4-phase autonomous loop (Phase 1/2/report regeneration call run_unified.py sweep; report regeneration requests only the core local report set)
│   ├── watch_cycle.py              live TUI monitor (rich) for running cycle
│   ├── generate_dashboard.py       HTML dashboard from framework reports
│   ├── generate_framework_report.py CSV/MD from run dirs
│   ├── cleanup_stale_runs.py       post-promotion stale dir removal
│   ├── run_training_ritual.py      signal → export → train → gate (human-triggered)
│   ├── train_from_signal.py        trains + gates new DPC-UNet checkpoint
│   ├── export_training_data.py     exports adversarial training pairs
│   ├── check_environment.py        ★ validates Python version, deps, model, dataset, DPC ckpt
│   ├── evaluate_checkpoint.py      A/B checkpoint comparison
│   ├── run_demo.py                 CI-safe demo workflow
│   ├── generate_auto_summary.py    auto-summary from run dirs
│   ├── generate_team_summary.py    team-facing Markdown summary
│   ├── generate_cycle_report.py    cycle-level report
│   ├── cw_tune.py                  one-off CW tuning script (not a main workflow)
│   ├── ci/
│   │   ├── validate_outputs.py     artifact + schema gate (used by CI)
│   │   └── check_tracked_outputs.py gitignore hygiene check
│   └── ops/                        [NO SOURCE — only stale .pyc; ignore entirely]
│
├── configs/
│   ├── default.yaml                ★ base config; override with --set
│   ├── ci_demo.yaml                1-image CI-safe run (no attack, no defense)
│   ├── coco_subset500.yaml         validation dataset config for Phase 4 mAP50
│   ├── runtime_profiles.yaml       strict / demo / fast-demo profile aliases
│   ├── defense_eval_sweep.yaml     reference matrix config; not a canonical runner input
│   └── cw_mps.yaml                 CW-specific Metal/MPS config
│
├── schemas/v1/                     JSON schemas for all artifact types
│   ├── framework_metrics.schema.json
│   ├── framework_run_summary.schema.json
│   ├── warnings.schema.json
│   ├── cycle_summary.schema.json
│   ├── headline_metrics_csv.schema.json
│   ├── per_class_vulnerability_csv.schema.json
│   ├── legacy_compat_csv.schema.json
│   ├── system_health_summary.schema.json
│   └── demo_manifest.schema.json
│
├── tests/                          264+ tests; pytest config in pyproject.toml
│   ├── conftest.py                 adds repo root to sys.path for script imports
│   ├── fixtures/                   schema fixtures for contract tests
│   └── test_*.py                   one file per subsystem (see Section 10)
│
├── docs/
│   ├── BOOTSTRAP.md                ★ this file — complete system overview
│   ├── FRESH_CLONE_SETUP.md        ★ practical setup for a new machine
│   ├── TEAM_MANUAL.md              full reference: all scripts, attacks, defenses, NUC ops
│   ├── TEAM_GUIDE.md               quickest onboarding commands
│   ├── PIPELINE_IN_PLAIN_ENGLISH.md narrative walkthrough of one run
│   ├── LOOP_DESIGN.md              4-phase cycle design and warm-start carry-forward
│   ├── ATTACK_TEMPLATE.md          step-by-step: add a new attack plugin
│   ├── DEFENSE_TEMPLATE.md         step-by-step: add a new defense plugin
│   ├── LOCAL_CONFIG_POLICY.md      .env and local config governance
│   └── audit_findings.md           remediation tracking (historical)
│
├── outputs/                        runtime artifacts (partially gitignored)
│   ├── framework_runs/             GITIGNORED — per-run output dirs
│   ├── framework_reports/          tracked — sweep CSV/MD/JSON reports
│   ├── cycle_history/              tracked — per-cycle JSON records (authoritative)
│   ├── cycle_state.json            GITIGNORED — live cycle state (may be stale)
│   ├── cycle_training_signal.json  GITIGNORED — training signal
│   └── dashboard.html              tracked via gitignore exception (!outputs/dashboard.html)
│
├── coco/val2017_subset500/         GITIGNORED — local dataset images + labels
├── yolo26n.pt, yolo11n.pt, ...     GITIGNORED — YOLO weights in repo root
├── dpc_unet_*.pt                   GITIGNORED — DPC-UNet checkpoints
│
├── README.md                       canonical command reference + output map
├── PROJECT_STATE.md                ★ current plugin lists and output contracts
├── CLAUDE.md                       ★ code review rules, PR discipline, high-risk surfaces
├── pyproject.toml                  pytest, ruff, mypy configuration
├── requirements.txt                pinned runtime deps
├── requirements-dev.txt            test/lint deps
└── .env.example                    template — copy to .env, never commit .env
```

---

## 4. Architecture and Execution Flow

### Subsystem relationships

```
User / Operator
       │
       ├─── scripts/run_unified.py run-one     ──┐
       ├─── scripts/run_unified.py sweep       ──┼── public sweep surfaces
       ├─── scripts/sweep_and_report.py          ├── invoke run_experiment.py
       └─── scripts/auto_cycle.py --loop       ──┘   via subprocess
                                                │
                       src/lab/runners/run_experiment.py
                       (UnifiedExperimentRunner)
                                |
              ┌─────────────────┼─────────────────┐
              │                 │                  │
        attack plugin     defense plugin      model adapter
        (BaseAttack)      (BaseDefense)       (BaseModel)
        via AdapterLoader  via AdapterLoader   via framework_registry
              │                 │                  │
              └─────────────────┴──────────────────┘
                                │
                    per-image loop  (tqdm)
                    ─────────────────────────────────────
                    image = cv2.imread(path)
                    attacked, meta = attack.apply(image, model)
                    preprocessed, meta = defense.preprocess(attacked)
                    write preprocessed → outputs/<run_name>/images/
                    ─────────────────────────────────────
                                │
                    model.predict(prepared_images)
                    defense.postprocess(predictions)
                                │
                    ┌───────────┴────────────┐
                    │                        │
               prediction metrics       if validation.enabled:
               (fast, always)           model.validate() → mAP50
                    │                        │
                    └───────────┬────────────┘
                                │
               write 3 required artifacts atomically:
               metrics.json  predictions.jsonl  run_summary.json
               + resolved_config.yaml
```

### Plugin discovery (how attacks and defenses load)

Source: `src/lab/core/adapter_loader.py:33–47`

1. First call to `build_attack_plugin(name)` triggers `AdapterLoader._load()`
2. Loader scans `lab.attacks` for modules whose name ends in `_adapter`
3. Each `*_adapter.py` is imported — the `@register_attack_plugin(...)` decorator fires as a side-effect, storing the class in `PluginRegistry._store`
4. `build(name)` looks up the alias, instantiates with params kwargs

**No central list to maintain.** A new `src/lab/attacks/myattack_adapter.py` with `@register_attack_plugin("myattack")` is automatically discoverable. Duplicate alias → `ValueError` at import time.

### Skip / resume logic

Source: `src/lab/runners/run_intent.py:87–200`

Before any run starts, `check_run_resume()` compares a stored fingerprint in `run_summary.json`
against the intended fingerprint. The fingerprint covers:

- SHA256 of the normalized config YAML
- attack signature (name + params + objective fields)
- defense signature (name + params)
- SHA256 of the YOLO model checkpoint
- SHA256(s) of defense checkpoint(s) (e.g. DPC-UNet)
- seed, validation_enabled, reporting_context

If all three artifacts exist and fingerprints match → **skip** (return immediately).
If artifacts are partial → **re-run** (overwrite).
If absent → **run** normally.

This is what makes `auto_cycle --loop` fully resumable after crash or interruption.

### Step-by-step execution trace (single run)

```
1. User invokes scripts/run_unified.py run-one --config ... --set ...
2. run_unified.py parses args, applies --set overrides to config dict
3. run_unified.py invokes run_experiment.py via subprocess
   (build_run_experiment_command() in cli_utils.py builds the command)
4. run_experiment.py resolves run_dir = output_root / run_name
5. run_experiment.py calls check_run_resume() → skip / rerun / run
6. run_experiment.py builds attack, defense, model instances via plugin registries
7. run_experiment.py collects images (sorted, truncated to max_images)
8. Per-image loop:
   a. attacked_image, attack_meta  = attack.apply(image, model)
   b. preprocessed, defense_meta  = defense.preprocess(attacked_image)
   c. write preprocessed image → run_dir/images/
9. model.predict(prepared_images) → PredictionRecord list
10. defense.postprocess(predictions) → filtered predictions
11. summarize_prediction_metrics() → confidence/count dict
12. if validation.enabled: model.validate() → mAP50, precision, recall
13. Write atomically:
    - metrics.json        (schema: framework_metrics/v1)
    - predictions.jsonl   (one JSON object per image)
    - run_summary.json    (schema: framework_run_summary/v1; includes provenance + fingerprints)
    - resolved_config.yaml
```

---

## 5. Canonical Workflows

### A. Single experiment run

**Purpose:** Run one attack + defense combination on N images.

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set defense.name=median_preprocess \
  --set runner.run_name=my_run \
  --set runner.max_images=8
```

**Inputs:** YAML config, YOLO weights, images in `data.source_dir`
**Outputs:** `outputs/framework_runs/<run_name>/` (3-artifact contract + `resolved_config.yaml`)
**Gotchas:** `PYTHONPATH=src` required; `run_name` autogenerates a timestamp if omitted;
re-runs skipped if fingerprint matches existing run

### B. Matrix sweep

**Purpose:** Run all attack × defense combinations; generate comparison report.

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --attacks fgsm,pgd,deepfool \
  --defenses c_dog,median_preprocess \
  --preset smoke \
  --workers 1
```

**Inputs:** Same as single run; `--attacks`, `--defenses`, `--preset` control scope
**Outputs:** `outputs/framework_reports/<sweep_id>/` (CSV, MD, JSON)
**Gotchas:** `--workers 1` recommended on GPU/memory-constrained machines;
without `--update-pages`, the sweep does NOT overwrite `docs/index.html`

### C. Autonomous 4-phase cycle

**Purpose:** Characterize → matrix → tune → validate → repeat.

```bash
PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --loop
# In a second pane:
PYTHONPATH=src ./.venv/bin/python scripts/watch_cycle.py
```

**State files:** `outputs/cycle_state.json` (live, gitignored),
`outputs/cycle_history/<id>.json` (per-cycle, tracked)

**Gotchas:**
- Uses `fcntl.flock` lock at `outputs/.cycle.lock` — run only one instance
- Python interpreter hardcoded to `.venv/bin/python` (`auto_cycle.py:78`)
- `jpeg_attack`, `c_dog_ensemble`, `random_resize` excluded from catalogs (see Section 9)
- Slow attacks (`square`, `eot_pgd`, `dispersion_reduction`, `deepfool`) are image-capped in Phase 4

### D. Training pipeline (human-triggered)

**Purpose:** Fine-tune DPC-UNet using the worst observed attack as training signal.

```bash
# Prerequisite: outputs/cycle_training_signal.json must be < 24h old
PYTHONPATH=src ./.venv/bin/python scripts/run_training_ritual.py --dry-run
PYTHONPATH=src ./.venv/bin/python scripts/run_training_ritual.py
```

**Gate:** `new_mAP50 − baseline_mAP50 ≥ −0.005` → promote. Otherwise keep current checkpoint.

**After promotion:** Update `DPC_UNET_CHECKPOINT_PATH` in `.env` on every machine.
Then run `cleanup_stale_runs.py --dry-run` to preview stale run dirs.

### E. Validate environment

```bash
# Basic check (no c_dog requirement)
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py

# Full check including DPC-UNet checkpoint
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py --require-cdog
```

Checks: Python 3.11, ultralytics==8.4.23, torch==2.5.1, torchvision==0.20.1,
torch runtime health, YOLO model, DPC checkpoint, dataset path + label pairing.

### F. Quality gate (before every PR)

```bash
./.venv/bin/ruff check src tests scripts
./.venv/bin/mypy
./.venv/bin/pytest -q
```

---

## 6. Setup and Environment Guide

### Prerequisites

- **Python 3.11.x** — strictly required. 3.12 was tried and abandoned (`.venv-py312-backup/` exists).
- CUDA GPU strongly recommended for Phase 4 and white-box attack runs. CPU works for smoke runs.

### Installation

```bash
git clone <repo-url>
cd YOLO-Bad-Triangle

python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt       # pinned runtime stack
pip install -r requirements-dev.txt   # pytest, mypy, ruff

cp .env.example .env
# .env should contain:
#   PYTHONPATH=src
#   DPC_UNET_CHECKPOINT_PATH=<path to dpc_unet_adversarial_finetuned.pt>
```

### Pinned versions (`requirements.txt`)

| Package | Version |
|---------|---------|
| `ultralytics` | `==8.4.23` |
| `torch` | `==2.5.1` |
| `torchvision` | `==0.20.1` |
| `numpy` | `>=1.23.5,<2.0.0` (no numpy 2.x) |
| `opencv-python` | `>=4.8.0,<5.0.0` |
| `pandas` | `>=1.5.0,<2.3.0` |

### Required local assets (not in git)

| Asset | Location | How to obtain |
|-------|----------|--------------|
| YOLO weights | `yolo26n.pt` in repo root (default config) | `from ultralytics import YOLO; YOLO("yolo26n.pt")` triggers download |
| COCO val2017 subset | `coco/val2017_subset500/images/` + `labels/` | Manual download — see `docs/FRESH_CLONE_SETUP.md` |
| DPC-UNet checkpoint | Path in `DPC_UNET_CHECKPOINT_PATH` | Obtain from team; current recommended: `dpc_unet_adversarial_finetuned.pt` |

### Common setup failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `check_environment.py` fails Python version | Wrong venv | `python3.11 -m venv .venv` |
| torch/torchvision mismatch | pip resolved wrong versions | `pip install -r requirements.txt` exactly |
| `YOLO model missing` | `.pt` not in repo root | Place `yolo26n.pt` there or use `--model-path` |
| `Dataset labels missing` | images present, no labels dir | Add `coco/val2017_subset500/labels/*.txt` |
| `c_dog` crash on startup | `DPC_UNET_CHECKPOINT_PATH` unset or wrong | Set in `.env` or shell |
| Any `src/lab/...` ImportError | `PYTHONPATH` not set | `export PYTHONPATH=src` or add to `.env` |

---

## 7. Config and Control Surface

### How configuration works

1. Start with a YAML file (default: `configs/default.yaml`)
2. Apply `--set key.subkey=value` overrides (dot-path notation, repeatable)
3. Result dict passed to `UnifiedExperimentRunner`

Source: `src/lab/runners/cli_utils.py` — `load_yaml_mapping`, `apply_override`

### Key YAML sections (`configs/default.yaml`)

```yaml
model:
  name: yolo             # "yolo" or "torchvision_frcnn" (frcnn has no mAP50 support)
  params:
    model: yolo26n.pt    # YOLO weights filename (searched in repo root)

data:
  source_dir: coco/val2017_subset500/images

attack:
  name: none             # any registered alias, or "none" for baseline
  params: {}             # attack-specific: epsilon, steps, n_queries, etc.

defense:
  name: none
  params: {}

predict:
  conf: 0.5              # YOLO confidence threshold (affects detection counts)
  iou: 0.7
  imgsz: 640

validation:
  enabled: false         # set true to get mAP50 — required for Phase 4
  dataset: configs/coco_subset500.yaml

runner:
  seed: 42
  max_images: 8          # 0 = use all images; 32 = smoke; 500 = Phase 4
  output_root: outputs/framework_runs
  run_name: baseline_smoke
```

### Highest-impact knobs

| Knob | Effect |
|------|--------|
| `attack.name` | Which attack to apply |
| `defense.name` | Which defense to apply |
| `runner.max_images` | Image count — controls wall-clock time and result quality |
| `validation.enabled` | Whether to run mAP50 — adds significant time |
| `runner.seed` | Reproducibility — propagated to attack and model |
| `runner.run_name` | Output directory name — also part of skip-logic identity |
| `predict.conf` | Detection threshold — affects all detection-count metrics |

### Attack parameter spaces (from `auto_cycle.py:122–173`)

Auto-cycle uses coordinate descent over these ranges:

| Attack | Tuned params |
|--------|-------------|
| `fgsm` | `epsilon` (log scale, 0.001–0.3) |
| `pgd` | `epsilon` (log), `steps` (int, 5–80) |
| `deepfool` | `epsilon` (log), `steps` (int, 10–200) |
| `eot_pgd` | `epsilon`, `alpha`, `eot_samples` |
| `square` | `eps` (log), `n_queries` (int, 50–500) |
| `blur` | `kernel_size` (odd int, 3–51) |

---

## 8. Important Files Cheat Sheet

| File | What it does | Risk if changed |
|------|-------------|----------------|
| `src/lab/runners/run_experiment.py` | Core pipeline — every run goes through here | **CRITICAL** — ML results, artifacts |
| `src/lab/runners/run_intent.py` | Fingerprinting + skip logic | **CRITICAL** — silent skip or re-run bugs |
| `src/lab/config/contracts.py` | All canonical constants | HIGH — readers depend on exact values |
| `src/lab/attacks/base_attack.py` | Attack interface contract | HIGH — breaks all plugins |
| `src/lab/defenses/base_defense.py` | Defense interface contract | HIGH — breaks all plugins |
| `src/lab/eval/framework_metrics.py` | Metric computation | HIGH — all numbers change |
| `src/lab/reporting/framework_comparison.py` | CSV row builder | MEDIUM — report schema |
| `src/lab/reporting/warnings.py` | Warning generation | LOW — additive |
| `src/lab/core/plugin_registry.py` | Registry data structure | LOW |
| `src/lab/core/adapter_loader.py` | Lazy plugin loader | LOW |
| `scripts/auto_cycle.py` | 4-phase orchestrator (stateful) | **CRITICAL** — stateful, resumable |
| `scripts/sweep_and_report.py` | Matrix sweep | MEDIUM |
| `scripts/run_unified.py` | CLI entrypoint | LOW |
| `configs/default.yaml` | Default run config | MEDIUM — affects all runs |
| `configs/ci_demo.yaml` | CI must stay green | LOW |
| `schemas/v1/*.schema.json` | Artifact contracts | MEDIUM — requires fixture updates |
| `tests/fixtures/` | Schema test fixtures | MEDIUM — must match schemas |

---

## 9. Legacy, Duplicate, and Confusing Areas

### CANONICAL NOW

- `scripts/run_unified.py run-one` — single run
- `scripts/sweep_and_report.py` — matrix sweep
- `scripts/auto_cycle.py --loop` — autonomous loop
- Transform order `attack_then_defense` (`contracts.py:44`)

### LEGACY / AVOID

- **`scripts/ops/`** — only `.pyc` files (Python 3.12, cpython-312), no source. The scripts were
  removed. Do not reference. Evidence: `find scripts/ops -name "*.py"` returns nothing.
- **`.venv-py312-backup/`** — dead Python 3.12 environment. Never activate.
- **`LEGACY_PIPELINE_TRANSFORM_ORDER`** — constant in `contracts.py:53–58` and
  `auto_cycle.py:91–95` identifies **old artifacts** with reversed order (`defense_then_attack`).
  Any artifact with `semantic_order=defense_then_attack` is from a prior era and is **not
  comparable** to current outputs.
- **`SPEC.md`** — dated 2026-03-28; references in-progress delegated Phase 4 runs. Historical only.
- **`REMEDIATION_PLAN.md`** — dated 2026-03-29; most items resolved. Historical reference.
- **`MESSAGES_FOR_NUC_CLAUDE.md` / `MESSAGES_FOR_MAC_CLAUDE.md`** — runtime coordination files;
  gitignored; currently empty. Not a workflow to replicate.

### REGISTERED BUT EXCLUDED FROM AUTO-CYCLE

Evidence: `auto_cycle.py:100–108`, `PROJECT_STATE.md`

| Plugin | Type | Reason noted in source |
|--------|------|------------------------|
| `jpeg_attack` | Attack | "no-op behavior under current defaults" |
| `c_dog_ensemble` | Defense | "underperforming single c_dog" |
| `random_resize` | Defense | "inherent mAP50 cost (−0.25) exceeds any attack-recovery benefit" |
| `confidence_filter` | Defense | Registered; not in catalog; no comment — **unknown status** |
| `fgsm_center_mask`, `fgsm_edge_mask` | Attacks | Registered; not in `ALL_ATTACKS`; usable via manual `--set` |
| `cw` | Attack | In `sweep_and_report.py`'s `CANONICAL_ATTACKS_ALL`; not in `auto_cycle.py`'s `ALL_ATTACKS` |

### KNOWN GAPS AND CONFUSING AREAS

**`setup_assets.sh`** references `scripts/convert_coco_to_yolo.py` at line 54. That script does
not exist in the current tree. The dataset download steps work; the label generation step breaks.
A teammate following this script will hit a file-not-found error. Use `docs/FRESH_CLONE_SETUP.md`
instead for the current authoritative setup path.

**`run_unified.py sweep` subcommand** is the canonical public sweep surface and forwards via
subprocess to `sweep_and_report.py` for backend compatibility. It does not re-implement sweep
logic. Evidence: `run_unified.py`.

**`outputs/` gitignore policy** uses negation rules (e.g., `!outputs/dashboard.html`). Easy to
accidentally commit generated files or fail to commit tracked ones. Check `.gitignore` directly.

**`per_class` key type** — the metrics writer (`framework_metrics.py`) stores keys as strings
(`"0"`, `"42"`). Readers in `framework_comparison.py` cast with `int(k)`. This is documented in
`contracts.py:31–33` but any new reader not aware will silently drop all per-class data.

**Mypy scope** — `pyproject.toml` only type-checks `src/lab/eval`, `src/lab/reporting`,
`src/lab/runners`. Attack plugins, defense plugins, models, and all scripts are untyped in CI.

**`auto_cycle.py`** hardcodes `PYTHON = REPO / ".venv" / "bin" / "python"` at line 78.
If the venv is named differently or located elsewhere, the cycle will silently use the wrong
interpreter. Always use `.venv` at repo root.

---

## 10. Validation and Safe Change Workflow

### Before touching anything

```bash
pytest -q    # must be green (264+) before you start
```

### After any change

```bash
ruff check src tests scripts
mypy
pytest -q
```

### If you changed a plugin or the runner

```bash
# Run a minimal end-to-end smoke check
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=sanity_fgsm \
  --set runner.max_images=4

ls outputs/framework_runs/sanity_fgsm/
# Expect: metrics.json  predictions.jsonl  run_summary.json  resolved_config.yaml  images/
```

### If you changed reporting or schemas

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/validate_outputs.py \
  --output-root outputs/framework_runs/sanity_fgsm \
  --contract-name framework_run \
  --framework-run-dir outputs/framework_runs/sanity_fgsm \
  --legacy-compat-csv tests/fixtures/schema/valid/legacy_compat.csv \
  --require-schema
```

### Key test files by subsystem

| Test file | Covers |
|-----------|--------|
| `test_auto_cycle_and_dashboard.py` | Auto-cycle + dashboard |
| `test_framework_attack_plugins.py` | All attack plugins |
| `test_framework_defense_plugins.py` | All defense plugins |
| `test_framework_metrics.py` | Metric computation |
| `test_framework_output_contract.py` | 3-artifact contract |
| `test_framework_reporting.py` | Reporting pipeline |
| `test_schema_contracts.py` | JSON schema validation |
| `test_run_unified.py` | run_unified CLI |
| `test_sweep_and_report.py` | Sweep + --update-pages logic |
| `test_cleanup_stale_runs.py` | Stale run removal |
| `test_training_ritual.py` | Training pipeline wrapper |
| `test_watch_cycle.py` | watch_cycle TUI helpers |
| `test_check_environment.py` | check_environment.py |

---

## 11. Outputs and Artifacts

### Per-run outputs (`outputs/framework_runs/<run_name>/`)

GITIGNORED. Three files are required for a run to be considered complete:

| File | Schema | Contents |
|------|--------|----------|
| `metrics.json` | `framework_metrics/v1` | prediction metrics, validation metrics, per-class data |
| `predictions.jsonl` | — | one JSON object per image: boxes, scores, class_ids |
| `run_summary.json` | `framework_run_summary/v1` | model, attack, defense, seed, provenance, fingerprints, reporting_context |

Also written: `resolved_config.yaml`, `images/` (prepared images), optionally `experiment_summary.json`.

### Sweep/report outputs (`outputs/framework_reports/<sweep_id>/`)

TRACKED in git. Produced by `generate_framework_report.py`:
- `framework_run_report.md` — human-readable comparison
- `framework_run_summary.csv` — machine-readable rows (one per run)
- `team_summary.json` / `team_summary.md`

### Cycle outputs

| File | Tracked | Contents |
|------|---------|---------|
| `outputs/cycle_history/<id>.json` | Yes | complete per-cycle record including phase4_results |
| `outputs/cycle_state.json` | No | live state — may be stale; prefer cycle_history |
| `outputs/cycle_warm_start.json` | No | carry-forward params for next cycle |
| `outputs/cycle_training_signal.json` | No | worst attack + weakest defense for retraining |
| `outputs/dashboard.html` | Yes (exception) | compatibility mirror of the latest generated dashboard |

`auto_cycle.py` report regeneration intentionally requests only the local/core
report bundle: `framework_run_report.md`, `framework_run_summary.csv`, and the
local `dashboard.html` under the explicit report root. Optional extras remain
available on manual sweeps, and `scripts/sweep_and_report.py` remains the
compatibility backend behind `run_unified.py sweep`.

### Which artifacts matter for downstream work

- **Decisions and gate comparisons:** `cycle_history/<id>.json` → `phase4_results`
- **Report generation:** `framework_run_summary.csv`
- **Training trigger:** `cycle_training_signal.json`
- **Training verdict:** `outputs/training_runs/<id>/training_manifest.json`

---

## 12. Gaps and Risks

| Gap | Severity | Detail |
|-----|----------|--------|
| `setup_assets.sh` references missing `convert_coco_to_yolo.py` | HIGH | Line 54 calls a script that doesn't exist; dataset setup breaks at label generation. Use `FRESH_CLONE_SETUP.md` instead. |
| DPC-UNet checkpoint not obtainable from repo | HIGH | No download link or generation script. New teammate must receive file directly. |
| Mypy only covers 3 of 6 packages | MEDIUM | Attack/defense/model code is untyped in CI; type errors in plugins won't be caught. |
| `scripts/ops/` zombie directory | LOW | Only `.pyc` files, no source. Confusing; safe to ignore. |
| `confidence_filter` defense status unclear | LOW | Registered, not in catalog, no comment. Ask owner before relying on it. |
| `per_class` key type inconsistency | MEDIUM | Writer = str keys, readers cast to int. Documented in `contracts.py:31–33` but future readers may miss it. |
| `auto_cycle.py` hardcodes `.venv` path | MEDIUM | Won't work with non-standard venv name or location. |
| Colab retraining workflow partially documented | LOW | `LOOP_DESIGN.md` describes a Colab cell that must be added manually to the notebook. |

---

## 13. First 10 Tasks for a New Teammate

| # | Task | Why |
|---|------|-----|
| 1 | Read `docs/FRESH_CLONE_SETUP.md`, get machine set up | Nothing else works until the assets are in place |
| 2 | `check_environment.py` — all checks must pass | Diagnoses 90% of setup issues immediately |
| 3 | `pytest -q` — 264+ must pass | Confirms your environment matches the rest of the team |
| 4 | Run a 4-image smoke run, inspect every output file | Understand what a complete run looks like on disk |
| 5 | `sweep_and_report.py --list-plugins` | See all registered attacks and defenses with their aliases |
| 6 | Read `src/lab/config/contracts.py` top to bottom | Every canonical constant in the system; 15 min now saves hours later |
| 7 | Run a 2-attack × 1-defense smoke sweep, read the CSV report | See matrix output vs single run |
| 8 | Read `scripts/auto_cycle.py` header + `ALL_ATTACKS` / `ATTACK_PARAM_SPACE` constants | Understand what the loop does and what it deliberately excludes |
| 9 | Read `CLAUDE.md` before touching any file intended for a PR | The review rules are strict and enforced |
| 10 | Make a tiny isolated change, run the full quality gate | Confirm your change → test → CI path works end to end |

---

## 14. Evidence Appendix

| Claim | Source |
|-------|--------|
| Canonical entrypoint = `run_unified.py run-one` | `PROJECT_STATE.md:7`, `contracts.py:40–41` |
| Transform order = attack then defense | `contracts.py:47–52`, `README.md:24–29`, `PIPELINE_IN_PLAIN_ENGLISH.md:24` |
| Python 3.11 strictly required | `requirements.txt:3`, `check_environment.py:22`, `ci.yml:22` |
| Pinned versions | `requirements.txt:7–13`, `check_environment.py:24–26` |
| Three-artifact contract | `run_intent.py:87`, `sweep_and_report.py:70`, `auto_cycle.py:81` |
| Plugin discovery via `*_adapter.py` | `adapter_loader.py:37–42` |
| Duplicate alias → ValueError | `plugin_registry.py:35–40` |
| Active auto-cycle attack catalog | `auto_cycle.py:100–103` |
| `jpeg_attack` excluded ("no-op") | `auto_cycle.py:103` comment |
| `c_dog_ensemble` excluded ("underperforming") | `auto_cycle.py:106` comment |
| `random_resize` excluded ("−0.25 mAP50 cost") | `auto_cycle.py:108` comment |
| Phase 4 image caps for slow attacks | `auto_cycle.py:186–194` |
| Coordinate descent parameter spaces | `auto_cycle.py:122–173` |
| Skip logic fingerprint fields | `run_intent.py:122–139` |
| Mypy scope = 3 packages | `pyproject.toml:22–28` |
| CI pipeline = lint + mypy + pytest + demo + artifact validation | `.github/workflows/ci.yml:32–109` |
| `per_class` keys written as strings | `contracts.py:31–33` comment |
| `setup_assets.sh` calls missing script | `setup_assets.sh:54` |
| `scripts/ops/` — pyc only, no source | filesystem: `find scripts/ops -name "*.py"` returns empty |
| `auto_cycle.py` hardcodes `.venv` path | `auto_cycle.py:78` |
| `outputs/dashboard.html` tracked via negation | `.gitignore:23` |
| `framework_runs/` gitignored | `.gitignore:18` |
| Legacy transform order constant | `contracts.py:53–58` |

---

## 15. Teammate-Ready Build Plan

### Phase 1: Observer (Days 1–5)

**Goal:** Understand the system without touching anything critical.

- Get environment green: `check_environment.py` + `pytest -q`
- Run a smoke run, a smoke sweep, and read every output file on disk
- Read `src/lab/config/contracts.py` and `src/lab/runners/run_intent.py` fully
- Read `CLAUDE.md` — all of it. The review posture is non-negotiable.
- Branch for every experiment. Never commit directly to `main`.

**Safest subsystems:** `src/lab/reporting/warnings.py` (add warning codes),
`src/lab/eval/framework_metrics.py` (add derived metrics). Both well-tested and isolated.

---

### Phase 2: Small Contributor (Days 6–20)

**Goal:** Make a change, get it reviewed, merge safely.

**Good first contributions:**
- Add a new **attack plugin** — create `src/lab/attacks/<name>_adapter.py`,
  inherit `BaseAttack`, register with `@register_attack_plugin`. Follow `ATTACK_TEMPLATE.md` exactly.
- Add a new **warning code** in `src/lab/reporting/warnings.py` with a focused test.
- Fix a specific bug with the smallest possible diff — no surrounding cleanup.

**Conventions that are enforced:**
- One concern per PR; state it in the PR description
- State explicitly what the PR does NOT address
- Atomic writes: `tmp = path.with_suffix(".tmp"); tmp.write_text(content); os.replace(tmp, path)`
- Test style: `unittest.TestCase`, `tempfile.TemporaryDirectory`, `mock.patch.object` for globals
- No new abstraction unless shared across ≥2 callers in the same PR

**Areas requiring owner guidance before touching:**
- `scripts/auto_cycle.py` — stateful and resumable; bugs silently corrupt cycle state
- `src/lab/runners/run_experiment.py` — any change affects all ML results
- `src/lab/runners/run_intent.py` — bugs silently skip or re-run experiments
- `schemas/v1/` — requires fixture updates and deliberate compatibility note

---

### Phase 3: Confident Contributor (Day 21+)

**Goal:** Modify core systems safely with full context.

At this point you should be able to:
- Explain why `semantic_order=attack_then_defense` matters for comparing artifacts
- Explain what `check_run_resume()` does before any experiment starts
- Know which auto-cycle attacks are image-capped and why
- Know the difference between `diagnostic` and `authoritative` authority rows
- Have run at least one full 4-phase cycle and read the resulting `cycle_history/` artifact

Good Phase 3 contributions:
- Extend the training pipeline to support additional defense architectures
- Wire training into `auto_cycle` with an explicit flag (currently human-triggered only)
- Add a new model adapter
- Extend the reporting pipeline with a new output format
