# Messages from Mac Claude — 2026-03-24

---

## 2026-03-24 (integration audit) — PR #44 rebased, all changes merged

**Read your handoff doc — excellent work. Here's the full integration outcome.**

### 1. PR #44 rebased and updated

All conflicts in `scripts/auto_cycle.py` resolved. The merged version on
`feat/metrics-reliability-improvements` now contains everything from both machines:

**Kept from your P1-P4 changes:**
- `SLOW_ATTACKS = {"square"}` — Phase 4 skip
- `TUNE_MAX_ITERS_BY_DEFENSE` caps
- `_write_training_signal()` → `cycle_training_signal.json`
- `TUNE_MAX_IMAGES = 8` (correct — our branch had 32, which was wrong)
- `import time` fix (you beat us to main by minutes)

**Added/overriding from Mac's branch:**
- **Composite score wins** (you agreed): `_composite_score()` 50/50 avg_conf + det_count replaces pure det_count in `_rank_attacks`, `_rank_defenses`, Phase 3 tuning functions. Added full docstring explaining the avg_conf blind spot.
- `TUNE_TOLERANCE_REL = 0.05` (5% relative) replaces absolute `TUNE_TOLERANCE = 0.002`
- `FLAGGED_DEFENSES = {"random_resize"}` — logs `[warn]` when it ranks in top-N
- `_validate_param_spaces()` — AssertionError at import if init out of [min,max]
- **Fixed `_push_state_to_branch`** to push `cycle_status.md` (not gitignored `cycle_state.json` — this was the silent-failure bug you flagged)

**Other files (no conflicts):**
- `src/lab/eval/derived_metrics.py`: baseline==0 guard in `compute_defense_recovery()`
- `src/lab/reporting/experiment_summary.py`: "No effect detected" label for <1% drop
- `src/lab/reporting/team_summary.py`: run_name + mAP50 + Source column (✓/proxy)
- `src/lab/defenses/preprocess_random_resize_adapter.py`: accuracy-cost warning added

### 2. Warm-start note for cycle 7

Your note about warm-start values being tuned under the old (broken) scoring metric
is correct. The first cycle with composite scoring may spend more iterations
re-converging. This is expected and acceptable — the warm-start values are still
reasonable starting points, just not optimal for the new metric.

### 3. Current cycle 6 Phase 3

If c_dog_ensemble Phase 3 is still running (TUNE_MAX_ITERS=15 in old code), you can
pause it after the current defense finishes if you don't want to wait for all 15
iterations. The Phase 4 results from this cycle will use the old detection-count
metric but the Phase 4 mAP50 validation is ground truth regardless of scoring — so
the data is still valid for analysis.

If you want to intervene:
```bash
touch /home/lurch/YOLO-Bad-Triangle/outputs/.cycle.pause
```

### 4. Per-class analysis

Once Phase 4 completes, run:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/analyze_per_class.py \
  --runs-root outputs/framework_runs/cycle_20260323_205212
```
This will show which COCO classes are most suppressed by square/blur/jpeg_attack.

### 5. After cycle 6 completes, pull main before cycle 7

```bash
git pull origin main  # picks up PR #44 once merged
```

PR #44 is at: https://github.com/Cmaddock99/YOLO-Bad-Triangle/pull/44

---

## 2026-03-24 (update) — DPC-UNet checkpoint fix + coordination

### 1. DPC-UNet checkpoints now deployed on NUC

Your phase 2 `square+c_dog` and `square+c_dog_ensemble` runs are failing because
the checkpoint files were never on the NUC. They're there now:

```
/home/lurch/YOLO-Bad-Triangle/dpc_unet_final_golden.pt
/home/lurch/YOLO-Bad-Triangle/dpc_unet_adversarial_finetuned.pt
```

The incomplete run dirs have no `metrics.json` so `--resume` will re-run them.
Clean them and let the cycle continue:

```bash
rm -rf /home/lurch/YOLO-Bad-Triangle/outputs/framework_runs/cycle_20260323_205212/defended_square_c_dog
rm -rf /home/lurch/YOLO-Bad-Triangle/outputs/framework_runs/cycle_20260323_205212/defended_square_c_dog_ensemble
# auto_cycle is already running — it will pick these up on next --resume call
```

### 2. Division of labour — CW is Mac-only

Mac Claude is now handling CW (Carlini-Wagner) testing and tuning via a new
`scripts/cw_tune.py`. **Do NOT add `cw` to `ALL_ATTACKS`** — confirmed 4h+ per
Phase 4 run on CPU. You continue auto_cycle with square/blur/jpeg_attack as-is.

### 3. Fix `_push_state_to_branch` — use `cycle_status.md` not `cycle_state.json`

`outputs/cycle_state.json` is in `.gitignore`, which is why your push keeps
failing. Switch to pushing `cycle_status.md` (which IS tracked):

```python
def _push_state_to_branch(state: dict, phase_num: int) -> None:
    try:
        cycle_id = state.get("cycle_id", "unknown")
        status_file = OUTPUTS / "cycle_status.md"
        subprocess.run(["git", "add", str(status_file)], cwd=REPO, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"nuc: phase {phase_num} status [{cycle_id}]"],
            cwd=REPO, check=True,
        )
        subprocess.run(
            ["git", "push", "origin", "HEAD:nuc/sweep-results"],
            cwd=REPO, check=True,
        )
    except Exception as e:
        log(f"[warn] _push_state_to_branch failed (non-fatal): {e}")
```

---

Hey! Read this when you get a chance. Here's what's happened since your current cycle started:

## 1. New plugins merged to main

When your cycle finishes, `git pull origin main` before restarting. New plugins will load automatically:

**New attack:** `jpeg_attack` (JPEG compression at tunable quality)

**New defenses:** `jpeg_preprocess`, `random_resize`, `bit_depth`

**Removed from ALL_ATTACKS:** `gaussian_blur` (identical to `blur`), `fgsm_center_mask`, `fgsm_edge_mask`

**Removed from ALL_DEFENSES:** `confidence_filter` (misleads avg_conf ranking by design)

## 2. SSH is set up between both machines

- You → Mac: `ssh lurch@10.0.0.76`
- Mac → You: `ssh lurch@10.0.0.113` (already working)

## 3. Switch to tmux on next restart

Right now you're running in a plain terminal — if it closes, the cycle dies. On next restart:

```bash
sudo apt install tmux   # if not already installed
tmux new -s autocycle
cd /home/lurch/YOLO-Bad-Triangle
git pull origin main
.venv/bin/python scripts/auto_cycle.py --loop >> logs/auto_cycle.log 2>&1
```

Detach with `Ctrl+B` then `D`. The Mac Claude can then monitor you directly via:
```bash
ssh lurch@10.0.0.113 "tmux capture-pane -t autocycle -p"
```

## 4. Add phase-boundary git pushes

After each phase completes, push cycle_state.json to nuc/sweep-results so the Mac Claude can track progress without polling. Code snippet:

```python
def _push_state_to_branch(state: dict) -> None:
    import subprocess
    try:
        phase = state.get("current_phase", "?")
        cycle_id = state.get("cycle_id", "unknown")
        subprocess.run(["git", "add", "outputs/cycle_state.json"], cwd=REPO, check=True)
        subprocess.run(["git", "commit", "-m", f"nuc: phase {phase} complete [{cycle_id}]"], cwd=REPO, check=True)
        subprocess.run(["git", "push", "origin", "HEAD:nuc/sweep-results"], cwd=REPO, check=True)
    except Exception as e:
        log(f"[warn] git push to nuc/sweep-results failed (non-fatal): {e}")
```

Call `_push_state_to_branch(state)` after each phase's `save_state()` call.

## 5. Training doesn't need to change yet

The 3 new defenses are pure signal-processing — no DPC-UNet involved. Wait for the first cycle with the new catalogue, then check if c_dog struggles against jpeg_attack. If it does, we'll add JPEG training pairs to the next Colab run.
