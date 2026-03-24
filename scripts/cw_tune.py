#!/usr/bin/env python3
"""scripts/cw_tune.py

Carlini-Wagner L2 test-and-tune cycle for YOLO-Bad-Triangle.

CW is too slow for the NUC's CPU-only auto_cycle (Phase 4 would take 4 h+).
This script runs on the Mac (Apple Silicon MPS) and mirrors the auto_cycle
phase structure — but focused entirely on CW.

  Phase 1  Smoke        Baseline + CW with defaults (8 images, MPS).
                         Confirms attack is working; records initial drop.

  Phase 2  Tune         Coordinate descent over c, max_iter, lr (8 images).
                         Same algorithm as auto_cycle phase 3.

  Phase 3  Validate     Best CW params × all defenses (50 images, MPS).
                         Produces per-defense recovery table.

State:   outputs/cw_tune_state.json
Lock:    outputs/.cw_tune.lock
Log:     logs/cw_tune.log

Usage:
  PYTHONPATH=src ./.venv/bin/python scripts/cw_tune.py           # run / resume
  PYTHONPATH=src ./.venv/bin/python scripts/cw_tune.py --status  # show state
  PYTHONPATH=src ./.venv/bin/python scripts/cw_tune.py --reset   # start fresh
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO = Path(__file__).parent.parent
OUTPUTS = REPO / "outputs"
STATE_FILE = OUTPUTS / "cw_tune_state.json"
LOCK_FILE = OUTPUTS / ".cw_tune.lock"
LOG_DIR = REPO / "logs"
PYTHON = REPO / ".venv" / "bin" / "python"

RUNS_ROOT = str(OUTPUTS / "framework_runs" / "cw_tune")
REPORT_ROOT = str(OUTPUTS / "framework_reports" / "cw_tune")

# ── CW-specific settings ───────────────────────────────────────────────────────

# Apple Silicon MPS gives ~3-5× speedup vs CPU for CW.
# Falls back to CPU gracefully if MPS is unavailable.
CW_DEVICE = "mps"

ALL_DEFENSES: list[str] = [
    "bit_depth", "c_dog", "c_dog_ensemble", "jpeg_preprocess",
    "median_preprocess", "random_resize",
]

# Smoke: 8 images (same as auto_cycle phase 1/2)
# Tune:  8 images — fast enough for coordinate descent probing
# Validate: 50 images — more reliable signal than smoke, practical with MPS
SMOKE_IMAGES = "8"
VALIDATE_IMAGES = "50"

# Coordinate descent settings (same as auto_cycle)
TUNE_MAX_ITERS = 15
TUNE_TOLERANCE = 0.002

# CW tunable parameter space
CW_PARAM_SPACE: dict[str, dict] = {
    "attack.params.c": {
        "init": 1.0, "min": 0.1, "max": 10.0, "scale": "log", "factor": 3.0,
    },
    "attack.params.max_iter": {
        "init": 200, "min": 50, "max": 500, "scale": "int", "step": 50,
    },
    "attack.params.lr": {
        "init": 0.01, "min": 0.001, "max": 0.1, "scale": "log", "factor": 3.0,
    },
}

# Fixed overrides applied to every CW run
CW_FIXED_OVERRIDES: dict[str, str] = {
    "attack.params.device": CW_DEVICE,
    "attack.params.early_stop": "true",
}

# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "cw_tune.log", "a") as fh:
        fh.write(line + "\n")


# ── State ─────────────────────────────────────────────────────────────────────

def init_state() -> dict:
    return {
        "started_at": datetime.now().isoformat(),
        "phase1_complete": False,
        "phase2_complete": False,
        "phase3_complete": False,
        "initial_drop": None,         # detection drop with default CW params
        "best_params": {},            # best params found by coordinate descent
        "best_tune_score": None,      # best confidence drop achieved in phase 2
        "tune_history": [],           # coordinate descent trace
        "validation_results": {},     # phase 3: per-defense recovery table
    }


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return init_state()


def save_state(state: dict) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Metrics helpers ───────────────────────────────────────────────────────────

def read_metrics(run_dir: Path) -> dict | None:
    f = run_dir / "metrics.json"
    return json.loads(f.read_text()) if f.exists() else None


def get_avg_conf(m: dict) -> float | None:
    return m.get("predictions", {}).get("confidence", {}).get("mean")


def get_detection_drop(m_baseline: dict, m_attack: dict) -> float:
    b = get_avg_conf(m_baseline) or 0.0
    a = get_avg_conf(m_attack) or b
    return b - a


# ── Subprocess helpers ────────────────────────────────────────────────────────

def _env() -> dict:
    cpu_count = str(os.cpu_count() or 4)
    env = {
        **os.environ,
        "PYTHONPATH": str(REPO / "src"),
        "OMP_NUM_THREADS": cpu_count,
        "MKL_NUM_THREADS": cpu_count,
        "OPENBLAS_NUM_THREADS": cpu_count,
        "NUMEXPR_NUM_THREADS": cpu_count,
    }
    if not env.get("DPC_UNET_CHECKPOINT_PATH"):
        for candidate in ("dpc_unet_adversarial_finetuned.pt", "dpc_unet_final_golden.pt"):
            path = REPO / candidate
            if path.exists():
                env["DPC_UNET_CHECKPOINT_PATH"] = str(path)
                break
    return env


def run_single(
    *,
    attack: str,
    defense: str,
    run_name: str,
    max_images: str = SMOKE_IMAGES,
    overrides: dict | None = None,
    validation: bool = False,
) -> bool:
    """Run one experiment via run_unified.py. Skips if metrics.json exists."""
    run_dir = Path(RUNS_ROOT) / run_name
    if (run_dir / "metrics.json").exists():
        log(f"  skip (exists): {run_name}")
        return True

    cmd = [
        str(PYTHON), "scripts/run_unified.py", "run-one",
        "--config", "configs/default.yaml",
        "--set", f"attack.name={attack}",
        "--set", f"defense.name={defense}",
        "--set", f"runner.run_name={run_name}",
        "--set", f"runner.output_root={RUNS_ROOT}",
        "--set", f"runner.max_images={max_images}",
    ]
    if validation:
        cmd += ["--set", "validation.enabled=true"]
    # Apply fixed CW overrides first, then caller overrides (caller can override CW_FIXED_OVERRIDES)
    for key, val in {**CW_FIXED_OVERRIDES, **(overrides or {})}.items():
        cmd += ["--set", f"{key}={val}"]

    log(f"  run: {run_name}  (attack={attack}, defense={defense})")
    result = subprocess.run(cmd, cwd=str(REPO), env=_env())
    return result.returncode == 0


# ── Coordinate descent (mirrored from auto_cycle.py) ─────────────────────────

def _clamp(value, spec: dict):
    lo, hi = spec["min"], spec["max"]
    if spec["scale"] in ("int", "odd_int"):
        return int(max(lo, min(hi, int(value))))
    return float(max(lo, min(hi, float(value))))


def _candidates(spec: dict, current) -> list:
    scale = spec["scale"]
    lo, hi = spec["min"], spec["max"]

    if scale == "log":
        f = spec["factor"]
        cands = [float(current) * f, float(current) / f]
        cands = [float(max(lo, min(hi, c))) for c in cands]
        cands = [c for c in cands if abs(c - current) / (abs(current) + 1e-12) > 0.05]
    elif scale == "linear_float":
        step = spec["step"]
        cands = [float(current) + step, float(current) - step]
        cands = [float(max(lo, min(hi, c))) for c in cands]
        cands = [c for c in cands if abs(c - current) > 1e-9]
    elif scale == "odd_int":
        step = spec["step"]
        up, down = int(current) + step, int(current) - step
        if up % 2 == 0: up += 1
        if down % 2 == 0: down -= 1
        cands = [c for c in [up, down] if lo <= c <= hi and c != int(current)]
    elif scale == "int":
        step = spec["step"]
        cands = [int(current) + step, int(current) - step]
        cands = [c for c in cands if lo <= c <= hi and c != int(current)]
    else:
        return []

    seen, out = set(), []
    for c in cands:
        key = round(float(c), 8)
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def _fmt(params: dict) -> str:
    return "  ".join(f"{k.split('.')[-1]}={v}" for k, v in params.items())


def _coordinate_descent(
    label: str,
    param_space: dict,
    score_fn,
    run_prefix: str,
    existing_history: list | None = None,
) -> tuple[dict, float, list]:
    history = list(existing_history or [])
    counter = [len(history)]

    def next_name() -> str:
        counter[0] += 1
        return f"{run_prefix}_{counter[0]:03d}"[:80]

    current = {k: spec["init"] for k, spec in param_space.items()}
    current_score = score_fn(current, next_name())
    log(f"  [{label}] init  score={current_score:.4f}  params={_fmt(current)}")
    history.append({
        "iter": 0, "param": "init", "value": None,
        "score": current_score, "delta": 0.0, "improved": True,
    })

    for iteration in range(1, TUNE_MAX_ITERS + 1):
        pass_improved = False

        for param_key, spec in param_space.items():
            best_candidate = None
            best_candidate_score = current_score

            for candidate in _candidates(spec, current[param_key]):
                test_params = {**current, param_key: candidate}
                s = score_fn(test_params, next_name())
                short = param_key.split(".")[-1]
                log(f"  [{label}] iter={iteration}  {short}={candidate}  "
                    f"score={s:.4f}  delta={s - current_score:+.4f}")
                history.append({
                    "iter": iteration, "param": param_key,
                    "value": candidate, "score": round(s, 6),
                    "delta": round(s - current_score, 6),
                    "improved": False,
                })
                if s > best_candidate_score:
                    best_candidate_score = s
                    best_candidate = candidate

            if (best_candidate is not None and
                    best_candidate_score - current_score > TUNE_TOLERANCE):
                log(f"  [{label}] ✓ commit  {param_key.split('.')[-1]}  "
                    f"{current[param_key]} → {best_candidate}  "
                    f"({current_score:.4f} → {best_candidate_score:.4f})")
                current = {**current, param_key: best_candidate}
                current_score = best_candidate_score
                history[-1]["improved"] = True
                pass_improved = True

        if not pass_improved:
            log(f"  [{label}] converged after {iteration} pass(es)  "
                f"best={current_score:.4f}  {_fmt(current)}")
            break

    return dict(current), current_score, history


# ── Git helpers ───────────────────────────────────────────────────────────────

def git_commit_phase(phase_num: int, state: dict) -> None:
    """Commit a phase-complete snapshot so the cycle is visible in git history."""
    status_file = _write_status(state)
    try:
        subprocess.run(["git", "add", str(status_file)], cwd=str(REPO), check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(REPO))
        if diff.returncode == 0:
            log(f"git_commit_phase {phase_num}: nothing new to commit")
            return
        phase_labels = {1: "smoke", 2: "tune", 3: "validate"}
        label = phase_labels.get(phase_num, str(phase_num))
        msg_lines = [f"cw_tune: phase {phase_num}/{label} complete"]
        if phase_num >= 2 and state.get("best_params"):
            for k, v in state["best_params"].items():
                msg_lines.append(f"  cw {k.split('.')[-1]}={v}")
        if phase_num < 3:
            msg_lines += ["", f"*** PARTIAL — phase(s) {phase_num+1}–3 still pending ***"]
        subprocess.run(
            ["git", "commit", "-m", "\n".join(msg_lines)],
            cwd=str(REPO), check=True,
        )
        subprocess.run(["git", "push"], cwd=str(REPO), check=True)
        log(f"git_commit_phase: pushed phase {phase_num} snapshot")
    except subprocess.CalledProcessError as exc:
        log(f"git_commit_phase: failed (non-fatal) — {exc}")


def _write_status(state: dict) -> Path:
    lines = [
        "# CW tune status",
        "",
        f"started_at : {state.get('started_at', 'unknown')}",
        f"updated_at : {datetime.now().isoformat()}",
        "",
        f"P1={state['phase1_complete']}  "
        f"P2={state['phase2_complete']}  "
        f"P3={state['phase3_complete']}",
        "",
    ]
    if state.get("initial_drop") is not None:
        lines.append(f"initial_drop : {state['initial_drop']:.4f}")
    if state.get("best_params"):
        lines.append(f"best_params  : {_fmt(state['best_params'])}")
    if state.get("best_tune_score") is not None:
        lines.append(f"best_score   : {state['best_tune_score']:.4f}")
    if state.get("validation_results"):
        lines += ["", "## Defense recovery (phase 3)"]
        for defense, result in sorted(state["validation_results"].items()):
            lines.append(f"  {defense:25s}  recovery={result.get('recovery', 'n/a')}")
    status_file = OUTPUTS / "cw_tune_status.md"
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    status_file.write_text("\n".join(lines) + "\n")
    return status_file


# ── Phase 1 — Smoke ───────────────────────────────────────────────────────────

def phase1(state: dict) -> bool:
    log("=== Phase 1: Smoke (baseline + CW defaults, 8 images, MPS) ===")

    run_single(attack="none", defense="none", run_name="baseline_none")
    run_single(attack="cw",   defense="none", run_name="cw_default_smoke")

    baseline_m = read_metrics(Path(RUNS_ROOT) / "baseline_none")
    attack_m   = read_metrics(Path(RUNS_ROOT) / "cw_default_smoke")

    if not baseline_m or not attack_m:
        log("Phase 1: missing metrics — aborting")
        return False

    drop = get_detection_drop(baseline_m, attack_m)
    baseline_conf = get_avg_conf(baseline_m) or 0.0
    attack_conf   = get_avg_conf(attack_m)   or baseline_conf

    log(f"Phase 1 result: baseline_conf={baseline_conf:.4f}  "
        f"attack_conf={attack_conf:.4f}  drop={drop:.4f}")

    state["initial_drop"] = round(drop, 6)
    state["phase1_complete"] = True
    return True


# ── Phase 2 — Tune ────────────────────────────────────────────────────────────

def phase2(state: dict) -> bool:
    log("=== Phase 2: Coordinate descent (CW params, 8 images, MPS) ===")

    baseline_m = read_metrics(Path(RUNS_ROOT) / "baseline_none")
    if not baseline_m:
        log("Phase 2: no baseline metrics — run phase 1 first")
        return False
    baseline_conf = get_avg_conf(baseline_m) or 1.0

    def score_fn(params: dict, run_name: str) -> float:
        run_single(
            attack="cw", defense="none", run_name=run_name,
            overrides=params,
        )
        m = read_metrics(Path(RUNS_ROOT) / run_name)
        if not m:
            return -1.0
        conf = get_avg_conf(m) or baseline_conf
        return baseline_conf - conf   # higher = more attack effect = better

    best_params, best_score, history = _coordinate_descent(
        label="cw",
        param_space=CW_PARAM_SPACE,
        score_fn=score_fn,
        run_prefix="cw_tune",
        existing_history=state.get("tune_history"),
    )

    log(f"Phase 2 done. best_score={best_score:.4f}  params={_fmt(best_params)}")
    state["best_params"] = best_params
    state["best_tune_score"] = round(best_score, 6)
    state["tune_history"] = history
    state["phase2_complete"] = True
    return True


# ── Phase 3 — Validate ────────────────────────────────────────────────────────

def phase3(state: dict) -> bool:
    log(f"=== Phase 3: Validate (best CW × all defenses, {VALIDATE_IMAGES} images) ===")

    best_params = state.get("best_params")
    if not best_params:
        log("Phase 3: no best_params from phase 2 — aborting")
        return False

    # Run baseline and bare CW attack at full validation image count
    run_single(
        attack="none", defense="none",
        run_name="baseline_none_50",
        max_images=VALIDATE_IMAGES,
        validation=True,
    )
    run_single(
        attack="cw", defense="none",
        run_name="cw_best_no_defense",
        max_images=VALIDATE_IMAGES,
        overrides=best_params,
        validation=True,
    )

    baseline_m = read_metrics(Path(RUNS_ROOT) / "baseline_none_50")
    attack_m   = read_metrics(Path(RUNS_ROOT) / "cw_best_no_defense")

    if not baseline_m or not attack_m:
        log("Phase 3: missing baseline or attack metrics")
        return False

    baseline_conf = get_avg_conf(baseline_m) or 1.0
    attack_conf   = get_avg_conf(attack_m)   or baseline_conf
    drop = baseline_conf - attack_conf

    validation_results: dict[str, dict] = {}

    log(f"  baseline_conf={baseline_conf:.4f}  attack_conf={attack_conf:.4f}  "
        f"drop={drop:.4f}")

    for defense in ALL_DEFENSES:
        run_name = f"cw_best_{defense}"
        run_single(
            attack="cw", defense=defense,
            run_name=run_name,
            max_images=VALIDATE_IMAGES,
            overrides=best_params,
            validation=True,
        )
        m = read_metrics(Path(RUNS_ROOT) / run_name)
        if not m:
            log(f"  {defense}: no metrics (skipped or failed)")
            continue
        def_conf = get_avg_conf(m) or attack_conf
        recovery = (def_conf - attack_conf) / drop if drop > 1e-6 else 0.0
        validation_results[defense] = {
            "defense_conf": round(def_conf, 6),
            "recovery": round(recovery, 4),
        }
        log(f"  {defense:25s}  def_conf={def_conf:.4f}  recovery={recovery:+.3f}")

    state["validation_results"] = validation_results
    state["phase3_complete"] = True

    _print_summary(state, baseline_conf, attack_conf, drop)
    return True


def _print_summary(state: dict, baseline_conf: float, attack_conf: float, drop: float) -> None:
    log("")
    log("=" * 60)
    log("CW Tune — Final Summary")
    log("=" * 60)
    log(f"  Best params: {_fmt(state['best_params'])}")
    log(f"  Baseline conf : {baseline_conf:.4f}")
    log(f"  CW attack conf: {attack_conf:.4f}  (drop={drop:.4f})")
    log("")
    log(f"  {'Defense':<25s}  {'Recovery':>10s}")
    log(f"  {'-'*25}  {'-'*10}")
    results = sorted(
        state["validation_results"].items(),
        key=lambda x: x[1].get("recovery", -99),
        reverse=True,
    )
    for defense, r in results:
        log(f"  {defense:<25s}  {r['recovery']:>+10.3f}")
    log("=" * 60)


# ── Lock ──────────────────────────────────────────────────────────────────────

class _Lock:
    def __init__(self):
        OUTPUTS.mkdir(parents=True, exist_ok=True)
        self._fh = open(LOCK_FILE, "w")

    def __enter__(self):
        try:
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("Another cw_tune instance is already running. Exiting.")
            sys.exit(1)
        return self

    def __exit__(self, *_):
        fcntl.flock(self._fh, fcntl.LOCK_UN)
        self._fh.close()
        LOCK_FILE.unlink(missing_ok=True)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--status", action="store_true", help="Print state and exit")
    parser.add_argument("--reset",  action="store_true", help="Delete state and start fresh")
    args = parser.parse_args()

    if args.status:
        if STATE_FILE.exists():
            state = load_state()
            print(json.dumps(state, indent=2))
        else:
            print("No state file found.")
        return

    if args.reset:
        STATE_FILE.unlink(missing_ok=True)
        print("State reset. Run without --reset to start fresh.")
        return

    with _Lock():
        state = load_state()

        if not state["phase1_complete"]:
            if not phase1(state):
                log("Phase 1 failed — exiting")
                return
            save_state(state)
            git_commit_phase(1, state)

        if not state["phase2_complete"]:
            if not phase2(state):
                log("Phase 2 failed — exiting")
                return
            save_state(state)
            git_commit_phase(2, state)

        if not state["phase3_complete"]:
            if not phase3(state):
                log("Phase 3 failed — exiting")
                return
            save_state(state)
            git_commit_phase(3, state)

        log("All phases complete.")


if __name__ == "__main__":
    main()
