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
import re
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
    "blur", "deepfool", "dispersion_reduction", "eot_pgd", "fgsm", "pgd", "square",
    # jpeg_attack temporarily removed — no-op behavior under current defaults
]
ALL_DEFENSES: list[str] = [
    "bit_depth", "c_dog", "jpeg_preprocess",
    # c_dog_ensemble temporarily removed — underperforming single c_dog
    "median_preprocess",
    # random_resize removed — inherent mAP50 cost (−0.25) exceeds any attack-recovery benefit
]

TOP_N_ATTACKS = 3
TOP_N_DEFENSES = 3   # bumped from 2 — catalogue now has 6 defenses
RANKING_SMOKE_MAX_IMAGES = 32

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
        "attack.params.steps":   {"init": 50,    "min": 10,    "max": 200,  "scale": "int",  "step": 30},
    },
    "dispersion_reduction": {
        "attack.params.epsilon": {"init": 0.05,  "min": 0.01,  "max": 0.15, "scale": "log", "factor": 2.0},
        "attack.params.steps":   {"init": 50,    "min": 20,    "max": 100,  "scale": "int",  "step": 20},
    },
    "eot_pgd": {
        "attack.params.epsilon":    {"init": 0.016, "min": 0.002, "max": 0.3,  "scale": "log", "factor": 2.0},
        "attack.params.alpha":      {"init": 0.0015, "min": 0.0005, "max": 0.02, "scale": "log", "factor": 2.0},
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

TUNE_MAX_IMAGES = 16
CONSISTENCY_CHECK_MAX_IMAGES = 50

TUNE_MAX_IMAGES_BY_ATTACK: dict[str, int] = {
    "square":               8,
    "eot_pgd":             12,
    "dispersion_reduction": 12,
}

# Attacks too slow for NUC Phase 4 (500-image full validation).
# Skip these in Phase 4; Mac's standalone sweep handles their validation.
SLOW_ATTACKS: set[str] = {"square", "eot_pgd", "dispersion_reduction"}  # ~126s/img, ~48s/img, ~60s/img on NUC CPU

# Phase 1 characterize image cap for slow attacks (default: RANKING_SMOKE_MAX_IMAGES).
# Limits characterization smoke runs without affecting Phase 2/3 if not in top attacks.
CHARACTERIZE_MAX_IMAGES_BY_ATTACK: dict[str, int] = {
    "square":               8,
    "eot_pgd":             12,
    "dispersion_reduction": 12,
}

# Coordinate descent settings
TUNE_MAX_ITERS = 15          # max passes over all parameters (global default)
TUNE_TOLERANCE_REL = 0.05    # minimum *relative* improvement to count as a gain
                              # relative keeps weak attacks from accepting noise
                              # and strong attacks from missing real gains
TUNE_TOLERANCE_ABS = 0.005   # absolute floor: when current_score ≈ 0 the relative
                              # threshold collapses to 0, disabling early exit

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
    log_path = LOG_DIR / "auto_cycle.log"

    # Avoid duplicate lines when stdout is already redirected to auto_cycle.log.
    try:
        stdout_stat = os.fstat(sys.stdout.fileno())
        file_stat = os.stat(log_path) if log_path.exists() else None
        if file_stat and stdout_stat.st_dev == file_stat.st_dev and stdout_stat.st_ino == file_stat.st_ino:
            return
    except Exception:
        # If fd/stat probing fails, fall back to explicit file append.
        pass

    with open(log_path, "a", encoding="utf-8") as fh:
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
        "checkpoint_fingerprint": None,
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
    max_images: int | None = None,
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
    if max_images is not None:
        cmd += ["--max-images", str(max_images)]
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
    timeout_seconds: int | None = None,
    max_images_override: int | None = None,
) -> bool:
    """Call run_unified.py for one experiment. Skip if metrics.json already exists."""
    run_dir = Path(runs_root) / run_name
    if (run_dir / "metrics.json").exists():
        log(f"  skip (exists): {run_name}")
        return True

    # "tune" preset: more images than smoke for reliable signal, less than full
    max_images = (
        str(max_images_override)
        if max_images_override is not None
        else {"smoke": "8", "tune": str(TUNE_MAX_IMAGES), "full": "0"}.get(preset, "0")
    )
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
    try:
        result = subprocess.run(cmd, cwd=str(REPO), env=_env(), timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        log(f"  timeout: {run_name} exceeded {timeout_seconds}s")
        return False
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
    # Run fast attacks together, then slow attacks individually with lower image caps.
    fast_attacks = [a for a in ALL_ATTACKS if a not in SLOW_ATTACKS]
    slow_attacks = [a for a in ALL_ATTACKS if a in SLOW_ATTACKS]
    ok = run_sweep(
        attacks=fast_attacks,
        defenses=["none"],
        runs_root=state["runs_root"],
        report_root=state["report_root"],
        sweep_phases="1,2",
        max_images=RANKING_SMOKE_MAX_IMAGES,
    )
    for attack in slow_attacks:
        cap = CHARACTERIZE_MAX_IMAGES_BY_ATTACK.get(attack, RANKING_SMOKE_MAX_IMAGES)
        log(f"  Phase 1: slow attack {attack} capped at {cap} images")
        ok_a = run_sweep(
            attacks=[attack],
            defenses=["none"],
            runs_root=state["runs_root"],
            report_root=state["report_root"],
            sweep_phases="1,2",
            max_images=cap,
        )
        ok = ok and ok_a
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
        max_images=RANKING_SMOKE_MAX_IMAGES,
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

_FINGERPRINT_UNSAFE = re.compile(r"[^a-zA-Z0-9._-]")


def _param_fingerprint(prefix: str, params: dict) -> str:
    """Deterministic, filesystem-safe run name derived from param values."""
    parts = [prefix]
    for k in sorted(params):
        short = k.split(".")[-1]
        v = params[k]
        if isinstance(v, float):
            parts.append(f"{short}{v:.6g}")
        else:
            parts.append(f"{short}{v}")
    raw = "__".join(parts)
    return _FINGERPRINT_UNSAFE.sub("_", raw)[:120]


def _initial_step(spec: dict) -> float:
    """Return the original step/factor from a param spec."""
    if spec["scale"] == "log":
        return float(spec["factor"])
    return float(spec["step"])


def _three_point_scan(
    param_space: dict,
    warm_keys: set[str],
    score_fn,
    run_prefix: str,
) -> dict:
    """For params absent from warm-start, probe min/mid/max and pick the best init."""
    overrides: dict = {}
    scan_counter = [0]

    for key, spec in param_space.items():
        if key in warm_keys:
            continue
        lo, hi = spec["min"], spec["max"]
        mid = (lo + hi) / 2.0
        if spec["scale"] in ("int", "odd_int"):
            mid = int(round(mid))
            if spec["scale"] == "odd_int" and mid % 2 == 0:
                mid += 1

        best_val, best_score = spec["init"], -float("inf")
        for probe_val in [lo, mid, hi]:
            scan_counter[0] += 1
            trial = {k: spec2["init"] for k, spec2 in param_space.items()}
            trial[key] = probe_val
            name = _param_fingerprint(f"{run_prefix}_scan", trial)
            s = score_fn(trial, name)
            if s > best_score:
                best_score = s
                best_val = probe_val
        overrides[key] = best_val
        log(f"  3-point scan: {key.split('.')[-1]} → {best_val}  (score={best_score:.4f})")
    return overrides


def _clamp(value, spec: dict):
    """Return value clamped to [spec.min, spec.max], cast to the right type."""
    lo, hi = spec["min"], spec["max"]
    if spec["scale"] in ("int", "odd_int"):
        return int(max(lo, min(hi, int(value))))
    return float(max(lo, min(hi, float(value))))


def _candidates(spec: dict, current, step_override: float | None = None) -> list:
    """Generate up to two candidate values to probe from the current position.

    When *step_override* is provided it replaces the spec's step/factor for
    adaptive step-size support.
    """
    scale = spec["scale"]
    lo, hi = spec["min"], spec["max"]

    if scale == "log":
        f = step_override if step_override is not None else spec["factor"]
        cands = [float(current) * f, float(current) / f]
        cands = [float(max(lo, min(hi, c))) for c in cands]
        cands = [c for c in cands if abs(c - current) / (abs(current) + 1e-12) > 0.05]
    elif scale == "linear_float":
        step = step_override if step_override is not None else spec["step"]
        cands = [float(current) + step, float(current) - step]
        cands = [float(max(lo, min(hi, c))) for c in cands]
        cands = [c for c in cands if abs(c - current) > 1e-9]
    elif scale == "odd_int":
        step = int(step_override) if step_override is not None else spec["step"]
        up, down = int(current) + step, int(current) - step
        if up   % 2 == 0: up   += 1
        if down % 2 == 0: down -= 1
        cands = [c for c in [up, down] if lo <= c <= hi and c != int(current)]
    elif scale == "int":
        step = int(step_override) if step_override is not None else spec["step"]
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
               runs_root=runs_root, overrides=params, preset="tune",
               max_images_override=TUNE_MAX_IMAGES_BY_ATTACK.get(attack))
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    # suppression: higher = attack was more effective (composite score closer to 0)
    return 1.0 - _composite_score(m, baseline_conf, baseline_det)


def _run_and_score_defense(attack, defense, params, run_name, runs_root,
                            baseline_conf, baseline_det, attack_composite):
    run_single(attack=attack, defense=defense, run_name=run_name,
               runs_root=runs_root, overrides=params, preset="tune",
               max_images_override=TUNE_MAX_IMAGES_BY_ATTACK.get(attack))
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    suppression = 1.0 - attack_composite
    if suppression < 1e-4:
        return 0.0  # attack had negligible composite effect — recovery undefined
    def_composite = _composite_score(m, baseline_conf, baseline_det)
    return (def_composite - attack_composite) / suppression


def _run_and_score_defense_multi(
    attacks: list[str],
    defense: str,
    params: dict,
    run_name_prefix: str,
    runs_root: str,
    baseline_conf: float,
    baseline_det: int,
    attack_composites: list[float],
) -> float:
    """Score a defense against multiple attacks, returning the average recovery."""
    scores = []
    for attack, atk_comp in zip(attacks, attack_composites):
        name = f"{run_name_prefix}_vs_{attack}"
        s = _run_and_score_defense(attack, defense, params, name,
                                   runs_root, baseline_conf, baseline_det, atk_comp)
        scores.append(s)
    return sum(scores) / len(scores) if scores else -1.0


def _coordinate_descent(label, param_space, score_fn, run_prefix,
                         existing_history=None, max_iters: int | None = None):
    """Coordinate descent with adaptive steps, momentum, diagonal probes,
    param-fingerprint caching, and diminishing-returns early termination.

    Returns (best_params, best_score, history).
    """
    _max_iters = max_iters if max_iters is not None else TUNE_MAX_ITERS
    history = list(existing_history or [])
    counter = [len(history)]
    DIMINISHING_WINDOW = 3

    def _score(params, tag=""):
        """Score with param-fingerprint naming for automatic caching."""
        counter[0] += 1
        name = _param_fingerprint(run_prefix, params)
        return score_fn(params, name)

    current = {k: spec["init"] for k, spec in param_space.items()}
    current_score = _score(current)
    log(f"  [{label}] init  score={current_score:.4f}  "
        f"params={_fmt(current)}")
    history.append({"iter": 0, "param": "init", "value": None,
                    "score": current_score, "delta": 0.0, "improved": True})

    current_steps: dict[str, float] = {
        k: _initial_step(spec) for k, spec in param_space.items()
    }
    momentum: dict[str, int] = {k: 0 for k in param_space}
    pass_gains: list[float] = []

    for iteration in range(1, _max_iters + 1):
        score_at_pass_start = current_score
        pass_improved = False
        iter_best_moves: list[tuple[str, float, object]] = []

        for param_key, spec in param_space.items():
            best_candidate = None
            best_candidate_score = current_score

            raw_cands = _candidates(spec, current[param_key],
                                    step_override=current_steps.get(param_key))
            if momentum.get(param_key, 0) != 0:
                mom_dir = momentum[param_key]
                ordered = sorted(
                    raw_cands,
                    key=lambda c, _cur=current[param_key], _d=mom_dir: (
                        -_d * (c - _cur)
                    ),
                )
            else:
                ordered = raw_cands

            momentum_hit = False
            for ci, candidate in enumerate(ordered):
                test_params = {**current, param_key: candidate}
                s = _score(test_params)
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
                    if ci == 0 and momentum.get(param_key, 0) != 0:
                        momentum_hit = True

                if momentum_hit and ci == 0 and best_candidate is not None:
                    break

            if (best_candidate is not None and
                    best_candidate_score - current_score
                    > abs(current_score) * TUNE_TOLERANCE_REL):
                direction = 1 if best_candidate > current[param_key] else -1
                log(f"  [{label}] ✓ commit  {param_key.split('.')[-1]}  "
                    f"{current[param_key]} → {best_candidate}  "
                    f"({current_score:.4f} → {best_candidate_score:.4f})")
                iter_best_moves.append((param_key, best_candidate_score - current_score, best_candidate))
                current = {**current, param_key: best_candidate}
                current_score = best_candidate_score
                history[-1]["improved"] = True
                pass_improved = True
                momentum[param_key] = direction
                min_step = _initial_step(spec) / 2.0
                current_steps[param_key] = max(min_step, current_steps[param_key] / 2.0)
            else:
                momentum[param_key] = 0
                current_steps[param_key] = _initial_step(param_space[param_key])

        if len(param_space) >= 2 and len(iter_best_moves) >= 1:
            diag_params = dict(current)
            moves = sorted(iter_best_moves, key=lambda t: -t[1])
            keys_to_move = [m[0] for m in moves[:2]]
            for pk in keys_to_move:
                spec = param_space[pk]
                step = current_steps[pk]
                d = momentum.get(pk, 1)
                if spec["scale"] == "log":
                    nudge = current[pk] * (step if d > 0 else 1.0 / step)
                elif spec["scale"] in ("int", "odd_int"):
                    nudge = int(current[pk]) + int(step) * d
                    if spec["scale"] == "odd_int" and nudge % 2 == 0:
                        nudge += d
                else:
                    nudge = float(current[pk]) + step * d
                diag_params[pk] = _clamp(nudge, spec)

            if diag_params != current:
                s = _score(diag_params)
                log(f"  [{label}] iter={iteration}  diagonal  "
                    f"score={s:.4f}  delta={s - current_score:+.4f}")
                history.append({
                    "iter": iteration, "param": "diagonal",
                    "value": {k: diag_params[k] for k in keys_to_move},
                    "score": round(s, 6),
                    "delta": round(s - current_score, 6),
                    "improved": False,
                })
                if (s - current_score > abs(current_score) * TUNE_TOLERANCE_REL):
                    log(f"  [{label}] ✓ commit diagonal  "
                        f"({current_score:.4f} → {s:.4f})")
                    current = dict(diag_params)
                    current_score = s
                    history[-1]["improved"] = True
                    pass_improved = True

        pass_gain = current_score - score_at_pass_start
        pass_gains.append(pass_gain)

        if not pass_improved:
            log(f"  [{label}] converged after {iteration} pass(es)  "
                f"best={current_score:.4f}  {_fmt(current)}")
            break

        if len(pass_gains) >= DIMINISHING_WINDOW:
            recent = pass_gains[-DIMINISHING_WINDOW:]
            threshold = max(2.0 * TUNE_TOLERANCE_REL * abs(current_score), TUNE_TOLERANCE_ABS)
            if sum(recent) < threshold:
                log(f"  [{label}] diminishing returns after {iteration} pass(es)  "
                    f"cumulative_gain={sum(recent):.6f}  "
                    f"best={current_score:.4f}  {_fmt(current)}")
                break

    return dict(current), current_score, history


def _fmt(params: dict) -> str:
    return "  ".join(f"{k.split('.')[-1]}={v}" for k, v in params.items())


def pre_tune_consistency_check(state: dict) -> list[str]:
    """Re-rank top defenses using a larger sample before expensive tuning."""
    attacks = list(state.get("top_attacks") or [])
    defenses = list(state.get("top_defenses") or [])
    if not attacks or not defenses:
        return defenses

    runs_root = state["runs_root"]
    baseline_m = read_metrics(Path(runs_root) / "baseline_none")
    if not baseline_m:
        return defenses
    baseline_conf = get_avg_conf(baseline_m) or 1.0
    baseline_det = get_total_detections(baseline_m)
    if baseline_det <= 0:
        return defenses

    anchor_attack = attacks[0]
    atk_run = f"consistency_atk_{anchor_attack}"
    if not run_single(
        attack=anchor_attack,
        defense="none",
        run_name=atk_run,
        runs_root=runs_root,
        preset="smoke",
        max_images_override=CONSISTENCY_CHECK_MAX_IMAGES,
    ):
        return defenses
    atk_metrics = read_metrics(Path(runs_root) / atk_run)
    if not atk_metrics:
        return defenses
    atk_health = _composite_score(atk_metrics, baseline_conf, baseline_det)
    suppression = 1.0 - atk_health
    if suppression <= 1e-4:
        return defenses

    ranked: list[tuple[float, str]] = []
    for defense in defenses:
        run_name = f"consistency_{anchor_attack}_{defense}"
        ok = run_single(
            attack=anchor_attack,
            defense=defense,
            run_name=run_name,
            runs_root=runs_root,
            preset="smoke",
            max_images_override=CONSISTENCY_CHECK_MAX_IMAGES,
        )
        if not ok:
            continue
        m = read_metrics(Path(runs_root) / run_name)
        if not m:
            continue
        def_health = _composite_score(m, baseline_conf, baseline_det)
        recovery = (def_health - atk_health) / suppression
        ranked.append((recovery, defense))

    if not ranked:
        return defenses
    ranked.sort(reverse=True)
    reranked = [d for _, d in ranked]
    for d in defenses:
        if d not in reranked:
            reranked.append(d)
    log(f"  Phase 3 consistency gate reranked defenses: {reranked[:len(defenses)]}")
    return reranked[: len(defenses)]


# ── Phase 3 — Tune ────────────────────────────────────────────────────────────

def phase3(state: dict) -> bool:
    log(f"=== Phase 3: Adaptive Tune "
        f"({state['top_attacks']} × {state['top_defenses']}, "
        f"{TUNE_MAX_IMAGES} imgs) ===")
    state["top_defenses"] = pre_tune_consistency_check(state)
    runs_root = state["runs_root"]
    tune_history = state.setdefault("tune_history", {})

    baseline_m = read_metrics(Path(runs_root) / "baseline_none")
    baseline_conf = (get_avg_conf(baseline_m) or 1.0) if baseline_m else 1.0
    baseline_det = get_total_detections(baseline_m) if baseline_m else 0

    warm = {}
    if WARM_START_FILE.exists():
        try:
            warm = json.loads(WARM_START_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    # ── Step 1: Tune each top attack (no defense) ─────────────────────────────
    for attack in state["top_attacks"]:
        space = ATTACK_PARAM_SPACE.get(attack)
        if not space:
            log(f"  No param space for {attack}, skipping")
            state.setdefault("best_attack_params", {})[attack] = {}
            continue

        existing = tune_history.get(f"attack_{attack}", [])

        warm_atk = set((warm.get("attack_params") or {}).get(attack, {}).keys())
        def _atk_score(params, name, _a=attack, _bc=baseline_conf, _bd=baseline_det):
            return _run_and_score_attack(_a, params, name, runs_root, _bc, _bd)

        scan_overrides = _three_point_scan(space, warm_atk, _atk_score, f"tune_atk_{attack}")
        if scan_overrides:
            for k, v in scan_overrides.items():
                space[k]["init"] = v

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

    # ── Step 2: Baseline for defense tuning using best-tuned attacks ──────────
    anchor_attacks = state["top_attacks"][:2]
    attack_composites: list[float] = []
    for atk in anchor_attacks:
        best_atk_params = state.get("best_attack_params", {}).get(atk, {})
        tuned_atk_run = f"tune_atk_{atk}_best"
        run_single(attack=atk, defense="none",
                   run_name=tuned_atk_run, runs_root=runs_root,
                   overrides=best_atk_params, preset="tune",
                   max_images_override=TUNE_MAX_IMAGES_BY_ATTACK.get(atk))
        tuned_m = read_metrics(Path(runs_root) / tuned_atk_run)
        ac = _composite_score(tuned_m, baseline_conf, baseline_det) if tuned_m else 1.0
        attack_composites.append(ac)
        log(f"  Tuned {atk} composite={ac:.4f}  "
            f"(suppression={1.0 - ac:.4f} vs baseline)")

    # ── Step 3: Tune each top defense against anchor attacks ──────────────────
    for defense in state["top_defenses"]:
        space = DEFENSE_PARAM_SPACE.get(defense)
        if not space:
            log(f"  No param space for {defense}, skipping")
            state.setdefault("best_defense_params", {})[defense] = {}
            continue

        existing = tune_history.get(f"defense_{defense}", [])

        def _def_score(params, name, _anchors=list(anchor_attacks), _d=defense,
                       _bc=baseline_conf, _bd=baseline_det, _acs=list(attack_composites)):
            return _run_and_score_defense_multi(
                _anchors, _d, params, name, runs_root, _bc, _bd, _acs)

        warm_def = set((warm.get("defense_params") or {}).get(defense, {}).keys())
        scan_overrides = _three_point_scan(space, warm_def, _def_score, f"tune_def_{defense}")
        if scan_overrides:
            for k, v in scan_overrides.items():
                space[k]["init"] = v

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
    delegated_runs: list[str] = []
    failed_runs: list[str] = []

    def _timeout_for_attack(attack_name: str) -> int:
        if attack_name in SLOW_ATTACKS:
            return 4 * 60 * 60
        return 2 * 60 * 60

    # Baseline
    if not run_single(
        attack="none",
        defense="none",
        run_name="validate_baseline",
        runs_root=runs_root,
        preset="full",
        validation=True,
        timeout_seconds=_timeout_for_attack("none"),
    ):
        failed_runs.append("validate_baseline")

    # Best attack configs (no defense) — skip slow attacks; Mac handles those
    for attack in state["top_attacks"]:
        if attack in SLOW_ATTACKS:
            log(f"  Skipping Phase 4 for {attack} (slow attack — Mac handles validation)")
            delegated_runs.append(f"validate_atk_{attack}")
            continue
        if not run_single(
            attack=attack, defense="none",
            run_name=f"validate_atk_{attack}",
            runs_root=runs_root,
            overrides=best_atk.get(attack),
            preset="full", validation=True,
            timeout_seconds=_timeout_for_attack(attack),
        ):
            failed_runs.append(f"validate_atk_{attack}")

    # Best attack × defense combos — skip slow attacks on NUC
    for attack in state["top_attacks"]:
        if attack in SLOW_ATTACKS:
            for defense in state["top_defenses"]:
                delegated_runs.append(f"validate_{attack}_{defense}")
            continue
        for defense in state["top_defenses"]:
            merged = {**(best_atk.get(attack) or {}), **(best_def.get(defense) or {})}
            if not run_single(
                attack=attack, defense=defense,
                run_name=f"validate_{attack}_{defense}",
                runs_root=runs_root,
                overrides=merged or None,
                preset="full", validation=True,
                timeout_seconds=_timeout_for_attack(attack),
            ):
                failed_runs.append(f"validate_{attack}_{defense}")

    state["phase4_complete"] = True
    state["complete"] = True
    state["finished_at"] = datetime.now().isoformat()
    state["delegated_phase4_runs"] = sorted(set(delegated_runs))
    state["failed_phase4_runs"] = sorted(set(failed_runs))
    if failed_runs:
        log("[warn] Phase 4 had failed or timed-out runs: " + ", ".join(sorted(set(failed_runs))))
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
        "delegated_phase4_runs": state.get("delegated_phase4_runs", []),
    }
    delegated_expected = set(state.get("delegated_phase4_runs", []))
    delegated_present = delegated_expected.intersection(validation_results.keys())
    delegated_missing = sorted(delegated_expected - delegated_present)
    if delegated_expected and delegated_missing:
        log(
            "[warn] delegated Phase 4 runs missing from cycle history: "
            + ", ".join(delegated_missing)
        )
    if delegated_expected:
        summary["delegated_phase4_status"] = {
            "expected": sorted(delegated_expected),
            "present": sorted(delegated_present),
            "missing": delegated_missing,
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
        def _is_none_like(value: object) -> bool:
            return value in (None, "", "none")

        def _to_float(value: object) -> float | None:
            try:
                parsed = float(value)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return None
            return parsed

        baseline_entry: dict | None = None
        attack_only: dict[str, dict] = {}
        defended: dict[str, dict[str, dict]] = {}

        for _, payload in validation_results.items():
            atk = payload.get("attack")
            dfn = payload.get("defense")
            atk_real = not _is_none_like(atk)
            dfn_real = not _is_none_like(dfn)
            if not atk_real and not dfn_real:
                baseline_entry = payload
            elif atk_real and not dfn_real:
                attack_only[str(atk)] = payload
            elif atk_real and dfn_real:
                defended.setdefault(str(atk), {})[str(dfn)] = payload

        if not attack_only:
            log("_write_training_signal: no attack-only validation rows — skipping")
            return

        # Prefer full-run mAP50 ranking when available; this tracks actual robustness
        # signal better than smoke/composite proxy metrics.
        attacks_with_map = {
            atk: row for atk, row in attack_only.items() if _to_float(row.get("mAP50")) is not None
        }
        if attacks_with_map:
            baseline_map50 = _to_float((baseline_entry or {}).get("mAP50"))
            attack_rows: list[tuple[float, str]] = []
            defense_recovery: dict[str, dict[str, float]] = {}

            for atk, atk_row in attacks_with_map.items():
                atk_map50 = _to_float(atk_row.get("mAP50"))
                if atk_map50 is None:
                    continue
                attack_rows.append((atk_map50, atk))

                def_scores = defended.get(atk, {})
                for dfn, drow in def_scores.items():
                    def_map50 = _to_float(drow.get("mAP50"))
                    if def_map50 is None:
                        continue
                    if baseline_map50 is not None and baseline_map50 > atk_map50:
                        recovery = (def_map50 - atk_map50) / (baseline_map50 - atk_map50)
                    else:
                        recovery = 0.0
                    defense_recovery.setdefault(atk, {})[dfn] = recovery

            if not attack_rows:
                log("_write_training_signal: no attack mAP50 values — skipping")
                return

            attack_rows.sort()  # lowest mAP50 first
            worst_attack = attack_rows[0][1]
            weakest_defense = "none"
            weakest_recovery = 0.0
            if defense_recovery.get(worst_attack):
                weakest_defense = min(defense_recovery[worst_attack], key=lambda d: defense_recovery[worst_attack][d])
                weakest_recovery = defense_recovery[worst_attack][weakest_defense]

            avg_recovery: dict[str, float] = {}
            for atk in attacks_with_map:
                values = list(defense_recovery.get(atk, {}).values())
                avg_recovery[atk] = (sum(values) / len(values)) if values else 0.0

            signal = {
                "cycle_id": state["cycle_id"],
                "generated_at": state.get("finished_at"),
                "ranking_source": "phase4_map50",
                "worst_attack": worst_attack,
                "worst_attack_params": state.get("best_attack_params", {}).get(worst_attack, {}),
                "weakest_defense": weakest_defense,
                "weakest_defense_recovery": round(weakest_recovery, 4),
                "all_attack_avg_recovery": {atk: round(score, 4) for atk, score in avg_recovery.items()},
            }
            sig_path = OUTPUTS / "cycle_training_signal.json"
            sig_path.write_text(json.dumps(signal, indent=2))
            log(
                f"Training signal (mAP50): {worst_attack} bypassed {weakest_defense} "
                f"(recovery={weakest_recovery:.3f}) → {sig_path}"
            )
            return

        baseline_dets = _to_float((baseline_entry or {}).get("detections"))
        if baseline_dets is None or baseline_dets == 0:
            log("_write_training_signal: no baseline detections — skipping")
            return

        attack_dets_map: dict[str, float] = {}
        defense_recovery: dict[str, dict[str, float]] = {}

        for atk, row in attack_only.items():
            dets = _to_float(row.get("detections"))
            if dets is not None:
                attack_dets_map[atk] = dets

        for atk, def_map in defended.items():
            atk_dets = attack_dets_map.get(atk)
            if atk_dets is None:
                continue
            for dfn, drow in def_map.items():
                def_dets = _to_float(drow.get("detections"))
                if def_dets is None:
                    continue
                drop = baseline_dets - atk_dets
                if drop > 0:
                    recovery = (def_dets - atk_dets) / drop
                    defense_recovery.setdefault(atk, {})[dfn] = recovery

        if not defense_recovery:
            log("_write_training_signal: no defense recovery data — skipping")
            return

        atk_avg: list[tuple[float, str]] = []
        for atk, rmap in defense_recovery.items():
            avg = sum(rmap.values()) / len(rmap) if rmap else 1.0
            atk_avg.append((avg, atk))
        atk_avg.sort()
        worst_attack = atk_avg[0][1]
        rmap = defense_recovery[worst_attack]
        weakest_defense = min(rmap, key=lambda d: rmap[d])
        weakest_recovery = rmap[weakest_defense]

        signal = {
            "cycle_id": state["cycle_id"],
            "generated_at": state.get("finished_at"),
            "ranking_source": "phase4_detection_recovery",
            "worst_attack": worst_attack,
            "worst_attack_params": state.get("best_attack_params", {}).get(worst_attack, {}),
            "weakest_defense": weakest_defense,
            "weakest_defense_recovery": round(weakest_recovery, 4),
            "all_attack_avg_recovery": {a: round(s, 4) for s, a in atk_avg},
        }
        sig_path = OUTPUTS / "cycle_training_signal.json"
        sig_path.write_text(json.dumps(signal, indent=2))
        log(
            f"Training signal (detection): {worst_attack} bypassed {weakest_defense} "
            f"(recovery={weakest_recovery:.3f}) → {sig_path}"
        )
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


def _current_checkpoint_fingerprint() -> str | None:
    """Stable fingerprint for the active DPC-UNet checkpoint file."""
    ckpt_path = _env().get("DPC_UNET_CHECKPOINT_PATH")
    if not ckpt_path:
        return None
    path = Path(ckpt_path)
    if not path.exists():
        return None
    stat = path.stat()
    return f"{path.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"


def maybe_pause_for_checkpoint_update(state: dict, *, next_phase: int) -> None:
    """Pause between phases if the checkpoint changed during a cycle."""
    current_fp = _current_checkpoint_fingerprint()
    if not current_fp:
        return
    prior_fp = state.get("checkpoint_fingerprint")
    if not prior_fp:
        state["checkpoint_fingerprint"] = current_fp
        save_state(state)
        return
    if prior_fp == current_fp:
        return

    log(
        "Checkpoint update detected mid-cycle. "
        f"Pausing before phase {next_phase} to avoid mixing checkpoints in one cycle."
    )
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    PAUSE_FILE.touch(exist_ok=True)
    wait_if_paused(next_phase - 1)
    state["checkpoint_fingerprint"] = _current_checkpoint_fingerprint() or current_fp
    save_state(state)


def git_pull() -> None:
    """Pull latest changes from remote. Called at the start of each new cycle
    so new plugins, param-space tweaks, and bug fixes are picked up automatically.
    Uses merge (not fast-forward-only) so NUC's local cycle commits don't block pulls."""
    try:
        result = subprocess.run(
            ["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        if result.returncode == 0:
            msg = result.stdout.strip() or "already up to date"
            log(f"git_pull: {msg}")
        else:
            log(f"git_pull: failed — {result.stderr.strip()}")
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
    raw_best_atk = state.get("best_attack_params", {})
    raw_best_def = state.get("best_defense_params", {})
    best_atk = {k: v for k, v in raw_best_atk.items() if k in ATTACK_PARAM_SPACE}
    best_def = {k: v for k, v in raw_best_def.items() if k in DEFENSE_PARAM_SPACE}

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
        if attack not in ATTACK_PARAM_SPACE:
            continue
        space = ATTACK_PARAM_SPACE.get(attack, {})
        for key, val in params.items():
            if key in space:
                space[key]["init"] = val

    for defense, params in warm.get("defense_params", {}).items():
        if defense not in DEFENSE_PARAM_SPACE:
            continue
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
                maybe_pause_for_checkpoint_update(state, next_phase=1)
                if not phase1(state):
                    break
                save_state(state)
                generate_report(state)
                git_commit_phase(state, 1)
                wait_if_paused(1)

            if not state["phase2_complete"]:
                maybe_pause_for_checkpoint_update(state, next_phase=2)
                if not phase2(state):
                    break
                save_state(state)
                generate_report(state)
                git_commit_phase(state, 2)
                wait_if_paused(2)

            if not state["phase3_complete"]:
                maybe_pause_for_checkpoint_update(state, next_phase=3)
                if not phase3(state):
                    break
                save_state(state)
                git_commit_phase(state, 3)
                wait_if_paused(3)

            if not state["phase4_complete"]:
                maybe_pause_for_checkpoint_update(state, next_phase=4)
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
