#!/usr/bin/env python3
"""Canonical single-run and sweep entry point for YOLO-Bad-Triangle.

Usage (single run):
    PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \\
        --profile yolo11n_lab_v1 \\
        --set attack.name=fgsm \\
        --set runner.run_name=my_run

Usage (sweep, forwarded to the compatibility backend in sweep_and_report.py):
    PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep \\
        --profile yolo11n_lab_v1 \\
        --attacks fgsm,pgd --preset smoke
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.cli_utils import (
    build_repo_python_command,
    build_run_experiment_command,
    load_yaml_mapping,
    resolve_python_bin,
    sanitize_segment,
    with_src_pythonpath,
)


def _log(component: str, severity: str, message: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    stream = sys.stderr if severity.upper() in {"WARN", "ERROR"} else sys.stdout
    print(f"{ts} [{component}] {severity.upper()}: {message}", file=stream)


def _run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
    rendered = " ".join(command)
    _log(component, "INFO", f"$ {rendered}")
    code = subprocess.call(command, env=env)
    if code != 0:
        _log(component, "ERROR", f"command failed with exit code {code}")
    return code


def _render_override_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float, str)):
        return str(value)
    return json.dumps(value, separators=(",", ":"))


def _mapping_to_overrides(prefix: str, payload: dict[str, object]) -> list[str]:
    overrides: list[str] = []
    for key, value in payload.items():
        if isinstance(value, dict):
            overrides.extend(_mapping_to_overrides(f"{prefix}.{key}", value))
            continue
        overrides.append(f"{prefix}.{key}={_render_override_value(value)}")
    return overrides


def _resolve_matrix_path_value(raw: object, *, base_dir: Path) -> str:
    expanded = os.path.expandvars(str(raw or "")).strip()
    path = Path(expanded).expanduser()
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return str(path)


def _expand_env_values(value: object) -> object:
    if isinstance(value, dict):
        return {key: _expand_env_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env_values(item) for item in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def _build_patch_matrix_commands(
    *,
    root: Path,
    matrix_config: Path,
    profile_override: str | None,
    cli_overrides: list[str],
    python_bin: str,
    dry_run: bool,
) -> list[list[str]]:
    payload = load_yaml_mapping(matrix_config)
    profile_name = str(profile_override or payload.get("profile") or "yolo11n_patch_eval_v1").strip()
    if not profile_name:
        raise ValueError("patch-matrix requires a profile name.")
    artifacts = payload.get("artifacts") or []
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("patch-matrix requires a non-empty 'artifacts' list.")
    defenses = payload.get("defenses") or ["none"]
    if not isinstance(defenses, list) or not defenses:
        raise ValueError("patch-matrix requires a non-empty 'defenses' list.")
    shared_overrides = [str(item) for item in (payload.get("overrides") or []) if str(item).strip()]
    defense_params = payload.get("defense_params") or {}
    if not isinstance(defense_params, dict):
        raise ValueError("patch-matrix defense_params must be a mapping when provided.")

    commands: list[list[str]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ValueError("Each patch-matrix artifact entry must be a mapping.")
        artifact_name = str(artifact.get("name") or "").strip()
        artifact_path_raw = artifact.get("artifact_path")
        if not artifact_name or not str(artifact_path_raw or "").strip():
            raise ValueError("Each artifact requires both 'name' and 'artifact_path'.")
        artifact_path = _resolve_matrix_path_value(artifact_path_raw, base_dir=matrix_config.parent)
        artifact_overrides = _mapping_to_overrides(
            "attack.params",
            {
                key: value
                for key, value in dict(_expand_env_values(dict(artifact.get("attack_params") or {}))).items()
                if key not in {"artifact_path", "placement_mode"}
            },
        )
        placement_modes = artifact.get("placement_modes") or ["largest_person_torso"]
        if not isinstance(placement_modes, list) or not placement_modes:
            raise ValueError("artifact placement_modes must be a non-empty list when provided.")
        local_defenses = artifact.get("defenses") or defenses
        if not isinstance(local_defenses, list) or not local_defenses:
            raise ValueError("artifact defenses must be a non-empty list when provided.")

        for placement_mode in placement_modes:
            for defense_name in local_defenses:
                run_name = (
                    f"patchmatrix__{sanitize_segment(artifact_name, 'artifact')}"
                    f"__{sanitize_segment(placement_mode, 'placement')}"
                    f"__{sanitize_segment(defense_name, 'defense')}"
                )
                overrides = [
                    *shared_overrides,
                    *cli_overrides,
                    "attack.name=pretrained_patch",
                    f"attack.params.artifact_path={artifact_path}",
                    f"attack.params.placement_mode={placement_mode}",
                    *artifact_overrides,
                    f"defense.name={defense_name}",
                    f"runner.run_name={run_name}",
                ]
                if defense_name in defense_params and isinstance(defense_params[defense_name], dict):
                    overrides.extend(
                        _mapping_to_overrides(
                            "defense.params",
                            dict(_expand_env_values(dict(defense_params[defense_name]))),
                        )
                    )
                command = build_run_experiment_command(
                    root,
                    None,
                    overrides,
                    profile=profile_name,
                    python_bin=python_bin,
                )
                if dry_run:
                    command.append("--dry-run")
                commands.append(command)
    return commands


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Unified framework-first public entry surface for single runs and sweeps. "
            "The sweep subcommand forwards to scripts/sweep_and_report.py for backend compatibility."
        )
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    run_one = subparsers.add_parser("run-one", help="Run one framework experiment.")
    run_one_config = run_one.add_mutually_exclusive_group()
    run_one_config.add_argument("--config", default="configs/default.yaml")
    run_one_config.add_argument("--profile")
    run_one.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Config override in key=value form. Can be repeated.",
    )
    run_one.add_argument("--dry-run", action="store_true")
    run_one.add_argument("--list-plugins", action="store_true")
    run_one.add_argument("--seed", type=int, default=None,
        help="Random seed (overrides config). Shorthand for --set runner.seed=N.")

    sweep = subparsers.add_parser(
        "sweep",
        help="Run the canonical baseline + attack sweep with reports.",
    )
    sweep_config = sweep.add_mutually_exclusive_group()
    sweep_config.add_argument("--config", default="configs/default.yaml")
    sweep_config.add_argument("--profile")
    sweep.add_argument("--runs-root", default=None)
    sweep.add_argument("--report-root", default=None)
    sweep.add_argument("--attacks", default=None)
    sweep.add_argument("--defenses", default=None)
    sweep.add_argument("--preset", choices=("smoke", "full"), default=None)
    sweep.add_argument("--workers", default=None)
    sweep.add_argument("--phases", default=None)
    sweep.add_argument("--seed", type=int, default=None)
    sweep.add_argument("--max-images", type=int, default=None)
    sweep.add_argument("--resume", action="store_true")
    sweep.add_argument("--skip-errors", action="store_true")
    sweep.add_argument("--dry-run", action="store_true")
    sweep.add_argument(
        "--list-plugins",
        action="store_true",
        help="Print all available attack and defense plugin names and exit.",
    )
    sweep.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Config override in key=value form. Can be repeated and is forwarded to sweep_and_report.py.",
    )
    sweep.add_argument("--team-summary", dest="team_summary", action="store_true")
    sweep.add_argument("--no-team-summary", dest="team_summary", action="store_false")
    sweep.add_argument("--failure-gallery", dest="failure_gallery", action="store_true")
    sweep.add_argument("--no-failure-gallery", dest="failure_gallery", action="store_false")
    sweep.add_argument("--compat-dashboard", dest="compat_dashboard", action="store_true")
    sweep.add_argument("--no-compat-dashboard", dest="compat_dashboard", action="store_false")
    sweep.set_defaults(team_summary=None, failure_gallery=None, compat_dashboard=None)
    sweep.add_argument(
        "--reporting-dataset-scope",
        choices=("smoke", "tune", "full"),
        default=None,
    )
    sweep.add_argument(
        "--reporting-authority",
        choices=("diagnostic", "authoritative"),
        default=None,
    )
    sweep.add_argument(
        "--reporting-source-phase",
        choices=("phase1", "phase2", "phase3", "phase4", "manual"),
        default=None,
    )
    sweep.add_argument("--validation-enabled", action="store_true")

    patch_matrix = subparsers.add_parser(
        "patch-matrix",
        help="Run imported patch artifacts across placement-mode and defense combinations.",
    )
    patch_matrix.add_argument(
        "--matrix-config",
        default="configs/patch_artifacts.yaml",
        help="YAML file describing imported patch artifacts and defense combinations.",
    )
    patch_matrix.add_argument(
        "--profile",
        default=None,
        help="Optional profile override for the patch matrix (defaults to the matrix file profile).",
    )
    patch_matrix.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Additional config override in key=value form. Can be repeated.",
    )
    patch_matrix.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    python_bin = resolve_python_bin(ROOT)
    runtime_env = with_src_pythonpath(ROOT)

    if args.mode == "run-one":
        overrides = list(args.overrides)
        if args.seed is not None:
            overrides.append(f"runner.seed={args.seed}")
        command = build_run_experiment_command(
            ROOT,
            None if args.profile else args.config,
            overrides,
            profile=args.profile,
            python_bin=python_bin,
        )
        if args.dry_run:
            command.append("--dry-run")
        if args.list_plugins:
            command.append("--list-plugins")
        raise SystemExit(_run(command, component="run-unified", env=runtime_env))

    if args.mode == "patch-matrix":
        matrix_config = Path(str(args.matrix_config)).expanduser().resolve()
        commands = _build_patch_matrix_commands(
            root=ROOT,
            matrix_config=matrix_config,
            profile_override=args.profile,
            cli_overrides=list(args.overrides),
            python_bin=python_bin,
            dry_run=bool(args.dry_run),
        )
        for command in commands:
            code = _run(command, component="patch-matrix", env=runtime_env)
            if code != 0:
                raise SystemExit(code)
        raise SystemExit(0)

    command = build_repo_python_command(
        ROOT,
        "scripts/sweep_and_report.py",
        ["--profile", str(args.profile)] if args.profile else ["--config", str(args.config)],
        python_bin=python_bin,
    )
    if args.runs_root:
        command.extend(["--runs-root", str(args.runs_root)])
    if args.report_root:
        command.extend(["--report-root", str(args.report_root)])
    if args.attacks:
        command.extend(["--attacks", str(args.attacks)])
    if args.defenses:
        command.extend(["--defenses", str(args.defenses)])
    if args.preset:
        command.extend(["--preset", str(args.preset)])
    if args.workers:
        command.extend(["--workers", str(args.workers)])
    if args.phases:
        command.extend(["--phases", str(args.phases)])
    if args.seed is not None:
        command.extend(["--seed", str(args.seed)])
    if args.max_images is not None:
        command.extend(["--max-images", str(args.max_images)])
    if args.resume:
        command.append("--resume")
    if args.skip_errors:
        command.append("--skip-errors")
    if args.dry_run:
        command.append("--dry-run")
    if args.list_plugins:
        command.append("--list-plugins")
    for override in args.overrides:
        command.extend(["--set", override])
    if args.team_summary is True:
        command.append("--team-summary")
    if args.team_summary is False:
        command.append("--no-team-summary")
    if args.failure_gallery is True:
        command.append("--failure-gallery")
    if args.failure_gallery is False:
        command.append("--no-failure-gallery")
    if args.compat_dashboard is True:
        command.append("--compat-dashboard")
    if args.compat_dashboard is False:
        command.append("--no-compat-dashboard")
    if args.reporting_dataset_scope:
        command.extend(["--reporting-dataset-scope", str(args.reporting_dataset_scope)])
    if args.reporting_authority:
        command.extend(["--reporting-authority", str(args.reporting_authority)])
    if args.reporting_source_phase:
        command.extend(["--reporting-source-phase", str(args.reporting_source_phase)])
    if args.validation_enabled:
        command.append("--validation-enabled")
    raise SystemExit(_run(command, component="run-unified", env=runtime_env))


if __name__ == "__main__":
    main()
