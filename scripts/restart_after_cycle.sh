#!/usr/bin/env bash
# restart_after_cycle.sh
#
# Safely restarts auto_cycle.py --loop between cycles so the process picks up
# any code changes that landed on disk (e.g. from a git pull/rebase).
#
# Strategy:
#   1. Wait for the current Phase 4 to complete.
#   2. Touch .cycle.pause so the next cycle pauses after Phase 1 (no subprocess running).
#   3. Wait for the pause to activate.
#   4. Kill the old process (finally-block releases lock cleanly).
#   5. Stash outputs, pull latest, pop stash (belt-and-suspenders).
#   6. Start a fresh auto_cycle.py --loop process.
#   7. Remove .cycle.pause so it continues.
#
# Usage:  bash scripts/restart_after_cycle.sh &
#         (runs in the background; logs to logs/restart_watcher.log)

set -euo pipefail

REPO=/home/lurch/YOLO-Bad-Triangle
LOG=$REPO/logs/auto_cycle.log
WATCHER_LOG=$REPO/logs/restart_watcher.log
STATE=$REPO/outputs/cycle_state.json
PAUSE=$REPO/outputs/.cycle.pause
PYTHON=$REPO/.venv/bin/python
SCRIPT=$REPO/scripts/auto_cycle.py

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [restart_watcher] $*" | tee -a "$WATCHER_LOG"; }

log "Started. Waiting for Phase 4 to complete..."

# Step 1: wait for cycle_state.json to show complete=true
while true; do
    if python3 -c "import json,sys; d=json.load(open('$STATE')); sys.exit(0 if d.get('complete') else 1)" 2>/dev/null; then
        log "Phase 4 complete detected."
        break
    fi
    sleep 30
done

# Step 2: set pause so next cycle stops after Phase 1
log "Touching .cycle.pause..."
touch "$PAUSE"

# Step 3: wait for the pause to activate in the log
log "Waiting for 'PAUSED after phase 1' in log..."
while true; do
    if tail -n 30 "$LOG" 2>/dev/null | grep -q "PAUSED after phase 1"; then
        log "Pause confirmed active."
        break
    fi
    sleep 15
done

# Step 4: kill the paused process
CYCLE_PID=$(pgrep -f "auto_cycle.py --loop" | head -1 || true)
if [ -n "$CYCLE_PID" ]; then
    log "Killing auto_cycle PID $CYCLE_PID..."
    kill "$CYCLE_PID"
    sleep 4
else
    log "No auto_cycle process found — may have already exited."
fi

# Step 5: stash + pull + pop (belt-and-suspenders; execv in git_pull will handle future pulls)
cd "$REPO"
log "Stashing local outputs..."
git stash push -u -m "restart-watcher-$(date +%Y%m%d%H%M%S)" >> "$WATCHER_LOG" 2>&1 || true
log "Pulling latest code..."
git pull --no-rebase -X ours origin main >> "$WATCHER_LOG" 2>&1 || true
log "Restoring stash..."
git stash pop >> "$WATCHER_LOG" 2>&1 || true

# Step 6: start fresh process (appends to existing log)
log "Starting fresh auto_cycle.py --loop..."
nohup "$PYTHON" "$SCRIPT" --loop >> "$LOG" 2>&1 &
NEW_PID=$!
log "New auto_cycle PID: $NEW_PID"

# Step 7: remove pause so the fresh process runs freely
sleep 3
log "Removing .cycle.pause..."
rm -f "$PAUSE"

log "Done. auto_cycle is running fresh with updated code."
