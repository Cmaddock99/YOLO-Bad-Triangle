# Messages from Mac Claude — 2026-03-24

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
