# YOLO-Bad-Triangle — Team Manual

> **Start here.** This is the top-level reference for every teammate. Targeted guides
> ([FRESH_CLONE_SETUP.md](FRESH_CLONE_SETUP.md),
> [PIPELINE_IN_PLAIN_ENGLISH.md](PIPELINE_IN_PLAIN_ENGLISH.md),
> [LOOP_DESIGN.md](LOOP_DESIGN.md),
> [TEAM_GUIDE.md](TEAM_GUIDE.md)) go deeper on specific topics — link back here when
> you need the full picture.

---

## 1. What Is This Repo?

**YOLO-Bad-Triangle** is an adversarial robustness testing framework for YOLO object
detection models. It answers three questions:

1. **Which attacks actually reduce detection quality?** (measured by mAP50 drop)
2. **Which defenses recover performance?** (measured by mAP50 recovery %)
3. **Does adversarial fine-tuning make the model more robust?** (gated by delta vs baseline)

**Framework-first rule:** all execution goes through the canonical entrypoints
(`run_unified.py`, `sweep_and_report.py`, `auto_cycle.py`). Do not call
`src/lab/runners/run_experiment.py` directly.

---

## 2. Setup

Start with [FRESH_CLONE_SETUP.md](FRESH_CLONE_SETUP.md) if this is a brand-new
clone or a new teammate machine. That file answers the practical questions this
manual does not repeat in full:

- which runtime assets are in Git
- which ones are not
- where `yolo26n.pt` should live
- where the current DPC checkpoint should live
- how the `coco/val2017_subset500/` tree should look

### Prerequisites

- Python 3.11+
- `ffmpeg`
- local YOLO weights such as `yolo26n.pt`
- local dataset files under `coco/val2017_subset500/`
- local DPC checkpoint if you plan to run `c_dog`

### Bootstrap

```bash
python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
```

Recommended local convention:

- place `yolo26n.pt` in the repo root
- place `dpc_unet_adversarial_finetuned.pt` in the repo root
- set `DPC_UNET_CHECKPOINT_PATH=$PWD/dpc_unet_adversarial_finetuned.pt`

### Required `.env` keys

| Key | Required | Purpose |
|-----|----------|---------|
| `PYTHONPATH` | Yes | Must include `src/` |
| `DPC_UNET_CHECKPOINT_PATH` | Required for `c_dog` only | Path to `dpc_unet_adversarial_finetuned.pt` or another local DPC checkpoint |

### Verify setup

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py --require-cdog
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/default.yaml --dry-run
./.venv/bin/pytest -q
```

---

## 3. Core Concepts

### The Four-Phase Cycle

The orchestrator (`scripts/auto_cycle.py`) structures every experiment cycle into four
phases. **Only Phase 4 produces mAP50 — the authoritative metric.**

| Phase | Name | What it does | Metric used |
|-------|------|-------------|-------------|
| 1 | Characterize | Smoke-tests each attack on 8 images | Detection confidence drop |
| 2 | Matrix | Full attack × defense cross-product | Confidence + detection count |
| 3 | Tune | Re-runs top attacks with refined params | Confidence |
| 4 | Validate | Top pairs on full dataset (500 img) | **mAP50** (authoritative) |

Phases 1–3 use proxy metrics. Their numbers **cannot** be compared to Phase 4
mAP50 values. Never mix them in analysis.

### Run Naming Convention

```
<model>__<attack>__<defense>

dpc_unet__none__none          # baseline (no attack, no defense)
dpc_unet__square__none        # attack only
dpc_unet__square__c_dog       # attack + defense
```

### Three-Artifact Completion Contract

A run directory is **complete** only when all three files exist:

```
outputs/framework_runs/<run_name>/
  metrics.json        # numeric results
  predictions.jsonl   # per-image predictions
  run_summary.json    # provenance, config, fingerprint
```

Any directory missing one or more of these is treated as **in-progress** and will be
skipped by cleanup utilities, skip logic, and reporting. Never delete a partial run
directory manually — let `cleanup_stale_runs.py` handle it.

### Authority Levels

Every row in a report carries an `authority` field:

| Value | Source | Used for |
|-------|--------|---------|
| `authoritative` | Phase 4 full-dataset mAP50 runs | Decisions, gate comparisons |
| `diagnostic` | Phase 1/2/3 smoke or partial runs | Informational only |

The reporting pipeline prefers authoritative rows. If only diagnostic rows exist,
certain warnings are suppressed to avoid false positives.

### mAP50 — The Canonical Metric

mAP50 (mean Average Precision at IoU 0.5) is the only metric used for:

- Training gate decisions (delta ≥ −0.005 passes)
- Checkpoint promotion comparisons
- Defense recovery calculations

Confidence and detection count are **proxy metrics** used during Phases 1–3 only.

---

## 4. Attacks

Attacks are registered as plugins via `@register_attack_plugin()` in `src/lab/attacks/`.
Pass `--set attack.name=<alias>` to any runner.

| Alias | Type | Description |
|-------|------|-------------|
| `square` | Black-box | Square attack — bounded L∞ random search |
| `deepfool` | White-box | DeepFool — minimal L2 perturbation |
| `fgsm` | White-box | Fast Gradient Sign Method — single-step L∞ |
| `pgd` | White-box | PGD — multi-step iterative L∞ |
| `cw` | White-box | Carlini-Wagner whole-image L2 optimization |
| `eot_pgd` | White-box | PGD with random transform averaging for physical-style robustness |
| `dispersion_reduction` | White-box | Iterative perturbation that reduces detector response concentration |
| `blur` | Spatial | Gaussian blur degradation |
| `jpeg_attack` | Spatial | JPEG compression artifact attack |
| `fgsm_center_mask` | Localized | FGSM constrained to a central elliptical region |
| `fgsm_edge_mask` | Localized | FGSM constrained to high-gradient edge regions |

Runner note: `attack.name=none` is accepted as the baseline sentinel even though
there is no dedicated `none` attack plugin.

There is currently **no** universal printable adversarial-patch optimizer in the
canonical attack registry. The localized FGSM attacks are image-local masked
perturbations, not a persistent physical patch artifact.

Key attack parameters (override with `--set attack.<param>=<value>`):

| Param | Description |
|-------|-------------|
| `epsilon` | Perturbation budget for L∞ attacks |
| `steps` | Iteration count for PGD, DeepFool, EOT-PGD, DR |
| `attack_roi` | Normalized ROI mask `x,y,w,h` for ROI-aware objectives |
| `target_class` | Required for target/hide-class objective modes |

---

## 5. Defenses

Defenses are registered as plugins via `@register_defense_plugin()` in `src/lab/defenses/`.
Pass `--set defense.name=<alias>` to any runner.

| Alias | Description |
|-------|-------------|
| `none` | No defense — measures raw attack effect |
| `c_dog` | DPC-UNet diffusion denoiser; requires `DPC_UNET_CHECKPOINT_PATH` |
| `c_dog_ensemble` | Multi-pass DPC-UNet ensemble defense; registered but not in current auto-cycle catalog |
| `jpeg_preprocess` | JPEG compress + decompress before inference |
| `median_preprocess` | Median filter preprocessing |
| `bit_depth` | Bit-depth reduction preprocessing |
| `confidence_filter` | Post-prediction confidence-based filtering |
| `random_resize` | Random resize preprocessing; registered but not in current auto-cycle catalog |

**`c_dog` provenance note:** the defense model identity lives in
`run_summary.json` under `provenance.defense_checkpoints`, not in the primary
checkpoint fingerprint fields. Always check there when auditing `c_dog` runs.

---

## 6. Running Experiments

### Single run (custom or debug)

```bash
python scripts/run_unified.py \
  --config configs/default.yaml \
  --set attack.name=square \
  --set defense.name=c_dog \
  --set runner.run_name=dpc_unet__square__c_dog
```

### Sweep (full attack × defense matrix)

```bash
# Quick smoke sweep (8 images per run)
python scripts/sweep_and_report.py --preset smoke

# Full sweep (all images)
python scripts/sweep_and_report.py --preset full

# Full sweep + update GitHub Pages dashboard
python scripts/sweep_and_report.py --preset full --update-pages
```

Without `--update-pages`, the sweep writes reports but does **not** overwrite
`docs/index.html`. Only pass `--update-pages` on intentional release sweeps.

### Autonomous cycle (NUC / long-running)

```bash
python scripts/auto_cycle.py          # single cycle
python scripts/auto_cycle.py --loop   # repeat indefinitely
```

### Monitor a running cycle

```bash
python scripts/watch_cycle.py         # live TUI dashboard (run in separate pane)
```

---

## 7. Scripts CLI Reference

### `scripts/auto_cycle.py`

Orchestrates the full 4-phase experiment cycle.

```
--loop               Repeat after each cycle completes
--dry-run            Plan without executing any runs
--max-cycles N       Stop after N cycles
--skip-phase N       Skip phase N (useful for resuming)
```

State files:
- `outputs/cycle_state.json` — current cycle (may be stale; prefer cycle_history)
- `outputs/cycle_history/<cycle_id>.json` — complete per-cycle record (authoritative)

---

### `scripts/run_unified.py`

Single-run entrypoint. Use for custom, one-off, or debugging runs.

```bash
python scripts/run_unified.py \
  --config configs/default.yaml \
  --set attack.name=pgd \
  --set defense.name=none \
  --set runner.run_name=dpc_unet__pgd__none
```

---

### `scripts/sweep_and_report.py`

Runs a matrix sweep across all attacks × defenses and generates CSV + HTML reports.

```
--preset smoke|full   Image count (smoke=8, full=all)
--update-pages        Allow writing docs/index.html (GitHub Pages)
--dry-run             Print plan without executing
--report-only         Regenerate report from existing runs (no new runs)
--attacks a1,a2       Filter to specific attacks
--defenses d1,d2      Filter to specific defenses
```

---

### `scripts/generate_dashboard.py`

Renders the HTML dashboard from framework report outputs.

```
--reports-root PATH   Directory containing sweep reports
--output PATH         HTML output file path
--no-pages            Skip writing docs/index.html (default in sweeps)
```

---

### `scripts/cleanup_stale_runs.py`

Removes `outputs/framework_runs/` directories that predate the latest checkpoint
promotion. Safe to run after any checkpoint promotion.

```bash
python scripts/cleanup_stale_runs.py --dry-run              # preview what would be removed
python scripts/cleanup_stale_runs.py --max-delete 10        # cap at 10 deletions
python scripts/cleanup_stale_runs.py --before-mtime <ISO>   # manual cutoff timestamp
```

**Safety guarantees:**
- Skips incomplete run directories (missing any of the 3 required artifacts)
- Skips runs whose checkpoint fingerprint matches the current promoted checkpoint
- Aborts (exit 2) if stale count exceeds `--max-delete` limit (default: 20)

---

### `scripts/watch_cycle.py`

Live TUI dashboard (powered by `rich`) showing cycle progress, current run ETA,
and machine thermals.

```bash
python scripts/watch_cycle.py
# Run in a separate terminal or tmux pane while auto_cycle.py --loop is active
```

---

### `scripts/run_training_ritual.py`

Human-triggered wrapper that sequences the full adversarial fine-tuning pipeline.

```bash
python scripts/run_training_ritual.py --dry-run             # preview steps only
python scripts/run_training_ritual.py                       # execute
python scripts/run_training_ritual.py --max-age-hours 48    # allow older signal
```

---

## 8. The Training Pipeline

After sufficient cycles accumulate, run adversarial fine-tuning to improve the model.
This is always **human-triggered** — never automatic.

```
auto_cycle.py --loop
  └── writes: outputs/cycle_training_signal.json
              (when enough_data=true and dominant attack is clear)

run_training_ritual.py
  ├── validates signal is fresh (default < 24 hours old)
  ├── runs export_training_data.py  →  outputs/training_exports/<id>/
  ├── runs train_from_signal.py     →  trains model, runs gate, writes manifest
  └── prints: final_verdict + gate_delta

Gate rule: new_mAP50 - baseline_mAP50 >= -0.005
  PASS  →  promote checkpoint (update DPC_UNET_CHECKPOINT_PATH in .env)
  FAIL  →  keep current checkpoint; investigate training pairs or params
```

**Check training verdict:**
```bash
python -m json.tool \
  outputs/training_runs/<cycle_id>/training_manifest.json \
  | grep -E "final_verdict|gate_delta"
```

**After promoting a checkpoint:**
1. Update `DPC_UNET_CHECKPOINT_PATH` in `.env` on every machine (local + NUC)
2. Run `python scripts/cleanup_stale_runs.py --dry-run` to preview stale dirs
3. Run cleanup without `--dry-run` to remove them

---

## 9. Skills (Slash Commands in Claude Code)

Skills are invoked in the Claude Code CLI as `/skill-name`.

| Skill | What it returns |
|-------|----------------|
| `/cycle-status` | Current cycle phase, active run, last completed run |
| `/cycle-report` | Full report: top attacks, defenses, recovery per cycle |
| `/eval-ab` | Head-to-head comparison of two checkpoints |
| `/training-status` | Signal readiness, last training verdict, gate delta |
| `/plan-next-cycle` | Parameter recommendations for next cycle |
| `/sweep-report` | Summary of latest sweep report |
| `/explain-run` | Plain-English explanation of a single run's metrics |
| `/full-repo-audit` | Comprehensive codebase audit (big-brother-auditor) |
| `/big-brother-auditor` | Targeted PR or file change review |
| `/check-comparability` | Verify two runs are like-for-like before comparing |

---

## 10. Reading Results

### Dashboard (`docs/index.html` or `outputs/framework_reports/`)

| Table | What it shows |
|-------|-------------|
| Attack Effectiveness | mAP50 drop per attack — negative means attack worked |
| Defense Recovery | % of mAP50 loss recovered by each defense |
| Per-Class Vulnerability | Which YOLO object classes are most affected per attack |

### Cycle History (`outputs/cycle_history/<cycle_id>.json`)

Key fields to check:

| Field | Meaning |
|-------|---------|
| `phase4_results` | Authoritative mAP50 rows (use these for analysis) |
| `top_attacks` | Attacks that qualified for Phase 4 |
| `top_defenses` | Defenses that qualified for Phase 4 |
| `training_signal_written` | Whether the training signal was emitted this cycle |

### Warning Codes

Warnings appear in sweep reports and `warnings.json` files. Common ones:

| Code | Meaning | Action |
|------|---------|--------|
| `NO_BASELINE` | No `none__none` baseline run found | Run baseline first |
| `MULTIPLE_BASELINES` | Multiple baseline candidates; first alphabetically chosen | Deduplicate if needed |
| `NO_VALIDATION` | No Phase 4 mAP50 run exists | Run or await Phase 4 |
| `LOW_ATTACK_COUNT` | Fewer than 2 attack runs | Add more attacks to matrix |
| `LOW_CONFIDENCE_FLOOR` | Baseline avg_confidence < 0.5 | Check model or dataset |
| `ATTACK_BELOW_NOISE` | Attack shows < 5% mAP50 drop | Attack may be misconfigured |
| `DEFENSE_RECOVERY_UNDEFINED` | Recovery undefined — attack had no effect | Expected if attack is below noise |
| `DEFENSE_DEGRADES_PERFORMANCE` | Defense makes detection worse than attack alone | Defense likely misconfigured |
| `MISSING_PER_CLASS` | No per-class data in metrics.json | Check predictions.per_class in run |

**`NO_VALIDATION` false positives:** if this warning fires but Phase 4 runs exist,
check that those rows have `authority=authoritative`. Phase 1 smoke rows cannot
incorrectly produce this warning.

**`stale_cycle_state`:** if `outputs/cycle_state.json` shows a different `cycle_id`
than the latest `cycle_history/` entry, it is stale. Use the cycle_history file
directly — ignore cycle_state for any analysis.

---

## 11. NUC Operations

The NUC is the dedicated compute node running `auto_cycle.py --loop` continuously.

### Connect and check status

```bash
ssh lurch@nuc.local
cd ~/ml-labs/YOLO-Bad-Triangle

tmux attach -t cycle                   # attach to running session
# or open a new pane:
python scripts/watch_cycle.py
```

### After a `main` branch merge on NUC

```bash
git pull origin main
pytest -q --tb=short                   # verify green before resuming cycle
```

### Restart a stuck or crashed cycle

```bash
tmux kill-session -t cycle             # kill hung session
tmux new-session -d -s cycle \
  'python scripts/auto_cycle.py --loop 2>&1 | tee outputs/auto_cycle.log'
```

### Cycle snapshots (read-only git branch)

The cycle loop automatically commits state snapshots to the `nuc/cycle-snapshots`
branch on origin using git plumbing (`write-tree` / `commit-tree` / `push`).
This does **not** touch your local HEAD or working tree.

```bash
git log origin/nuc/cycle-snapshots --oneline -10   # view recent snapshots
```

---

## 12. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `c_dog` crashes on startup | `DPC_UNET_CHECKPOINT_PATH` missing or wrong | Set correct path in `.env` |
| `NO_VALIDATION` on fresh sweep | No Phase 4 runs yet | Let auto_cycle complete Phase 4, or check `--skip-phase` |
| Run resuming with wrong checkpoint | Fingerprint mismatch in `run_summary.json` | Delete stale dir or run `cleanup_stale_runs.py` |
| Dashboard empty / no rows | Wrong `--reports-root` or missing framework_reports | Verify path; run `--report-only` to regenerate |
| `stale_cycle_state` warning | `cycle_state.json` cycle_id ≠ latest history entry | Use `cycle_history/<id>.json` directly |
| Tests fail after `git pull` | Dependency or schema change | `pip install -r requirements.txt && pytest -q` |
| `MULTIPLE_BASELINES` warning | Multiple `none__none` runs present | Alphabetical selection is deterministic; investigate if counts differ |
| Training gate fails repeatedly | Poor signal quality or insufficient attack diversity | Check `cycle_training_signal.json`: `enough_data`, `dominant_attack` |
| Watch cycle shows no progress | `auto_cycle.py` not running or tmux session detached | Check `tmux ls`; re-attach or restart |

---

## 13. Key File Map

```
YOLO-Bad-Triangle/
├── configs/
│   └── default.yaml              # base experiment config (override with --set)
├── docs/
│   ├── TEAM_MANUAL.md            # this file — start here
│   ├── PIPELINE_IN_PLAIN_ENGLISH.md  # narrative 4-phase loop walkthrough
│   ├── LOOP_DESIGN.md            # technical auto_cycle state machine design
│   ├── TEAM_GUIDE.md             # quick onboarding commands
│   └── LOCAL_CONFIG_POLICY.md    # .env and local config governance
├── outputs/                      # all runtime artifacts (gitignored)
│   ├── framework_runs/           # per-run directories (3-file contract)
│   ├── framework_reports/        # sweep HTML + CSV reports
│   ├── cycle_state.json          # current cycle state (may be stale)
│   ├── cycle_history/            # per-cycle full records (authoritative)
│   ├── cycle_training_signal.json
│   └── training_runs/            # training manifests + gate results
├── schemas/v1/                   # JSON schemas for all artifact types
├── scripts/
│   ├── auto_cycle.py             # 4-phase orchestrator
│   ├── run_unified.py            # single-run entrypoint
│   ├── sweep_and_report.py       # matrix sweep + CSV/HTML report
│   ├── generate_dashboard.py     # HTML dashboard renderer
│   ├── cleanup_stale_runs.py     # post-promotion stale dir cleanup
│   ├── watch_cycle.py            # live TUI monitor
│   ├── run_training_ritual.py    # training pipeline wrapper
│   ├── export_training_data.py   # exports adversarial training pairs
│   └── train_from_signal.py      # trains + gates new checkpoint
├── src/lab/
│   ├── attacks/                  # attack plugins (@register_attack_plugin)
│   ├── defenses/                 # defense plugins (@register_defense_plugin)
│   ├── config/contracts.py       # all canonical constants
│   ├── eval/                     # metrics computation + framework_metrics
│   ├── reporting/                # warnings, auto-summary generation
│   └── runners/
│       ├── run_experiment.py     # core runner (do not invoke directly)
│       └── run_intent.py         # fingerprinting + run-skip logic
└── .claude/skills/               # slash command skill definitions
```

---

## 14. Further Reading

| Document | When to read it |
|----------|----------------|
| [PIPELINE_IN_PLAIN_ENGLISH.md](PIPELINE_IN_PLAIN_ENGLISH.md) | You want a narrative walkthrough of the 4-phase loop |
| [LOOP_DESIGN.md](LOOP_DESIGN.md) | You're modifying auto_cycle.py or the state machine |
| [TEAM_GUIDE.md](TEAM_GUIDE.md) | You need the fastest-possible onboarding commands |
| [ATTACK_TEMPLATE.md](ATTACK_TEMPLATE.md) | You're writing a new attack plugin |
| [DEFENSE_TEMPLATE.md](DEFENSE_TEMPLATE.md) | You're writing a new defense plugin |
| [LOCAL_CONFIG_POLICY.md](LOCAL_CONFIG_POLICY.md) | You're adding a new config key or `.env` variable |
| [CLAUDE.md](../CLAUDE.md) | You're opening a PR or doing a code review |
