#!/usr/bin/env python3
"""Multi-attack × multi-defense sweep with reporting.

Runs all requested attack/defense combinations in parallel subprocesses and
generates a comparison report under outputs/framework_reports/<sweep_id>/.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \\
        --attacks fgsm,pgd,deepfool \\
        --defenses c_dog,median_preprocess \\
        --preset full \\
        --workers auto \\
        --validation-enabled

Use --list-plugins to see all registered attacks and defenses.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
import shlex
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from lab.runners.cli_utils import (
    apply_override,
    build_repo_python_command,
    build_run_experiment_command,
    load_yaml_mapping,
    with_src_pythonpath,
)
from lab.runners.run_intent import build_run_intent


CANONICAL_ATTACK_ALIASES = {
    "gaussian_blur": "blur",
    "ifgsm": "pgd",
    "bim": "pgd",
    "cw_l2": "cw",
    "square_attack": "square",
    "dr": "dispersion_reduction",
    "localized_fgsm_center_patch": "fgsm_center_mask",
    "localized_fgsm_edge_patch": "fgsm_edge_mask",
}
CANONICAL_ATTACKS_ALL = (
    "blur",
    "cw",
    "deepfool",
    "dispersion_reduction",
    "eot_pgd",
    "fgsm",
    "fgsm_center_mask",
    "fgsm_edge_mask",
    "jpeg_attack",
    "pgd",
    "square",
)
DEFAULT_ATTACKS = ("blur", "deepfool", "fgsm", "pgd")
DEFAULT_DEFENSES = ("median_preprocess",)
REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RUN_ARTIFACTS = ("metrics.json", "run_summary.json", "predictions.jsonl")


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _now() -> str:
    """Current local time as HH:MM:SS for progress headers."""
    return datetime.now().strftime("%H:%M:%S")


def _phase_header(n: int, label: str) -> str:
    return f"[{_now()}] Phase {n}: {label}"


def _parse_phases(raw: str) -> set[int]:
    phases: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
        except ValueError:
            raise ValueError(f"Invalid phase {part!r}: phases must be integers (1-4).")
        if n not in {1, 2, 3, 4}:
            raise ValueError(f"Invalid phase {n}: must be 1, 2, 3, or 4.")
        phases.add(n)
    if not phases:
        raise ValueError("--phases must include at least one phase number.")
    return phases


def _list_plugins() -> None:
    sys.path.insert(0, str((REPO_ROOT / "src").resolve()))
    from lab.attacks.framework_registry import list_available_attack_plugins
    from lab.defenses.framework_registry import list_available_defense_plugins
    attacks = list_available_attack_plugins()
    defenses = [d for d in list_available_defense_plugins() if d not in {"none", "identity"}]
    print("Available attacks:")
    for a in attacks:
        print(f"  {a}")
    print("\nAvailable defenses:")
    for d in defenses:
        print(f"  {d}")


def _resolve_all_plugins(value: str, kind: str) -> list[str] | None:
    """Expand 'all' to every registered plugin of the given kind.

    Returns None when value is not 'all', signalling the caller to parse normally.
    """
    if value.strip().lower() != "all":
        return None  # signal: not 'all', parse normally
    sys.path.insert(0, str((REPO_ROOT / "src").resolve()))
    if kind == "attack":
        from lab.attacks.framework_registry import list_available_attack_plugins
        available = {
            str(name).strip().lower()
            for name in list_available_attack_plugins()
        }
        return [name for name in CANONICAL_ATTACKS_ALL if name in available]
    from lab.defenses.framework_registry import list_available_defense_plugins
    return [d for d in list_available_defense_plugins() if d not in {"none", "identity"}]


def _run_command(
    command: list[str],
    *,
    dry_run: bool,
    bar: tqdm | None = None,
    skip_errors: bool = False,
    include_src_pythonpath: bool = True,
) -> bool:
    """Run a command. Returns True on success, False on failure (when skip_errors=True)."""
    rendered = " ".join(shlex.quote(part) for part in command)
    _write(f"$ {rendered}", bar=bar)
    if dry_run:
        return True
    runtime_env = with_src_pythonpath(REPO_ROOT) if include_src_pythonpath else os.environ.copy()
    result = subprocess.run(command, capture_output=True, text=True, env=runtime_env)
    if result.returncode != 0:
        if result.stdout:
            _write(result.stdout.rstrip(), bar=bar)
        if result.stderr:
            _write(result.stderr.rstrip(), bar=bar)
        if skip_errors:
            return False
        raise subprocess.CalledProcessError(result.returncode, command)
    return True


def _write(msg: str, *, bar: tqdm | None = None) -> None:
    """Print via tqdm.write when inside a bar, otherwise plain print."""
    if bar is not None:
        bar.write(msg)
    else:
        print(msg)


def _fmt_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _metrics_exists(run_dir: Path) -> bool:
    return (run_dir / "metrics.json").is_file()


def _required_run_artifacts_status(run_dir: Path) -> tuple[bool, list[str]]:
    missing = [name for name in REQUIRED_RUN_ARTIFACTS if not (run_dir / name).is_file()]
    return not missing, missing


def _load_resume_fingerprint(run_dir: Path) -> dict[str, object] | None:
    summary_path = run_dir / "run_summary.json"
    if not summary_path.is_file():
        return None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    validation = payload.get("validation")
    if not isinstance(validation, dict):
        validation = {}
    reporting_context = payload.get("reporting_context")
    if not isinstance(reporting_context, dict):
        reporting_context = {}
    defense_checkpoints = provenance.get("defense_checkpoints")
    if not isinstance(defense_checkpoints, list):
        defense_checkpoints = []
    defense_shas = sorted(
        str(item.get("sha256", "")).strip()
        for item in defense_checkpoints
        if isinstance(item, dict) and str(item.get("sha256", "")).strip()
    )
    return {
        "config_fingerprint_sha256": provenance.get("config_fingerprint_sha256"),
        "attack_signature": ((payload.get("attack") or {}).get("signature") if isinstance(payload.get("attack"), dict) else None),
        "defense_signature": ((payload.get("defense") or {}).get("signature") if isinstance(payload.get("defense"), dict) else None),
        "checkpoint_fingerprint_sha256": provenance.get("checkpoint_fingerprint_sha256"),
        "defense_checkpoint_shas": defense_shas,
        "seed": payload.get("seed"),
        "validation_enabled": validation.get("enabled"),
        "reporting_context": dict(reporting_context),
    }


def _normalize_intended_fingerprint(intent: dict[str, object]) -> dict[str, object]:
    defense_checkpoints = intent.get("defense_checkpoints")
    if not isinstance(defense_checkpoints, list):
        defense_checkpoints = []
    defense_shas = sorted(
        str(item.get("sha256", "")).strip()
        for item in defense_checkpoints
        if isinstance(item, dict) and str(item.get("sha256", "")).strip()
    )
    reporting_context = intent.get("reporting_context")
    if not isinstance(reporting_context, dict):
        reporting_context = {}
    return {
        "config_fingerprint_sha256": intent.get("config_fingerprint_sha256"),
        "attack_signature": intent.get("attack_signature"),
        "defense_signature": intent.get("defense_signature"),
        "checkpoint_fingerprint_sha256": intent.get("checkpoint_fingerprint_sha256"),
        "defense_checkpoint_shas": defense_shas,
        "seed": intent.get("seed"),
        "validation_enabled": intent.get("validation_enabled"),
        "reporting_context": dict(reporting_context),
    }


def _check_resume(run_dir: Path, intended_intent: dict[str, object]) -> tuple[str, str]:
    artifacts_complete, missing = _required_run_artifacts_status(run_dir)
    if not run_dir.exists() or (
        not (run_dir / "metrics.json").exists()
        and not (run_dir / "run_summary.json").exists()
        and not (run_dir / "predictions.jsonl").exists()
    ):
        return "run", ""
    if not artifacts_complete:
        return "reran_partial", f"missing required artifacts: {', '.join(missing)}"
    existing = _load_resume_fingerprint(run_dir)
    if existing is None:
        return "reran_partial", "run_summary.json missing or malformed"
    intended = _normalize_intended_fingerprint(intended_intent)
    # Only compare fields where the intended value is known (non-None).
    # When the sweep cannot compute a field (e.g. checkpoint SHA when the
    # file is absent on this machine), skip it rather than forcing a spurious
    # reran_mismatch on every --resume invocation.
    mismatches = [
        key for key in sorted(intended)
        if intended.get(key) is not None and existing.get(key) != intended.get(key)
    ]
    if mismatches:
        return "reran_mismatch", f"run intent changed: {', '.join(mismatches)}"
    return "skipped_exact", "exact run-intent match"


def _parse_csv_list(raw: str, label: str) -> list[str]:
    items = [part.strip() for part in raw.split(",") if part.strip()]
    if not items:
        raise ValueError(f"Expected at least one {label} in --{label}s.")
    return items


def _canonicalize_attack_name(name: str) -> str:
    normalized = str(name).strip().lower()
    return CANONICAL_ATTACK_ALIASES.get(normalized, normalized)


def _normalize_requested_attacks(attacks: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for attack in attacks:
        canonical = _canonicalize_attack_name(attack)
        if canonical in seen:
            continue
        normalized.append(canonical)
        seen.add(canonical)
    return normalized


def _parse_attacks(raw: str) -> list[str]:
    resolved = _resolve_all_plugins(raw, "attack")
    attacks = resolved if resolved is not None else _parse_csv_list(raw, "attack")
    return _normalize_requested_attacks(attacks)


def _parse_defenses(raw: str) -> list[str]:
    resolved = _resolve_all_plugins(raw, "defense")
    return resolved if resolved is not None else _parse_csv_list(raw, "defense")


def _experiment_overrides(
    *,
    output_root: Path,
    run_name: str,
    attack_name: str,
    defense_name: str,
    seed: int,
    max_images: int,
    validation_enabled: bool,
    objective_mode: str | None = None,
    target_class: int | None = None,
    attack_roi: str | None = None,
    reporting_run_role: str | None = None,
    reporting_dataset_scope: str | None = None,
    reporting_authority: str | None = None,
    reporting_source_phase: str | None = None,
) -> list[str]:
    overrides = [
        f"runner.output_root={output_root}",
        f"runner.run_name={run_name}",
        f"runner.seed={seed}",
        f"runner.max_images={max_images}",
        f"attack.name={attack_name}",
        f"defense.name={defense_name}",
        f"validation.enabled={str(validation_enabled).lower()}",
        "summary.enabled=false",
    ]
    if objective_mode:
        overrides.append(f"attack.params.objective_mode={objective_mode}")
    if target_class is not None:
        overrides.append(f"attack.params.target_class={int(target_class)}")
    if attack_roi:
        overrides.append(f"attack.params.attack_roi={attack_roi}")
    if reporting_run_role:
        overrides.append(f"reporting_context.run_role={reporting_run_role}")
    if reporting_dataset_scope:
        overrides.append(f"reporting_context.dataset_scope={reporting_dataset_scope}")
    if reporting_authority:
        overrides.append(f"reporting_context.authority={reporting_authority}")
    if reporting_source_phase:
        overrides.append(f"reporting_context.source_phase={reporting_source_phase}")
    return overrides


def _experiment_command(
    *,
    python_bin: str,
    config: Path,
    output_root: Path,
    run_name: str,
    attack_name: str,
    defense_name: str,
    seed: int,
    max_images: int,
    validation_enabled: bool,
    objective_mode: str | None = None,
    target_class: int | None = None,
    attack_roi: str | None = None,
    reporting_run_role: str | None = None,
    reporting_dataset_scope: str | None = None,
    reporting_authority: str | None = None,
    reporting_source_phase: str | None = None,
) -> list[str]:
    overrides = _experiment_overrides(
        output_root=output_root,
        run_name=run_name,
        attack_name=attack_name,
        defense_name=defense_name,
        seed=seed,
        max_images=max_images,
        validation_enabled=validation_enabled,
        objective_mode=objective_mode,
        target_class=target_class,
        attack_roi=attack_roi,
        reporting_run_role=reporting_run_role,
        reporting_dataset_scope=reporting_dataset_scope,
        reporting_authority=reporting_authority,
        reporting_source_phase=reporting_source_phase,
    )
    return build_run_experiment_command(
        REPO_ROOT,
        config,
        overrides,
        python_bin=python_bin,
    )


def _print_summary_command(
    *,
    python_bin: str,
    baseline_dir: Path,
    attack_dir: Path,
) -> list[str]:
    return build_repo_python_command(
        REPO_ROOT,
        "scripts/print_summary.py",
        ["--baseline", str(baseline_dir), "--attack", str(attack_dir)],
        python_bin=python_bin,
    )


def _generate_framework_report_command(
    *,
    python_bin: str,
    runs_root: Path,
    output_dir: Path,
) -> list[str]:
    return build_repo_python_command(
        REPO_ROOT,
        "scripts/generate_framework_report.py",
        ["--runs-root", str(runs_root), "--output-dir", str(output_dir)],
        python_bin=python_bin,
    )


def _generate_team_summary_command(
    *,
    python_bin: str,
    report_root: Path,
) -> list[str]:
    return build_repo_python_command(
        REPO_ROOT,
        "scripts/generate_team_summary.py",
        ["--report-root", str(report_root)],
        python_bin=python_bin,
    )


def _generate_failure_gallery_command(
    *,
    python_bin: str,
    runs_root: Path,
    output_path: Path,
) -> list[str]:
    return build_repo_python_command(
        REPO_ROOT,
        "scripts/generate_failure_gallery.py",
        ["--runs-root", str(runs_root), "--output", str(output_path)],
        python_bin=python_bin,
    )


def _default_max_images(preset: str) -> int:
    if preset == "full":
        return 0
    return 8


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run baseline + attack sweep (+ optional defense sweep) and generate reports."
    )
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--python-bin", default="./.venv/bin/python")
    parser.add_argument("--runs-root", help="Optional output root for framework runs.")
    parser.add_argument("--report-root", help="Optional output root for report artifacts.")
    parser.add_argument(
        "--attacks",
        default=",".join(DEFAULT_ATTACKS),
        help="Comma-separated attack names, or 'all' to run every registered attack plugin.",
    )
    parser.add_argument(
        "--defenses",
        default=",".join(DEFAULT_DEFENSES),
        help="Comma-separated defenses to sweep against each attack. "
             "Use 'none' to skip the defense sweep, or 'all' for every registered defense plugin.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-images", type=int)
    parser.add_argument("--baseline-run-name", default="baseline_none")
    parser.add_argument(
        "--preset",
        choices=("smoke", "full"),
        default="smoke",
        help="smoke=fast sanity defaults (8 images), full=all images.",
    )
    parser.add_argument("--validation-enabled", action="store_true")
    parser.add_argument(
        "--reporting-dataset-scope",
        choices=("smoke", "tune", "full"),
        help="Optional reporting metadata stamped onto each launched run.",
    )
    parser.add_argument(
        "--reporting-authority",
        choices=("diagnostic", "authoritative"),
        help="Optional reporting metadata stamped onto each launched run.",
    )
    parser.add_argument(
        "--reporting-source-phase",
        choices=("phase1", "phase2", "phase3", "phase4", "manual"),
        help="Optional reporting metadata stamped onto each launched run.",
    )
    parser.add_argument(
        "--objective-mode",
        choices=(
            "untargeted_conf_suppression",
            "target_class_misclassification",
            "class_conditional_hiding",
        ),
        help="Optional semantic objective mode applied to all gradient attacks in this sweep.",
    )
    parser.add_argument(
        "--target-class",
        type=int,
        help="Optional target class ID used by target/hiding objectives.",
    )
    parser.add_argument(
        "--attack-roi",
        help="Optional normalized ROI x,y,w,h (for example 0.2,0.2,0.5,0.5).",
    )
    parser.add_argument("--resume", action="store_true", help="Skip runs that already have metrics.json.")
    parser.add_argument(
        "--phases",
        default="1,2,3,4",
        help=(
            "Comma-separated phases to run (default: 1,2,3,4). "
            "1=baseline  2=attacks  3=defenses  4=reports. "
            "Example: --phases 3,4 to re-run only defenses + reports against an existing --runs-root."
        ),
    )
    parser.add_argument(
        "--workers",
        default="1",
        help="Parallel experiment workers. Pass a number (e.g. 4) or 'auto' to use CPU count. "
             "Default 1 = serial.",
    )
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="Continue the sweep when a run fails instead of aborting. "
             "All failures are reported at the end.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing.")
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="Print all available attack and defense plugin names and exit.",
    )
    parser.add_argument(
        "--team-summary",
        dest="team_summary",
        action="store_true",
        help="Generate team_summary.json and team_summary.md after aggregate report.",
    )
    parser.add_argument(
        "--no-team-summary",
        dest="team_summary",
        action="store_false",
    )
    parser.set_defaults(team_summary=True)
    try:
        args = parser.parse_args()

        if args.list_plugins:
            _list_plugins()
            return

        # Resolve workers: integer or 'auto'
        if str(args.workers).strip().lower() == "auto":
            workers = max(1, os.cpu_count() or 1)
        else:
            workers = max(1, int(args.workers))

        runs_root = (
            Path(args.runs_root).expanduser().resolve()
            if args.runs_root
            else Path(f"outputs/framework_runs/sweep_{_timestamp()}").resolve()
        )
        report_root = (
            Path(args.report_root).expanduser().resolve()
            if args.report_root
            else Path(f"outputs/framework_reports/{runs_root.name}").resolve()
        )
        config = Path(args.config).expanduser().resolve()
        if not config.is_file():
            raise FileNotFoundError(f"Config not found: {config}")
        base_config = load_yaml_mapping(config)
        python_bin_path = Path(args.python_bin).expanduser()
        if not python_bin_path.is_file():
            raise FileNotFoundError(f"Python binary not found: {python_bin_path}")

        phases = _parse_phases(args.phases)
        max_images = args.max_images if args.max_images is not None else _default_max_images(args.preset)
        attacks = _parse_attacks(args.attacks)
        raw_defenses = _parse_defenses(args.defenses)
        defenses = [d for d in raw_defenses if d.lower() != "none"]

        runs_root.mkdir(parents=True, exist_ok=True)
        report_root.mkdir(parents=True, exist_ok=True)

        # --- Startup banner ---
        phase_names = {1: "baseline", 2: "attacks", 3: "defenses", 4: "reports"}
        running_phases = sorted(phases)
        print(f"[{_now()}] Sweep starting")
        print(f"  Runs root:    {runs_root}")
        print(f"  Reports root: {report_root}")
        print(f"  Attacks:      {attacks}")
        if defenses:
            print(f"  Defenses:     {defenses}")
        total_runs = (
            (1 if 1 in phases else 0)
            + (len(attacks) if 2 in phases else 0)
            + (len(attacks) * len(defenses) if 3 in phases else 0)
        )
        phase_label = " → ".join(f"{n}:{phase_names[n]}" for n in running_phases)
        print(f"  Phases:       {phase_label}")
        print(f"  Total runs:   {total_runs}")
        if workers > 1:
            print(f"  Workers:      {workers} parallel")
        if args.objective_mode:
            print(f"  Objective:    {args.objective_mode}")
        if args.target_class is not None:
            print(f"  Target class: {args.target_class}")
        if args.attack_roi:
            print(f"  Attack ROI:   {args.attack_roi}")
        if args.skip_errors:
            print("  Mode:         skip-errors (failures collected, not fatal)")
        print()

        sweep_t0 = time.monotonic()
        failures: list[str] = []
        phase_times: dict[int, float] = {}
        manifest_entries: dict[str, dict[str, object]] = {}
        manifest_lock = threading.Lock()
        intent_cache: dict[tuple[str, ...], dict[str, object]] = {}
        intent_cache_lock = threading.Lock()

        def _record_manifest(run_name: str, *, status: str, reason: str = "", elapsed_ms: float | None = None) -> None:
            entry: dict[str, object] = {"status": status}
            if reason:
                entry["reason"] = reason
            if elapsed_ms is not None:
                entry["elapsed_ms"] = round(elapsed_ms, 1)
            with manifest_lock:
                manifest_entries[run_name] = entry

        def _resolved_intent(overrides: list[str]) -> dict[str, object]:
            key = tuple(overrides)
            with intent_cache_lock:
                cached = intent_cache.get(key)
            if cached is not None:
                return dict(cached)
            resolved = deepcopy(base_config)
            for assignment in overrides:
                apply_override(resolved, assignment)
            intent = build_run_intent(resolved, cwd=REPO_ROOT)
            with intent_cache_lock:
                intent_cache[key] = dict(intent)
            return dict(intent)

        # --- Phase 1: Baseline ---
        baseline_dir = runs_root / args.baseline_run_name
        if 1 in phases:
            baseline_overrides = _experiment_overrides(
                output_root=runs_root,
                run_name=args.baseline_run_name,
                attack_name="none",
                defense_name="none",
                seed=args.seed,
                max_images=max_images,
                validation_enabled=args.validation_enabled,
                objective_mode=args.objective_mode,
                target_class=args.target_class,
                attack_roi=args.attack_roi,
                reporting_run_role="baseline",
                reporting_dataset_scope=args.reporting_dataset_scope,
                reporting_authority=args.reporting_authority,
                reporting_source_phase=args.reporting_source_phase,
            )
            resume_action = "run"
            resume_reason = ""
            if args.resume:
                resume_action, resume_reason = _check_resume(
                    baseline_dir,
                    _resolved_intent(baseline_overrides),
                )
                if resume_action == "skipped_exact":
                    _record_manifest(args.baseline_run_name, status=resume_action, reason=resume_reason, elapsed_ms=0.0)
                    print(f"[{_now()}] Phase 1/baseline: skipping ({resume_reason})")
                    phase_times[1] = 0.0
                else:
                    _record_manifest(args.baseline_run_name, status=resume_action, reason=resume_reason)
            if not args.resume or resume_action != "skipped_exact":
                print(f"[{_now()}] Phase 1/baseline: starting...")
                t0 = time.monotonic()
                ok = _run_command(
                    build_run_experiment_command(
                        REPO_ROOT,
                        config,
                        baseline_overrides,
                        python_bin=args.python_bin,
                    ),
                    dry_run=args.dry_run,
                    skip_errors=args.skip_errors,
                )
                elapsed = time.monotonic() - t0
                phase_times[1] = elapsed
                if ok:
                    status = "ran"
                    if args.resume and resume_action in {"reran_partial", "reran_mismatch"}:
                        status = resume_action
                    _record_manifest(args.baseline_run_name, status=status, reason=resume_reason if args.resume else "", elapsed_ms=elapsed * 1000)
                    print(f"[{_now()}] Phase 1/baseline: done ({_fmt_elapsed(elapsed)})")
                else:
                    failures.append("baseline")
                    _record_manifest(args.baseline_run_name, status="failed", reason=resume_reason if args.resume else "command failed", elapsed_ms=elapsed * 1000)
                    print(f"[{_now()}] Phase 1/baseline: FAILED ({_fmt_elapsed(elapsed)}) — continuing")
        else:
            print(f"[{_now()}] Phase 1/baseline: skipped (not in --phases)")

        # --- Phase 2: Attack sweep ---
        def _run_attack_job(attack: str, bar: tqdm) -> tuple[str, bool]:
            attack_run_name = f"attack_{attack}"
            attack_dir = runs_root / attack_run_name
            attack_overrides = _experiment_overrides(
                output_root=runs_root,
                run_name=attack_run_name,
                attack_name=attack,
                defense_name="none",
                seed=args.seed,
                max_images=max_images,
                validation_enabled=args.validation_enabled,
                objective_mode=args.objective_mode,
                target_class=args.target_class,
                attack_roi=args.attack_roi,
                reporting_run_role="attack_only",
                reporting_dataset_scope=args.reporting_dataset_scope,
                reporting_authority=args.reporting_authority,
                reporting_source_phase=args.reporting_source_phase,
            )
            t0 = time.monotonic()
            resume_action = "run"
            resume_reason = ""
            if args.resume:
                resume_action, resume_reason = _check_resume(
                    attack_dir,
                    _resolved_intent(attack_overrides),
                )
                if resume_action == "skipped_exact":
                    _record_manifest(attack_run_name, status=resume_action, reason=resume_reason, elapsed_ms=0.0)
                    _write(f"  [{_now()}] {attack_run_name}: skipped ({resume_reason})", bar=bar)
                    return attack, True
            ok = _run_command(
                build_run_experiment_command(
                    REPO_ROOT,
                    config,
                    attack_overrides,
                    python_bin=args.python_bin,
                ),
                dry_run=args.dry_run,
                bar=bar,
                skip_errors=args.skip_errors,
            )
            elapsed = time.monotonic() - t0
            status = "done" if ok else "FAILED"
            manifest_status = "ran"
            if resume_action in {"reran_partial", "reran_mismatch"}:
                manifest_status = resume_action
            if ok:
                _record_manifest(attack_run_name, status=manifest_status, reason=resume_reason, elapsed_ms=elapsed * 1000)
            else:
                _record_manifest(attack_run_name, status="failed", reason=resume_reason or "command failed", elapsed_ms=elapsed * 1000)
            _write(f"  [{_now()}] {attack_run_name}: {status} ({_fmt_elapsed(elapsed)})", bar=bar)

            if ok:
                summary_command = _print_summary_command(
                    python_bin=args.python_bin,
                    baseline_dir=baseline_dir,
                    attack_dir=attack_dir,
                )
                summary_out = report_root / f"summary_{attack}.txt"
                rendered = " ".join(shlex.quote(part) for part in summary_command)
                _write(f"$ {rendered} > {shlex.quote(str(summary_out))}", bar=bar)
                if not args.dry_run:
                    with summary_out.open("w", encoding="utf-8") as handle:
                        subprocess.run(summary_command, check=True, stdout=handle)
            return attack, ok

        if 2 in phases:
            print(f"[{_now()}] Phase 2/attacks: starting ({len(attacks)} attack(s), workers={workers})...")
            t0_p2 = time.monotonic()
            with tqdm(total=len(attacks), desc="  attacks", unit="attack", dynamic_ncols=True) as bar2:
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = {pool.submit(_run_attack_job, attack, bar2): attack for attack in attacks}
                    for fut in as_completed(futures):
                        attack = futures[fut]
                        _, ok = fut.result()
                        if not ok:
                            failures.append(f"attack_{attack}")
                        bar2.set_description(f"  attacks | {attack} {'done' if ok else 'FAILED'}")
                        bar2.update(1)
            phase_times[2] = time.monotonic() - t0_p2
            print(f"[{_now()}] Phase 2/attacks: done ({_fmt_elapsed(phase_times[2])})")
        else:
            print(f"[{_now()}] Phase 2/attacks: skipped (not in --phases)")

        # --- Phase 3: Defense sweep ---
        def _run_defense_job(attack: str, defense: str, bar: tqdm) -> tuple[str, bool]:
            defended_run_name = f"defended_{attack}_{defense}"
            defended_dir = runs_root / defended_run_name
            defense_overrides = _experiment_overrides(
                output_root=runs_root,
                run_name=defended_run_name,
                attack_name=attack,
                defense_name=defense,
                seed=args.seed,
                max_images=max_images,
                validation_enabled=args.validation_enabled,
                objective_mode=args.objective_mode,
                target_class=args.target_class,
                attack_roi=args.attack_roi,
                reporting_run_role="defended",
                reporting_dataset_scope=args.reporting_dataset_scope,
                reporting_authority=args.reporting_authority,
                reporting_source_phase=args.reporting_source_phase,
            )
            t0 = time.monotonic()
            resume_action = "run"
            resume_reason = ""
            if args.resume:
                resume_action, resume_reason = _check_resume(
                    defended_dir,
                    _resolved_intent(defense_overrides),
                )
                if resume_action == "skipped_exact":
                    _record_manifest(defended_run_name, status=resume_action, reason=resume_reason, elapsed_ms=0.0)
                    _write(f"  [{_now()}] {defended_run_name}: skipped ({resume_reason})", bar=bar)
                    return defended_run_name, True
            ok = _run_command(
                build_run_experiment_command(
                    REPO_ROOT,
                    config,
                    defense_overrides,
                    python_bin=args.python_bin,
                ),
                dry_run=args.dry_run,
                bar=bar,
                skip_errors=args.skip_errors,
            )
            elapsed = time.monotonic() - t0
            status = "done" if ok else "FAILED"
            manifest_status = "ran"
            if resume_action in {"reran_partial", "reran_mismatch"}:
                manifest_status = resume_action
            if ok:
                _record_manifest(defended_run_name, status=manifest_status, reason=resume_reason, elapsed_ms=elapsed * 1000)
            else:
                _record_manifest(defended_run_name, status="failed", reason=resume_reason or "command failed", elapsed_ms=elapsed * 1000)
            _write(f"  [{_now()}] {defended_run_name}: {status} ({_fmt_elapsed(elapsed)})", bar=bar)
            return defended_run_name, ok

        if 3 in phases:
            defense_pairs = [(a, d) for a in attacks for d in defenses]
            n_pairs = len(defense_pairs)
            print(f"[{_now()}] Phase 3/defenses: starting ({n_pairs} run(s), workers={workers})...")
            t0_p3 = time.monotonic()
            with tqdm(total=n_pairs, desc="  defenses", unit="run", dynamic_ncols=True) as bar3:
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures3 = {
                        pool.submit(_run_defense_job, attack, defense, bar3): (attack, defense)
                        for attack, defense in defense_pairs
                    }
                    for fut in as_completed(futures3):
                        attack, defense = futures3[fut]
                        run_name, ok = fut.result()
                        if not ok:
                            failures.append(run_name)
                        bar3.set_description(f"  defenses | {attack}+{defense} {'done' if ok else 'FAILED'}")
                        bar3.update(1)
            phase_times[3] = time.monotonic() - t0_p3
            print(f"[{_now()}] Phase 3/defenses: done ({_fmt_elapsed(phase_times[3])})")
        else:
            print(f"[{_now()}] Phase 3/defenses: skipped (not in --phases)")

        # --- Phase 4: Reports ---
        if 4 in phases:
            report_steps = 3 if args.team_summary else 2
            print(f"[{_now()}] Phase 4/reports: generating ({report_steps} report(s))...")
            t0_p4 = time.monotonic()
            with tqdm(total=report_steps, desc="  reports", unit="report", dynamic_ncols=True) as bar4:
                _run_command(
                    _generate_framework_report_command(
                        python_bin=args.python_bin,
                        runs_root=runs_root,
                        output_dir=report_root,
                    ),
                    dry_run=args.dry_run,
                    bar=bar4,
                )
                bar4.set_description("  reports | framework report done")
                bar4.update(1)
                if args.team_summary:
                    _run_command(
                        _generate_team_summary_command(
                            python_bin=args.python_bin,
                            report_root=report_root,
                        ),
                        dry_run=args.dry_run,
                        bar=bar4,
                    )
                    bar4.set_description("  reports | team summary done")
                    bar4.update(1)
                _run_command(
                    _generate_failure_gallery_command(
                        python_bin=args.python_bin,
                        runs_root=runs_root,
                        output_path=report_root / "failure_gallery.html",
                    ),
                    dry_run=args.dry_run,
                    bar=bar4,
                    skip_errors=True,
                )
                bar4.set_description("  reports | failure gallery done")
                bar4.update(1)

            # Generate dashboard
            dashboard_out = Path("outputs/dashboard.html").resolve()
            _run_command(
                build_repo_python_command(
                    REPO_ROOT,
                    "scripts/generate_dashboard.py",
                    ["--reports-root", str(report_root.parent), "--output", str(dashboard_out)],
                    python_bin=args.python_bin,
                ),
                dry_run=args.dry_run,
                bar=bar4,
            )
            bar4.set_description("  reports | dashboard done")

            phase_times[4] = time.monotonic() - t0_p4
            print(f"[{_now()}] Phase 4/reports: done ({_fmt_elapsed(phase_times[4])})")
        else:
            print(f"[{_now()}] Phase 4/reports: skipped (not in --phases)")

        manifest = {
            "sweep_id": runs_root.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "config_path": str(config),
            "config_fingerprint_sha256": build_run_intent(base_config, cwd=REPO_ROOT)["config_fingerprint_sha256"],
            "requested_attacks": attacks,
            "requested_defenses": defenses,
            "seed": args.seed,
            "validation_enabled": args.validation_enabled,
            "runs": dict(sorted(manifest_entries.items())),
        }
        aggregate_counts = {
            "total": len(manifest_entries),
            "ran": sum(1 for entry in manifest_entries.values() if entry.get("status") == "ran"),
            "skipped_exact": sum(1 for entry in manifest_entries.values() if entry.get("status") == "skipped_exact"),
            "reran_partial": sum(1 for entry in manifest_entries.values() if entry.get("status") == "reran_partial"),
            "reran_mismatch": sum(1 for entry in manifest_entries.values() if entry.get("status") == "reran_mismatch"),
            "failed": sum(1 for entry in manifest_entries.values() if entry.get("status") == "failed"),
            "total_elapsed_ms": round((time.monotonic() - sweep_t0) * 1000, 1),
        }
        manifest["aggregate"] = aggregate_counts
        (report_root / "sweep_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        # --- Final summary ---
        total_elapsed = time.monotonic() - sweep_t0
        print()
        print("=" * 60)
        print(f"Sweep complete — total time: {_fmt_elapsed(total_elapsed)}")
        if phase_times:
            print("Phase breakdown:")
            for n in sorted(phase_times):
                print(f"  Phase {n}/{phase_names[n]:<10} {_fmt_elapsed(phase_times[n])}")
        if failures:
            print(f"\nWARNING: {len(failures)} run(s) failed: {', '.join(failures)}")
        if 4 in phases:
            print()
            print(f"Per-attack summaries: {report_root}/summary_*.txt")
            print(f"Aggregate CSV:        {report_root}/framework_run_summary.csv")
            print(f"Aggregate Markdown:   {report_root}/framework_run_report.md")
            print(f"Failure Gallery:      {report_root}/failure_gallery.html")
            if args.team_summary:
                print(f"Team JSON summary:    {report_root}/team_summary.json")
                print(f"Team MD summary:      {report_root}/team_summary.md")
            print("Dashboard:            outputs/dashboard.html")
        print("=" * 60)
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
