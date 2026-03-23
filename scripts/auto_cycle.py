#!/usr/bin/env python3
"""scripts/auto_cycle.py

Automated test-and-tune cycle for YOLO-Bad-Triangle.

Four phases run sequentially. State is persisted so the cycle is fully
resumable — re-invoke the script at any point to continue from where it
left off.

  Phase 1  Characterize   All attacks vs no defense (smoke, 8 images).
                           Ranks attacks by avg-confidence suppression.

  Phase 2  Matrix         Top-N attacks × all defenses (full, 500 images).
                           Ranks defenses by avg-confidence recovery.

  Phase 3  Tune           Adaptive coordinate descent for top attacks × top
                           defenses (32 images).  After each run, assesses the
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
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO = Path(__file__).parent.parent
OUTPUTS = REPO / "outputs"
STATE_FILE = OUTPUTS / "cycle_state.json"
LOCK_FILE = OUTPUTS / ".cycle.lock"
HISTORY_DIR = OUTPUTS / "cycle_history"
LOG_DIR = REPO / "logs"
PYTHON = REPO / ".venv" / "bin" / "python"

# ── Attack / defense catalogues ───────────────────────────────────────────────

ALL_ATTACKS: list[str] = [
    "blur", "deepfool", "eot_pgd", "fgsm",
    "fgsm_center_mask", "fgsm_edge_mask", "gaussian_blur", "pgd",
]
ALL_DEFENSES: list[str] = [
    "c_dog", "c_dog_ensemble", "confidence_filter", "median_preprocess",
]

TOP_N_ATTACKS = 3
TOP_N_DEFENSES = 2

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
    "fgsm_center_mask": {
        "attack.params.epsilon":         {"init": 0.008, "min": 0.001, "max": 0.15, "scale": "log",          "factor": 2.0},
        "attack.params.radius_fraction": {"init": 0.35,  "min": 0.1,   "max": 0.7,  "scale": "linear_float", "step": 0.1},
    },
    "fgsm_edge_mask": {
        "attack.params.epsilon":        {"init": 0.008, "min": 0.001, "max": 0.15, "scale": "log", "factor": 2.0},
        "attack.params.edge_threshold": {"init": 40,    "min": 10,    "max": 100,  "scale": "int",  "step": 15},
    },
    "blur": {
        "attack.params.kernel_size": {"init": 25, "min": 3, "max": 51, "scale": "odd_int", "step": 4},
    },
    "gaussian_blur": {
        "attack.params.kernel_size": {"init": 25, "min": 3, "max": 51, "scale": "odd_int", "step": 4},
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
    "confidence_filter": {
        "defense.params.threshold": {"init": 0.5, "min": 0.1, "max": 0.9, "scale": "linear_float", "step": 0.1},
    },
}

# Images used during tuning — more than smoke (8) for reliable signal,
# less than full (500) to keep each evaluation fast.
TUNE_MAX_IMAGES = 32

# Coordinate descent settings
TUNE_MAX_ITERS = 15       # max passes over all parameters
TUNE_TOLERANCE = 0.002    # minimum improvement to count as a gain

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


def get_map50(m: dict) -> float | None:
    return m.get("validation", {}).get("mAP50")


# ── Subprocess helpers ────────────────────────────────────────────────────────

def _env() -> dict:
    cpu_count = str(os.cpu_count() or 4)
    return {
        **os.environ,
        "PYTHONPATH": str(REPO / "src"),
        # Use all available CPU cores for PyTorch / OpenMP / MKL
        "OMP_NUM_THREADS": cpu_count,
        "MKL_NUM_THREADS": cpu_count,
        "OPENBLAS_NUM_THREADS": cpu_count,
        "NUMEXPR_NUM_THREADS": cpu_count,
    }


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

    scores: list[tuple[float, str]] = []
    for attack in ALL_ATTACKS:
        m = read_metrics(runs_root / f"attack_{attack}")
        if not m:
            continue
        conf = get_avg_conf(m) or baseline_conf
        drop = baseline_conf - conf
        log(f"  {attack:20s}  conf_drop={drop:+.4f}  "
            f"(baseline={baseline_conf:.4f} → {conf:.4f})")
        scores.append((drop, attack))

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

    recovery_by_defense: dict[str, list[float]] = {d: [] for d in ALL_DEFENSES}

    for attack in state["top_attacks"]:
        attack_m = read_metrics(runs_root / f"attack_{attack}")
        if not attack_m:
            continue
        attack_conf = get_avg_conf(attack_m) or baseline_conf
        drop = baseline_conf - attack_conf
        if drop < 1e-6:
            continue  # attack had no measurable effect

        for defense in ALL_DEFENSES:
            def_m = read_metrics(runs_root / f"defended_{attack}_{defense}")
            if not def_m:
                continue
            def_conf = get_avg_conf(def_m) or attack_conf
            recovery = (def_conf - attack_conf) / drop
            log(f"  {attack:20s} + {defense:25s}  recovery={recovery:+.3f}")
            recovery_by_defense[defense].append(recovery)

    avg_scores: list[tuple[float, str]] = []
    for defense, vals in recovery_by_defense.items():
        avg = sum(vals) / len(vals) if vals else 0.0
        avg_scores.append((avg, defense))
        log(f"  {defense:25s}  avg_recovery={avg:.3f}  (n={len(vals)})")

    avg_scores.sort(reverse=True)
    return [d for _, d in avg_scores[:TOP_N_DEFENSES]]


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


def _run_and_score_attack(attack, params, run_name, runs_root, baseline_conf):
    run_single(attack=attack, defense="none", run_name=run_name,
               runs_root=runs_root, overrides=params, preset="tune")
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    conf = get_avg_conf(m) or baseline_conf
    return baseline_conf - conf


def _run_and_score_defense(attack, defense, params, run_name, runs_root,
                            baseline_conf, attack_conf):
    run_single(attack=attack, defense=defense, run_name=run_name,
               runs_root=runs_root, overrides=params, preset="tune")
    m = read_metrics(Path(runs_root) / run_name)
    if not m:
        return -1.0
    drop = baseline_conf - attack_conf
    if drop < 1e-6:
        return 0.0
    return (get_avg_conf(m) or attack_conf - attack_conf) / drop


def _coordinate_descent(label, param_space, score_fn, run_prefix,
                         existing_history=None):
    """
    Coordinate descent over param_space.

    Each iteration loops over every parameter, probes one step up and one step
    down, and commits to whichever direction improved the score by more than
    TUNE_TOLERANCE.  Stops when a full pass finds no improvement, or after
    TUNE_MAX_ITERS passes.

    Returns (best_params, best_score, history).
    """
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

    # ── Step 1: Tune each top attack (no defense) ─────────────────────────────
    for attack in state["top_attacks"]:
        space = ATTACK_PARAM_SPACE.get(attack)
        if not space:
            log(f"  No param space for {attack}, skipping")
            state.setdefault("best_attack_params", {})[attack] = {}
            continue

        existing = tune_history.get(f"attack_{attack}", [])

        def _atk_score(params, name, _a=attack, _bc=baseline_conf):
            return _run_and_score_attack(_a, params, name, runs_root, _bc)

        best_params, best_score, history = _coordinate_descent(
            label=attack, param_space=space,
            score_fn=_atk_score,
            run_prefix=f"tune_atk_{attack}",
            existing_history=existing,
        )
        tune_history[f"attack_{attack}"] = history
        state.setdefault("best_attack_params", {})[attack] = best_params
        log(f"  {attack} → {best_params}  conf_drop={best_score:.4f}")
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
    attack_conf = (get_avg_conf(tuned_m) or baseline_conf) if tuned_m else baseline_conf
    log(f"  Tuned attack conf={attack_conf:.4f}  "
        f"(drop={baseline_conf - attack_conf:.4f} vs baseline={baseline_conf:.4f})")

    # ── Step 3: Tune each top defense against the best attack ─────────────────
    for defense in state["top_defenses"]:
        space = DEFENSE_PARAM_SPACE.get(defense)
        if not space:
            log(f"  No param space for {defense}, skipping")
            state.setdefault("best_defense_params", {})[defense] = {}
            continue

        existing = tune_history.get(f"defense_{defense}", [])

        def _def_score(params, name, _s=strongest, _d=defense,
                       _bc=baseline_conf, _ac=attack_conf):
            return _run_and_score_defense(_s, _d, params, name,
                                          runs_root, _bc, _ac)

        best_params, best_score, history = _coordinate_descent(
            label=defense, param_space=space,
            score_fn=_def_score,
            run_prefix=f"tune_def_{defense}",
            existing_history=existing,
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

    # Best attack configs (no defense)
    for attack in state["top_attacks"]:
        run_single(
            attack=attack, defense="none",
            run_name=f"validate_atk_{attack}",
            runs_root=runs_root,
            overrides=best_atk.get(attack),
            preset="full", validation=True,
        )

    # Best attack × defense combos
    for attack in state["top_attacks"]:
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


def git_push_results(state: dict) -> None:
    """Commit cycle_history and framework_reports for this cycle and push."""
    cycle_id = state["cycle_id"]
    history_file = HISTORY_DIR / f"{cycle_id}.json"
    report_dir = Path(state.get("report_root", ""))

    paths_to_add: list[str] = []
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
                continue

            if not state["phase1_complete"]:
                if not phase1(state):
                    break
                save_state(state)
                generate_report(state)

            if not state["phase2_complete"]:
                if not phase2(state):
                    break
                save_state(state)
                generate_report(state)

            if not state["phase3_complete"]:
                if not phase3(state):
                    break
                save_state(state)

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

    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
