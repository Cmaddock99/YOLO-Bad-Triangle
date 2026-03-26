#!/usr/bin/env python3
"""scripts/auto_cycle.py

Automated test-and-tune cycle for YOLO-Bad-Triangle.

Four phases run sequentially. State is persisted so the cycle is fully
resumable — re-invoke the script at any point to continue from where it
left off.

  Phase 1  Characterize   All attacks vs no defense (smoke, 8 images).
                           Ranks attacks by composite suppression
                           (avg-confidence + detection-count health).

  Phase 2  Matrix         Top-N attacks × all defenses (smoke, 8 images).
                           Ranks defenses by composite recovery
                           (relative to composite suppression in Phase 1).
                           (smoke is enough for ranking — full runs in Phase 4)

  Phase 3  Tune           Adaptive coordinate descent for top attacks × top
                           defenses (8 images).  After each run, assesses the
                           result and probes the most promising direction until
                           gains fall below a tolerance threshold.

  Phase 4  Validate       Best configs re-run: full dataset + mAP50.

State:   outputs/cycle_state.json
Lock:    outputs/.cycle.lock   (prevents concurrent execution)
Log:     logs/auto_cycle.log

Usage:
  PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py          # run / resume
  PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --loop   # run continuously
  PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --status # show state
  PYTHONPATH=src ./.venv/bin/python scripts/auto_cycle.py --reset  # start fresh

Loop mode:
  Each completed cycle saves a summary to outputs/cycle_history/ and immediately
  starts the next cycle, carrying the best-found attack/defense params forward as
  the starting point for Phase 3 coordinate descent — so each cycle tightens from
  where the last one left off rather than restarting from defaults.
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
STATE_FILE = OUTPUTS / "cycle_state.json"
WARM_START_FILE = OUTPUTS / "cycle_warm_start.json"
LOCK_FILE  = OUTPUTS / ".cycle.lock"
PAUSE_FILE = OUTPUTS / ".cycle.pause"
HISTORY_DIR = OUTPUTS / "cycle_history"
LOG_DIR = REPO / "logs"
PYTHON = REPO / ".venv" / "bin" / "python"

# ── Attack / defense catalogues ───────────────────────────────────────────────

ALL_ATTACKS: list[str] = [
    "blur", "deepfool", "eot_pgd", "fgsm", "jpeg_attack", "pgd", "square",
]
ALL_DEFENSES: list[str] = [
    "bit_depth", "c_dog", "c_dog_ensemble", "jpeg_preprocess",
    "median_preprocess",
    # random_resize removed — inherent mAP50 cost (−0.25) exceeds any attack-recovery benefit
]

TOP_N_ATTACKS = 3
TOP_N_DEFENSES = 3   # bumped from 2 — catalogue now has 6 defenses

# ── Adaptive tuning: parameter spaces ─────────────────────────────────────────
# Each param spec: init (starting value), min/max (bounds), and one of:
#   scale="log"          — float, try ×factor and ÷factor each step
#   scale="linear_float" — float, try ±step each step
#   scale="odd_int"      — int constrained to odd values, try ±step
#   scale="int"          — plain int, try ±step

ATTACK_PARAM_SPACE: dict[str, dict[str, dict]] = {
    "fgsm": {
        "attack.params.epsilon": {"init": 0.01,  "min": 0.001, "max": 0.3,  "scale": "log", "factor": 2.0},
    },
    "pgd": {
        "attack.params.epsilon": {"init": 0.016, "min": 0.002, "max": 0.25, "scale": "log", "factor": 2.0},
        "attack.params.steps":   {"init": 20,    "min": 5,     "max": 80,   "scale": "int",  "step": 10},
    },
    "deepfool": {
        "attack.params.epsilon": {"init": 0.05,  "min": 0.005, "max": 0.3,  "scale": "log", "factor": 2.0},
        "attack.params.steps":   {"init": 50,    "min": 10,    "max": 120,  "scale": "int",  "step": 20},
    },
    "eot_pgd": {
        "attack.params.epsilon":    {"init": 0.016, "min": 0.002, "max": 0.25, "scale": "log", "factor": 2.0},
        "attack.params.eot_samples":{"init": 4,     "min": 2,     "max": 16,   "scale": "int",  "step": 2},
    },
    "blur": {
        "attack.params.kernel_size": {"init": 25, "min": 3, "max": 51, "scale": "odd_int", "step": 4},
    },
    "jpeg_attack": {
        "attack.params.quality": {"init": 75, "min": 10, "max": 95, "scale": "int", "step": 15},
    },
    "square": {
        "attack.params.eps":       {"init": 0.05,  "min": 0.01, "max": 0.3,  "scale": "log", "factor": 2.0},
        "attack.params.n_queries": {"init": 100,   "min": 50,   "max": 500,  "scale": "int",  "step": 50},
    },
}

DEFENSE_PARAM_SPACE: dict[str, dict[str, dict]] = {
    "median_preprocess": {
        "defense.params.kernel_size": {"init": 7,    "min": 3,   "max": 31,  "scale": "odd_int",      "step": 2},
    },
    "c_dog": {
        "defense.params.timestep":      {"init": 50.0, "min": 10.0, "max": 90.0, "scale": "linear_float", "step": 15.0},
        "defense.params.sharpen_alpha": {"init": 0.0,  "min": 0.0,  "max": 0.7,  "scale": "linear_float", "step": 0.2},
    },
    "c_dog_ensemble": {
        "defense.params.sharpen_alpha": {"init": 0.3,  "min": 0.0,  "max": 0.7,  "scale": "linear_float", "step": 0.15},
        "defense.params.median_kernel": {"init": 3,    "min": 3,    "max": 11,   "scale": "odd_int",      "step": 2},
    },
    "jpeg_preprocess": {
        "defense.params.quality": {"init": 75, "min": 40, "max": 95, "scale": "int", "step": 15},
    },
    "bit_depth": {
        "defense.params.bits": {"init": 5, "min": 3, "max": 7, "scale": "int", "step": 1},
    },
}

# Images used during tuning — keep small when slow attacks (e.g. square)
# are in the catalogue. 8 matches Phase 1 smoke size for consistency.
TUNE_MAX_IMAGES = 8

# Attacks too slow for NUC Phase 4 (500-image full validation).
# Skip these in Phase 4; Mac's standalone sweep handles their validation.
SLOW_ATTACKS: set[str] = {"square", "eot_pgd"}  # ~126s/img and ~48s/img on NUC CPU

# Coordinate descent settings
TUNE_MAX_ITERS = 15          # max passes over all parameters (global default)
TUNE_TOLERANCE_REL = 0.05    # minimum *relative* improvement to count as a gain
                              # relative keeps weak attacks from accepting noise
                              # and strong attacks from missing real gains

# Per-defense iteration cap. Small param spaces converge in 2-3 passes;
# running 15 wastes hours when slow attacks are in the catalogue.
TUNE_MAX_ITERS_BY_DEFENSE: dict[str, int] = {
    "c_dog_ensemble":    3,   # 2 params, small ranges — converges fast
    "bit_depth":         3,   # 1 param, 5 discrete values
    "jpeg_preprocess":   5,   # 1 param, moderate range
    "median_preprocess": 6,   # 1 param, wide range
    "c_dog":             8,   # 2 params, wider ranges
}

# Defenses known to carry high inherent accuracy cost even without attacks.
# auto_cycle logs a warning when these appear in the top-N ranked defenses so
# the user knows to validate Phase 4 mAP50 before drawing conclusions.
# random_resize removed from catalogue entirely — no longer needs flagging.
FLAGGED_DEFENSES: set[str] = set()

# Defenses always included in top-N selection regardless of ranking.
# Ensures the learned denoiser (c_dog) is always tuned and validated
# so the retraining loop can measure improvement across cycles.
PINNED_DEFENSES: list[str] = ["c_dog"]


# ── Startup param-space validation ────────────────────────────────────────────

def _validate_param_spaces() -> None:
    """Assert that every 'init' value lies within [min, max] bounds.

    Catches typos at import time rather than silently starting coord descent
    out of range.
    """
    for space_name, space in (
        ("ATTACK_PARAM_SPACE", ATTACK_PARAM_SPACE),
        ("DEFENSE_PARAM_SPACE", DEFENSE_PARAM_SPACE),
    ):
        for item, params in space.items():
            for param, cfg in params.items():
                lo, hi, init = cfg["min"], cfg["max"], cfg["init"]
                assert lo <= init <= hi, (
                    f"{space_name}[{item}][{param}] init={init} "
                    f"out of bounds [{lo}, {hi}]"
                )

_validate_param_spaces()


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "auto_cycle.log", "a") as fh:
        fh.write(line + "\n")


# ── State ─────────────────────────────────────────────────────────────────────

def init_state() -> dict:
    cycle_id = datetime.now().strftime("cycle_%Y%m%d_%H%M%S")
    return {
        "cycle_id": cycle_id,
        "started_at": datetime.now().isoformat(),
        "current_phase": 1,
        "runs_root": str(OUTPUTS / "framework_runs" / cycle_id),
        "report_root": str(OUTPUTS / "framework_reports" / cycle_id),
        "phase1_complete": False,
        "phase2_complete": False,
        "phase3_complete": False,
        "phase4_complete": False,
        "complete": False,
        # filled in after each analysis step
        "top_attacks": [],
        "top_defenses": [],
        "best_attack_params": {},   # {attack_name: {set_key: value, ...}}
        "best_defense_params": {},  # {defense_name: {set_key: value, ...}}
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


def get_total_detections(m: dict) -> int:
    return int(m.get("predictions", {}).get("total_detections", 0))


def _composite_score(m: dict, baseline_conf: float, baseline_det: int) -> float:
    """Model health score relative to baseline: 1.0 = no degradation, 0.0 = total suppression.

    Weighted 50/50 between normalised avg_conf and normalised detection count.
    Using both catches attacks that suppress detections without reducing confidence
    (e.g. CW, high-eps square) as well as attacks that reduce confidence without
    fully eliminating detections (e.g. FGSM at low epsilon).

    Note: avg_conf is computed only over detections that were made — when a
    strong attack suppresses 60% of detections the remaining detections may be
    the most-confident ones, so avg_conf alone can *rise* under attack.  The
    detection-count component prevents this blind spot.
    """
    conf = get_avg_conf(m) or 0.0
    det = get_total_detections(m)
    conf_ratio = conf / baseline_conf if baseline_conf > 0 else 1.0
    det_ratio = det / baseline_det if baseline_det > 0 else 1.0
    return 0.5 * conf_ratio + 0.5 * det_ratio


def get_map50(m: dict) -> float | None:
    return m.get("validation", {}).get("mAP50")


# ── Subprocess helpers ────────────────────────────────────────────────────────

def _env() -> dict:
    cpu_count = str(os.cpu_count() or 4)
    env = {
        **os.environ,
        "PYTHONPATH": str(REPO / "src"),
        # Use all available CPU cores for PyTorch / OpenMP / MKL
        "OMP_NUM_THREADS": cpu_count,
        "MKL_NUM_THREADS": cpu_count,
        "OPENBLAS_NUM_THREADS": cpu_count,
        "NUMEXPR_NUM_THREADS": cpu_count,
    }
    # Ensure c_dog defense can find its checkpoint. Prefer the env var already
    # set by the user; fall back to the standard filename in the repo root.
    if not env.get("DPC_UNET_CHECKPOINT_PATH"):
        for candidate in ("dpc_unet_adversarial_finetuned.pt", "dpc_unet_final_golden.pt"):
            path = REPO / candidate
            if path.exists():
                env["DPC_UNET_CHECKPOINT_PATH"] = str(path)
                break
    return env


def run_sweep(
    *,
    attacks: list[str],
    defenses: list[str],
    runs_root: str,
    report_root: str,
    sweep_phases: str,
    preset: str = "smoke",
    validation: bool = False,
    workers: int = 1,
) -> bool:
    """Call sweep_and_report.py and return True on success."""
    cmd = [
        str(PYTHON), "scripts/sweep_and_report.py",
        "--attacks", ",".join(attacks),
        "--defenses", ",".join(defenses),
        "--runs-root", runs_root,
        "--report-root", report_root,
        "--preset", preset,
        "--phases", sweep_phases,
        "--resume",
        "--skip-errors",
        "--workers", str(workers),
    ]
    if validation:
        cmd.append("--validation-enabled")
    log(f"sweep phases={sweep_phases} attacks={attacks} defenses={defenses} "
        f"preset={preset} validation={validation}")
    result = subprocess.run(cmd, cwd=str(REPO), env=_env())
    return result.returncode == 0


def run_single(
    *,
    attack: str,
    defense: str,
    run_name: str,
    runs_root: str,
    overrides: dict | None = None,
    preset: str = "smoke",
    validation: bool = False,
) -> bool:
    """Call run_unified.py for one experiment. Skip if metrics.json already exists."""
    run_dir = Path(runs_root) / run_name
    if (run_dir / "metrics.json").exists():
        log(f"  skip (exists): {run_name}")
        return True

    # "tune" preset: more images than smoke for reliable signal, less than full
    max_images = {"smoke": "8", "tune": str(TUNE_MAX_IMAGES), "full": "0"}.get(preset, "0")
    cmd = [
        str(PYTHON), "scripts/run_unified.py", "run-one",
        "--config", "configs/default.yaml",
        "--set", f"attack.name={attack}",
        "--set", f"defense.name={defense}",
        "--set", f"runner.run_name={run_name}",
        "--set", f"runner.output_root={runs_root}",
        "--set", f"runner.max_images={max_images}",
    ]
    if validation:
        cmd += ["--set", "validation.enabled=true"]
    for key, val in (overrides or {}).items():
        cmd += ["--set", f"{key}={val}"]

    log(f"  run: {run_name}")
    result = subprocess.run(cmd, cwd=str(REPO), env=_env())
    return result.returncode == 0


def generate_report(state: dict) -> None:
    """Regenerate framework report over all runs collected so far."""
    log("Generating report...")
    run_sweep(
        attacks=["none"],   # content doesn't matter for phase 4 (report only)
        defenses=["none"],
        runs_root=state["runs_root"],
        report_root=state["report_root"],
        sweep_phases="4",
    )


# ── Phase 1 — Characterize ────────────────────────────────────────────────────

def phase1(state: dict) -> bool:
    log("=== Phase 1: Characterize (all attacks, smoke) ===")
    ok = run_sweep(
        attacks=ALL_ATTACKS,
        defenses=["none"],
        runs_root=state["runs_root"],
        report_root=state["report_root"],
        sweep_phases="1,2",   # baseline + attack-only runs
    )
    if not ok:
        log("Phase 1 had errors — continuing with available data")

    top = _rank_attacks(state)
    if not top:
        log("Phase 1: no usable attack results; aborting")
        return False

    state["top_attacks"] = top
    state["phase1_complete"] = True
    state["current_phase"] = 2
    log(f"Phase 1 done. Top attacks: {top}")
    return True


def _rank_attacks(state: dict) -> list[str]:
    runs_root = Path(state["runs_root"])
    baseline_m = read_metrics(runs_root / "baseline_none")
    if not baseline_m:
        log("  No baseline metrics found")
        return []
    baseline_conf = get_avg_conf(baseline_m) or 0.0
    baseline_det = get_total_detections(baseline_m)

    scores: list[tuple[float, str]] = []
    for attack in ALL_ATTACKS:
        m = read_metrics(runs_root / f"attack_{attack}")
        if not m:
            continue
        health = _composite_score(m, baseline_conf, baseline_det)
        suppression = 1.0 - health  # higher = attack more effective
        log(f"  {attack:20s}  suppression={suppression:+.4f}  "
            f"(conf={get_avg_conf(m) or 0.0:.4f}  "
            f"det={get_total_detections(m)}/{baseline_det})")
        scores.append((suppression, attack))

    scores.sort(reverse=True)
    return [a for _, a in scores[:TOP_N_ATTACKS]]


# ── Phase 2 — Matrix ──────────────────────────────────────────────────────────

def phase2(state: dict) -> bool:
    log(f"=== Phase 2: Matrix ({state['top_attacks']} × all defenses, smoke) ===")
    # Use smoke preset (8 images) — just enough to rank defenses reliably.
    # Full validated runs happen in Phase 4; no need to spend hours here.
    ok = run_sweep(
        attacks=state["top_attacks"],
        defenses=ALL_DEFENSES,
        runs_root=state["runs_root"],
        report_root=state["report_root"],
        sweep_phases="1,2,3",
        preset="smoke",
    )
    if not ok:
        log("Phase 2 had errors — continuing with available data")

    top = _rank_defenses(state)
    if not top:
        log("Phase 2: no usable defense results")
        return False

    state["top_defenses"] = top
    state["phase2_complete"] = True
    state["current_phase"] = 3
    log(f"Phase 2 done. Top defenses: {top}")
    return True


def _rank_defenses(state: dict) -> list[str]:
    runs_root = Path(state["runs_root"])
    baseline_m = read_metrics(runs_root / "baseline_none")
    baseline_conf = (get_avg_conf(baseline_m) or 0.0) if baseline_m else 0.0
    baseline_det = get_total_detections(baseline_m) if baseline_m else 0

    recovery_by_defense: dict[str, list[float]] = {d: [] for d in ALL_DEFENSES}

    for attack in state["top_attacks"]:
        attack_m = read_metrics(runs_root / f"attack_{attack}")
        if not attack_m:
            continue
        attack_health = _composite_score(attack_m, baseline_conf, baseline_det)
        suppression = 1.0 - attack_health
        if suppression < 1e-4:
            log(f"  {attack:20s}  skipping — no measurable composite suppression")
            continue  # attack had no measurable effect

        for defense in ALL_DEFENSES:
            def_m = read_metrics(runs_root / f"defended_{attack}_{defense}")
            if not def_m:
                continue
            def_health = _composite_score(def_m, baseline_conf, baseline_det)
            recovery = (def_health - attack_health) / suppression
            log(f"  {attack:20s} + {defense:25s}  composite_recovery={recovery:+.3f}")
            recovery_by_defense[defense].append(recovery)

    avg_scores: list[tuple[float, str]] = []
    for defense, vals in recovery_by_defense.items():
        avg = sum(vals) / len(vals) if vals else 0.0
        avg_scores.append((avg, defense))
        log(f"  {defense:25s}  avg_composite_recovery={avg:.3f}  (n={len(vals)})")

    avg_scores.sort(reverse=True)
    top = [d for _, d in avg_scores[:TOP_N_DEFENSES]]

    # Ensure pinned defenses are always included (e.g. c_dog for retraining loop)
    for pd in PINNED_DEFENSES:
        if pd not in top and pd in ALL_DEFENSES:
            top.append(pd)
            log(f"  {pd:25s}  pinned — always included for retraining loop evaluation")

    for d in top:
        if d in FLAGGED_DEFENSES:
            log(
                f"  [warn] '{d}' is in FLAGGED_DEFENSES — it has high inherent accuracy cost "
                f"(mAP50 typically drops 0.2+ even without attack). "
                f"Validate Phase 4 mAP50 before drawing conclusions."
            )

    return top


# ── Adaptive tuner ────────────────────────────────────────────────────────────

def _clamp(value, spec: dict):
    """Return value clamped to [spec.min, spec.max], cast to the right type."""
    lo, hi = spec["min"], spec["max"]
    if spec["scale"] in ("int", "odd_int"):
        return int(max(lo, min(hi, int(value))))
    return float(max(lo, min(hi, float(value))))


def _candidates(spec: dict, current) -> list:
    """Generate up to two candidate values to probe from the current position."""
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
        if up   % 2 == 0: up   += 1
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


def _run_and_score_attack(attack, params, run_name, runs_root,
                          baseline_conf, baseline_det):
    run_single(attack=attack, defense="none", run_name=run_name,
               runs_root=runs_root, overrides=params, preset="tune")
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    # suppression: higher = attack was more effective (composite score closer to 0)
    return 1.0 - _composite_score(m, baseline_conf, baseline_det)


def _run_and_score_defense(attack, defense, params, run_name, runs_root,
                            baseline_conf, baseline_det, attack_composite):
    run_single(attack=attack, defense=defense, run_name=run_name,
               runs_root=runs_root, overrides=params, preset="tune")
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    suppression = 1.0 - attack_composite
    if suppression < 1e-4:
        return 0.0  # attack had negligible composite effect — recovery undefined
    def_composite = _composite_score(m, baseline_conf, baseline_det)
    return (def_composite - attack_composite) / suppression


def _coordinate_descent(label, param_space, score_fn, run_prefix,
                         existing_history=None, max_iters: int | None = None):
    """
    Coordinate descent over param_space.

    Each iteration loops over every parameter, probes one step up and one step
    down, and commits to whichever direction improved the score by more than
    TUNE_TOLERANCE.  Stops when a full pass finds no improvement, or after
    max_iters passes (defaults to TUNE_MAX_ITERS).

    Returns (best_params, best_score, history).
    """
    _max_iters = max_iters if max_iters is not None else TUNE_MAX_ITERS
    history = list(existing_history or [])
    counter = [len(history)]

    def next_name():
        counter[0] += 1
        return f"{run_prefix}_{counter[0]:03d}"[:80]

    current = {k: spec["init"] for k, spec in param_space.items()}
    current_score = score_fn(current, next_name())
    log(f"  [{label}] init  score={current_score:.4f}  "
        f"params={_fmt(current)}")
    history.append({"iter": 0, "param": "init", "value": None,
                    "score": current_score, "delta": 0.0, "improved": True})

    for iteration in range(1, _max_iters + 1):
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
                    best_candidate_score - current_score
                    > abs(current_score) * TUNE_TOLERANCE_REL):
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


def _fmt(params: dict) -> str:
    return "  ".join(f"{k.split('.')[-1]}={v}" for k, v in params.items())


# ── Phase 3 — Tune ────────────────────────────────────────────────────────────

def phase3(state: dict) -> bool:
    log(f"=== Phase 3: Adaptive Tune "
        f"({state['top_attacks']} × {state['top_defenses']}, "
        f"{TUNE_MAX_IMAGES} imgs) ===")
    runs_root = state["runs_root"]
    tune_history = state.setdefault("tune_history", {})

    baseline_m = read_metrics(Path(runs_root) / "baseline_none")
    baseline_conf = (get_avg_conf(baseline_m) or 1.0) if baseline_m else 1.0
    baseline_det = get_total_detections(baseline_m) if baseline_m else 0

    # ── Step 1: Tune each top attack (no defense) ─────────────────────────────
    for attack in state["top_attacks"]:
        space = ATTACK_PARAM_SPACE.get(attack)
        if not space:
            log(f"  No param space for {attack}, skipping")
            state.setdefault("best_attack_params", {})[attack] = {}
            continue

        existing = tune_history.get(f"attack_{attack}", [])

        def _atk_score(params, name, _a=attack, _bc=baseline_conf, _bd=baseline_det):
            return _run_and_score_attack(_a, params, name, runs_root, _bc, _bd)

        best_params, best_score, history = _coordinate_descent(
            label=attack, param_space=space,
            score_fn=_atk_score,
            run_prefix=f"tune_atk_{attack}",
            existing_history=existing,
        )
        tune_history[f"attack_{attack}"] = history
        state.setdefault("best_attack_params", {})[attack] = best_params
        log(f"  {attack} → {best_params}  suppression={best_score:.4f}")
        save_state(state)

    # ── Step 2: Baseline for defense tuning using best-tuned attack ───────────
    # Evaluate defenses against the hardest version of the attack, not the
    # Phase-1 default-params run.
    strongest = state["top_attacks"][0]
    best_atk_params = state.get("best_attack_params", {}).get(strongest, {})
    tuned_atk_run = f"tune_atk_{strongest}_best"
    run_single(attack=strongest, defense="none",
               run_name=tuned_atk_run, runs_root=runs_root,
               overrides=best_atk_params, preset="tune")
    tuned_m = read_metrics(Path(runs_root) / tuned_atk_run)
    attack_composite = (
        _composite_score(tuned_m, baseline_conf, baseline_det) if tuned_m else 1.0
    )
    log(f"  Tuned attack composite={attack_composite:.4f}  "
        f"(suppression={1.0 - attack_composite:.4f} vs baseline)")

    # ── Step 3: Tune each top defense against the best attack ─────────────────
    for defense in state["top_defenses"]:
        space = DEFENSE_PARAM_SPACE.get(defense)
        if not space:
            log(f"  No param space for {defense}, skipping")
            state.setdefault("best_defense_params", {})[defense] = {}
            continue

        existing = tune_history.get(f"defense_{defense}", [])

        def _def_score(params, name, _s=strongest, _d=defense,
                       _bc=baseline_conf, _bd=baseline_det, _ac=attack_composite):
            return _run_and_score_defense(_s, _d, params, name,
                                          runs_root, _bc, _bd, _ac)

        best_params, best_score, history = _coordinate_descent(
            label=defense, param_space=space,
            score_fn=_def_score,
            run_prefix=f"tune_def_{defense}",
            existing_history=existing,
            max_iters=TUNE_MAX_ITERS_BY_DEFENSE.get(defense, TUNE_MAX_ITERS),
        )
        tune_history[f"defense_{defense}"] = history
        state.setdefault("best_defense_params", {})[defense] = best_params
        log(f"  {defense} → {best_params}  recovery={best_score:.3f}")
        save_state(state)

    state["phase3_complete"] = True
    state["current_phase"] = 4
    log(f"Phase 3 done.")
    log(f"  Best attack params:  {state.get('best_attack_params')}")
    log(f"  Best defense params: {state.get('best_defense_params')}")
    return True


# ── Phase 4 — Validate ────────────────────────────────────────────────────────

def phase4(state: dict) -> bool:
    log("=== Phase 4: Validate (full dataset, mAP50) ===")
    runs_root = state["runs_root"]
    best_atk = state.get("best_attack_params", {})
    best_def = state.get("best_defense_params", {})

    # Baseline
    run_single(attack="none", defense="none",
               run_name="validate_baseline",
               runs_root=runs_root, preset="full", validation=True)

    # Best attack configs (no defense) — skip slow attacks; Mac handles those
    for attack in state["top_attacks"]:
        if attack in SLOW_ATTACKS:
            log(f"  Skipping Phase 4 for {attack} (slow attack — Mac handles validation)")
            continue
        run_single(
            attack=attack, defense="none",
            run_name=f"validate_atk_{attack}",
            runs_root=runs_root,
            overrides=best_atk.get(attack),
            preset="full", validation=True,
        )

    # Best attack × defense combos — skip slow attacks on NUC
    for attack in state["top_attacks"]:
        if attack in SLOW_ATTACKS:
            continue
        for defense in state["top_defenses"]:
            merged = {**(best_atk.get(attack) or {}), **(best_def.get(defense) or {})}
            run_single(
                attack=attack, defense=defense,
                run_name=f"validate_{attack}_{defense}",
                runs_root=runs_root,
                overrides=merged or None,
                preset="full", validation=True,
            )

    state["phase4_complete"] = True
    state["complete"] = True
    state["finished_at"] = datetime.now().isoformat()
    log(f"Phase 4 done. Reports at: {state['report_root']}")
    return True


# ── Loop-mode helpers ─────────────────────────────────────────────────────────

def save_cycle_history(state: dict) -> None:
    """Persist a summary of the completed cycle to outputs/cycle_history/."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    # Collect Phase-4 validation metrics from completed runs
    validation_results = {}
    runs_root = Path(state["runs_root"])
    for mf in sorted(runs_root.glob("validate_*/metrics.json")):
        try:
            m = json.loads(mf.read_text())
            s = json.loads((mf.parent / "run_summary.json").read_text())
            validation_results[mf.parent.name] = {
                "attack":   s.get("attack",  {}).get("name"),
                "defense":  s.get("defense", {}).get("name"),
                "avg_conf": get_avg_conf(m),
                "mAP50":    get_map50(m),
                "mAP50_95": m.get("validation", {}).get("mAP50-95"),
                "precision":m.get("validation", {}).get("precision"),
                "recall":   m.get("validation", {}).get("recall"),
                "detections": m["predictions"].get("total_detections"),
            }
        except Exception:
            pass

    summary = {
        "cycle_id":          state["cycle_id"],
        "started_at":        state.get("started_at"),
        "finished_at":       state.get("finished_at"),
        "top_attacks":       state.get("top_attacks", []),
        "top_defenses":      state.get("top_defenses", []),
        "best_attack_params":state.get("best_attack_params", {}),
        "best_defense_params":state.get("best_defense_params", {}),
        "validation_results":validation_results,
    }
    out = HISTORY_DIR / f"{state['cycle_id']}.json"
    out.write_text(json.dumps(summary, indent=2))
    log(f"Cycle history saved: {out}")

    _write_training_signal(state, validation_results)
    _update_cycle_report()


def _update_cycle_report() -> None:
    """Regenerate outputs/cycle_report.csv + outputs/cycle_report.md (non-fatal)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_cycle_report", REPO / "scripts" / "generate_cycle_report.py"
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            csv_path, md_path = mod.generate_reports()
            log(f"Cycle report updated: {md_path}")
    except Exception as exc:
        log(f"[warn] _update_cycle_report failed (non-fatal): {exc}")


def _write_training_signal(state: dict, validation_results: dict) -> None:
    """Write outputs/cycle_training_signal.json identifying the attack/defense
    pair most in need of adversarial retraining.

    Signal format:
      worst_attack:  the attack with the lowest average detection recovery across defenses
      worst_attack_params: tuned params for that attack
      weakest_defense: the defense that recovered least against worst_attack
      weakest_defense_recovery: its recovery score (0.0 = no recovery, 1.0 = full)
      cycle_id: which cycle produced this signal

    Colab reads this file to generate adversarial training pairs with worst_attack
    at worst_attack_params, targeting weakest_defense's training distribution.
    """
    try:
        baseline_dets = None
        attack_dets_map: dict[str, int] = {}
        defense_recovery: dict[str, dict[str, float]] = {}  # attack → {defense: recovery}

        # Extract baseline — attack/defense can be None or the string "none"
        for run_name, v in validation_results.items():
            atk = v.get("attack")
            dfn = v.get("defense")
            if atk in (None, "none") and dfn in (None, "none"):
                baseline_dets = v.get("detections")
                break

        if baseline_dets is None or baseline_dets == 0:
            log("_write_training_signal: no baseline detections — skipping")
            return

        # Extract per-attack detection counts
        for run_name, v in validation_results.items():
            atk = v.get("attack")
            dfn = v.get("defense")
            dets = v.get("detections")
            if dets is None:
                continue
            atk_is_real = atk and atk != "none"
            dfn_is_real = dfn and dfn != "none"
            if atk_is_real and not dfn_is_real:
                attack_dets_map[atk] = dets
            elif atk_is_real and dfn_is_real:
                drop = baseline_dets - attack_dets_map.get(atk, baseline_dets)
                if drop > 0:
                    recovery = (dets - attack_dets_map.get(atk, dets)) / drop
                    defense_recovery.setdefault(atk, {})[dfn] = recovery

        if not defense_recovery:
            log("_write_training_signal: no defense recovery data — skipping")
            return

        # Find attack with lowest average defense recovery (hardest to defend)
        atk_avg: list[tuple[float, str]] = []
        for atk, rmap in defense_recovery.items():
            avg = sum(rmap.values()) / len(rmap) if rmap else 1.0
            atk_avg.append((avg, atk))
        atk_avg.sort()  # lowest recovery first
        worst_attack = atk_avg[0][1]

        # Find weakest defense against worst_attack
        rmap = defense_recovery[worst_attack]
        weakest_defense = min(rmap, key=lambda d: rmap[d])
        weakest_recovery = rmap[weakest_defense]

        signal = {
            "cycle_id":               state["cycle_id"],
            "generated_at":           state.get("finished_at"),
            "worst_attack":           worst_attack,
            "worst_attack_params":    state.get("best_attack_params", {}).get(worst_attack, {}),
            "weakest_defense":        weakest_defense,
            "weakest_defense_recovery": round(weakest_recovery, 4),
            "all_attack_avg_recovery": {a: round(s, 4) for s, a in atk_avg},
        }
        sig_path = OUTPUTS / "cycle_training_signal.json"
        sig_path.write_text(json.dumps(signal, indent=2))
        log(f"Training signal: {worst_attack} bypassed {weakest_defense} "
            f"(recovery={weakest_recovery:.3f}) → {sig_path}")
    except Exception as exc:
        log(f"_write_training_signal: failed (non-fatal) — {exc}")


def wait_if_paused(after_phase: int) -> None:
    """Block until outputs/.cycle.pause is removed. Called between phases so
    the user can inspect results before the next phase begins.
    Create the file to pause: touch outputs/.cycle.pause
    Remove it to resume:      rm outputs/.cycle.pause"""
    if PAUSE_FILE.exists():
        log(f"PAUSED after phase {after_phase} — remove outputs/.cycle.pause to resume")
        while PAUSE_FILE.exists():
            time.sleep(10)
        log(f"Resuming from phase {after_phase + 1}")


def git_pull() -> None:
    """Pull latest changes from remote. Called at the start of each new cycle
    so new plugins, param-space tweaks, and bug fixes are picked up automatically."""
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only", "origin", "main"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        if result.returncode == 0:
            msg = result.stdout.strip() or "already up to date"
            log(f"git_pull: {msg}")
        else:
            log(f"git_pull: skipped (non-fast-forward or network issue) — "
                f"{result.stderr.strip()}")
    except Exception as exc:
        log(f"git_pull: error — {exc} (continuing)")


def _write_cycle_status(state: dict, phase_num: int) -> Path:
    """Write outputs/cycle_status.md — a human-readable snapshot tracked by git."""
    lines = [
        "# Auto-cycle status",
        "",
        f"cycle_id   : {state['cycle_id']}",
        f"phase      : {phase_num}/4 complete",
        f"updated_at : {datetime.now().isoformat()}",
        "",
        f"top_attacks  : {state.get('top_attacks', [])}",
        f"top_defenses : {state.get('top_defenses', [])}",
        "",
        "best_attack_params:",
    ]
    for atk, params in state.get("best_attack_params", {}).items():
        lines.append(f"  {atk}: {params}")
    lines.append("best_defense_params:")
    for dfn, params in state.get("best_defense_params", {}).items():
        lines.append(f"  {dfn}: {params}")
    lines += [
        "",
        f"P1={state['phase1_complete']}  P2={state['phase2_complete']}  "
        f"P3={state['phase3_complete']}  P4={state['phase4_complete']}",
        "",
        ("*** CYCLE COMPLETE ***"
         if phase_num == 4
         else f"*** PARTIAL — phases {phase_num+1}–4 still pending ***"),
    ]
    status_file = OUTPUTS / "cycle_status.md"
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    status_file.write_text("\n".join(lines) + "\n")
    return status_file


def git_commit_phase(state: dict, phase_num: int) -> None:
    """Commit a lightweight phase-complete snapshot so other sessions can track
    progress without waiting for a full cycle to finish."""
    phase_labels = {1: "characterize", 2: "matrix", 3: "tune", 4: "validate"}
    phase_label  = phase_labels.get(phase_num, str(phase_num))
    cycle_id     = state["cycle_id"]

    status_file = _write_cycle_status(state, phase_num)
    report_dir  = Path(state.get("report_root", ""))

    paths_to_add = [str(status_file)]
    if report_dir.exists():
        paths_to_add.append(str(report_dir))

    try:
        subprocess.run(["git", "add"] + paths_to_add, cwd=str(REPO), check=True)
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=str(REPO)
        )
        if diff.returncode == 0:
            log(f"git_commit_phase {phase_num}: nothing new to commit")
            return

        top_atk = state.get("top_attacks", [])
        top_def = state.get("top_defenses", [])

        msg_lines = [
            f"auto_cycle: {cycle_id} phase {phase_num}/{phase_label} complete",
            "",
        ]
        if top_atk:
            msg_lines.append(f"Top attacks : {', '.join(top_atk)}")
        if top_def:
            msg_lines.append(f"Top defenses: {', '.join(top_def)}")
        if phase_num >= 3:
            for atk, params in state.get("best_attack_params", {}).items():
                for k, v in params.items():
                    msg_lines.append(f"  {atk} {k.split('.')[-1]}={v}")
            for dfn, params in state.get("best_defense_params", {}).items():
                for k, v in params.items():
                    msg_lines.append(f"  {dfn} {k.split('.')[-1]}={v}")
        if phase_num < 4:
            msg_lines += [
                "",
                f"*** PARTIAL — phases {phase_num+1}–4 still pending ***",
                "See outputs/cycle_status.md for live status.",
            ]

        subprocess.run(
            ["git", "commit", "-m", "\n".join(msg_lines)],
            cwd=str(REPO), check=True,
        )
        subprocess.run(["git", "push"], cwd=str(REPO), check=True)
        log(f"git_commit_phase: pushed phase {phase_num} snapshot for {cycle_id}")
        _push_state_to_branch(state, phase_num)
    except subprocess.CalledProcessError as exc:
        log(f"git_commit_phase: failed — {exc} (continuing)")


def _push_state_to_branch(state: dict, phase_num: int) -> None:
    """Push cycle_status.md to nuc/sweep-results branch after each phase so
    the other machine can track progress without polling the main branch.

    Note: cycle_state.json is in .gitignore — use cycle_status.md (tracked).
    """
    try:
        cycle_id = state.get("cycle_id", "unknown")
        status_file = OUTPUTS / "cycle_status.md"
        subprocess.run(
            ["git", "add", str(status_file)],
            cwd=str(REPO), check=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=str(REPO)
        )
        if diff.returncode == 0:
            return  # nothing new
        subprocess.run(
            ["git", "commit", "-m", f"nuc: phase {phase_num} status [{cycle_id}]"],
            cwd=str(REPO), check=True,
        )
        subprocess.run(
            ["git", "push", "origin", "HEAD:nuc/sweep-results"],
            cwd=str(REPO), check=True,
        )
        log(f"_push_state_to_branch: pushed phase {phase_num} to nuc/sweep-results")
    except Exception as exc:
        log(f"_push_state_to_branch: failed (non-fatal) — {exc}")


def git_push_results(state: dict) -> None:
    """Commit cycle_history and framework_reports for this cycle and push."""
    cycle_id = state["cycle_id"]
    history_file = HISTORY_DIR / f"{cycle_id}.json"
    report_dir = Path(state.get("report_root", ""))

    status_file = _write_cycle_status(state, 4)

    paths_to_add: list[str] = [str(status_file)]
    if history_file.exists():
        paths_to_add.append(str(history_file))
    if report_dir.exists():
        paths_to_add.append(str(report_dir))

    if not paths_to_add:
        log("git_push: nothing to commit")
        return

    try:
        # Stage only cycle history + reports (not raw run data)
        subprocess.run(["git", "add"] + paths_to_add, cwd=str(REPO), check=True)

        # Check if there's anything staged
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(REPO),
        )
        if result.returncode == 0:
            log("git_push: nothing new to commit")
            return

        # Build an informative commit message for other Claude sessions
        top_atk = state.get("top_attacks", [])
        top_def = state.get("top_defenses", [])
        best_atk_params = state.get("best_attack_params", {})
        best_def_params = state.get("best_defense_params", {})

        # Summarise best validated mAP50 from cycle history file
        best_map = None
        best_run = None
        if history_file.exists():
            h = json.loads(history_file.read_text())
            for run_name, rv in h.get("validation_results", {}).items():
                m = rv.get("mAP50")
                if m and (best_map is None or m > best_map):
                    best_map = m
                    best_run = run_name

        lines = [
            f"auto_cycle: {cycle_id} complete",
            "",
            f"Top attacks : {', '.join(top_atk) or 'none'}",
            f"Top defenses: {', '.join(top_def) or 'none'}",
        ]
        if best_map is not None:
            lines.append(f"Best mAP50  : {best_map:.4f} ({best_run})")
        if best_atk_params:
            for atk, params in best_atk_params.items():
                for k, v in params.items():
                    lines.append(f"  {atk} {k.split('.')[-1]}={v}")
        if best_def_params:
            for dfn, params in best_def_params.items():
                for k, v in params.items():
                    lines.append(f"  {dfn} {k.split('.')[-1]}={v}")
        lines += [
            "",
            "Next cycle will carry forward these params as Phase 3 init values.",
            "See outputs/cycle_history/ for full metrics.",
        ]
        msg = "\n".join(lines)
        subprocess.run(["git", "commit", "-m", msg], cwd=str(REPO), check=True)
        subprocess.run(["git", "push"], cwd=str(REPO), check=True)
        log(f"git_push: pushed results for {cycle_id}")
    except subprocess.CalledProcessError as exc:
        log(f"git_push: failed — {exc} (continuing)")


def carry_forward_params(state: dict) -> None:
    """
    Update ATTACK_PARAM_SPACE and DEFENSE_PARAM_SPACE init values with the
    best params found this cycle, so the next cycle's Phase 3 starts from
    the current optimum rather than factory defaults.

    Also persists the warm-start values to WARM_START_FILE so they survive
    process restarts — load_warm_start() reads this on every startup.
    """
    best_atk = state.get("best_attack_params", {})
    best_def = state.get("best_defense_params", {})

    for attack, params in best_atk.items():
        space = ATTACK_PARAM_SPACE.get(attack, {})
        for key, val in params.items():
            if key in space:
                space[key]["init"] = val
                log(f"  carry-forward: {attack} {key} init → {val}")

    for defense, params in best_def.items():
        space = DEFENSE_PARAM_SPACE.get(defense, {})
        for key, val in params.items():
            if key in space:
                space[key]["init"] = val
                log(f"  carry-forward: {defense} {key} init → {val}")

    # Persist so the next process invocation picks up from here too
    warm = {"attack_params": best_atk, "defense_params": best_def,
            "saved_at": datetime.now().isoformat(),
            "cycle_id": state.get("cycle_id")}
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    WARM_START_FILE.write_text(json.dumps(warm, indent=2))
    log(f"  carry-forward: warm-start saved to {WARM_START_FILE}")


def load_warm_start() -> None:
    """
    Apply persisted warm-start params to ATTACK_PARAM_SPACE / DEFENSE_PARAM_SPACE
    init values.  Called once at process startup so that a restarted process
    continues from the best-found params rather than the hardcoded defaults.
    """
    if not WARM_START_FILE.exists():
        return
    try:
        warm = json.loads(WARM_START_FILE.read_text())
    except Exception:
        return

    for attack, params in warm.get("attack_params", {}).items():
        space = ATTACK_PARAM_SPACE.get(attack, {})
        for key, val in params.items():
            if key in space:
                space[key]["init"] = val

    for defense, params in warm.get("defense_params", {}).items():
        space = DEFENSE_PARAM_SPACE.get(defense, {})
        for key, val in params.items():
            if key in space:
                space[key]["init"] = val

    log(f"Warm-start loaded from {WARM_START_FILE} "
        f"(cycle: {warm.get('cycle_id', 'unknown')})")


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_status() -> None:
    if not STATE_FILE.exists():
        print("No cycle state found. Run without --status to start one.")
        return
    state = json.loads(STATE_FILE.read_text())
    print(json.dumps(state, indent=2))


def cmd_reset() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print("Cycle state deleted. Next run will start fresh.")
    else:
        print("No cycle state to reset.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--status", action="store_true",
                        help="Print current cycle state and exit")
    parser.add_argument("--reset", action="store_true",
                        help="Delete cycle state and exit (next run starts fresh)")
    parser.add_argument("--loop", action="store_true",
                        help="Run continuously: after each cycle completes, carry "
                             "forward best params and start the next cycle immediately")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel workers for sweep phases (default: 1). "
                             "Use >1 only if you have multiple GPUs or CPU-only runs.")
    args = parser.parse_args()

    if args.status:
        cmd_status()
        return
    if args.reset:
        cmd_reset()
        return

    OUTPUTS.mkdir(parents=True, exist_ok=True)

    # Apply warm-start params from previous run (survives process restarts)
    load_warm_start()

    # Exclusive lock — prevents concurrent execution (cron restart safety)
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Another cycle instance is already running. Exiting.")
        sys.exit(0)

    try:
        cycle_num = 0
        while True:
            cycle_num += 1
            state = load_state()
            save_state(state)

            log(f"Cycle #{cycle_num}: {state['cycle_id']}  phase={state['current_phase']}"
                + ("  [loop mode]" if args.loop else ""))

            if state.get("complete"):
                if not args.loop:
                    log("Cycle already complete. Use --reset to start a new one.")
                    log(f"Reports: {state['report_root']}")
                    break
                # In loop mode a complete state means we just re-entered —
                # archive it and start the next cycle.
                log("Cycle complete — archiving and starting next cycle.")
                save_cycle_history(state)
                git_push_results(state)
                carry_forward_params(state)
                STATE_FILE.unlink()
                git_pull()  # pick up any changes before the next cycle
                continue

            if not state["phase1_complete"]:
                if not phase1(state):
                    break
                save_state(state)
                generate_report(state)
                git_commit_phase(state, 1)
                wait_if_paused(1)

            if not state["phase2_complete"]:
                if not phase2(state):
                    break
                save_state(state)
                generate_report(state)
                git_commit_phase(state, 2)
                wait_if_paused(2)

            if not state["phase3_complete"]:
                if not phase3(state):
                    break
                save_state(state)
                git_commit_phase(state, 3)
                wait_if_paused(3)

            if not state["phase4_complete"]:
                if not phase4(state):
                    break
                save_state(state)
                generate_report(state)

            log(f"All phases complete. Reports: {state['report_root']}")

            if not args.loop:
                break

            # Loop mode: archive this cycle and roll straight into the next
            save_cycle_history(state)
            git_push_results(state)
            carry_forward_params(state)
            STATE_FILE.unlink()
            log("─" * 60)
            log(f"Starting cycle #{cycle_num + 1} with carried-forward params...")
            git_pull()  # pick up any changes pushed by other sessions

    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
