#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.migration import allow_legacy_runtime, legacy_runtime_warning
from lab.runners.cli_utils import resolve_python_bin, with_src_pythonpath
from lab.runners import cli as legacy_cli


def _framework_attacks_from_legacy_config(config_path: Path) -> str:
    try:
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return "fgsm"
    if not isinstance(payload, dict):
        return "fgsm"
    experiments = payload.get("experiments", [])
    if not isinstance(experiments, list):
        return "fgsm"
    attacks: list[str] = []
    for item in experiments:
        if not isinstance(item, dict):
            continue
        attack = str(item.get("attack", "none")).strip().lower()
        if attack in {"", "none", "identity"}:
            continue
        if attack not in attacks:
            attacks.append(attack)
    return ",".join(attacks) if attacks else "fgsm"


def _run_framework_first(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root).expanduser().resolve()
    runs_root = output_root / "framework_runs"
    reports_root = output_root / "framework_reports"
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")

    # Legacy matrix configs are converted to framework sweep attack lists.
    attacks = args.attacks or _framework_attacks_from_legacy_config(config_path)
    framework_config = args.framework_config or str(ROOT / "configs/lab_framework_phase5.yaml")
    command = [
        resolve_python_bin(ROOT),
        str(ROOT / "scripts/run_unified.py"),
        "sweep",
        "--config",
        str(framework_config),
        "--runs-root",
        str(runs_root),
        "--report-root",
        str(reports_root),
        "--legacy-output-root",
        str(output_root),
        "--attacks",
        attacks,
    ]
    if args.validation_enabled:
        command.append("--validation-enabled")
    rendered = " ".join(command)
    print("FRAMEWORK-FIRST batch mode active via scripts/run_unified.py sweep.")
    print(f"$ {rendered}")
    return subprocess.call(command, env=with_src_pythonpath(ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Framework-first batch runner wrapper (legacy available via --legacy)."
    )
    parser.add_argument("--config", default="configs/week1_stabilization_demo_matrix.yaml")
    parser.add_argument("--output_root", default="outputs")
    parser.add_argument("--output-root", dest="output_root_dash", default=None)
    parser.add_argument(
        "--framework-config",
        default=None,
        help="Optional explicit framework config for framework-first mode.",
    )
    parser.add_argument("--attacks", default=None, help="Optional comma-separated attack list override.")
    parser.add_argument("--validation-enabled", action="store_true")
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Run legacy batch runtime directly (rollback-only mode).",
    )
    return parser


if __name__ == "__main__":
    parser = _build_parser()
    cli_args, _ = parser.parse_known_args()
    cli_args.output_root = cli_args.output_root_dash or cli_args.output_root
    if cli_args.legacy:
        if not allow_legacy_runtime(context="scripts/run_framework.py --legacy"):
            print(
                "ERROR: Legacy runtime is disabled by policy (USE_LEGACY_RUNTIME=false).",
                file=sys.stderr,
            )
            raise SystemExit(2)
        print(legacy_runtime_warning(operator_context="scripts/run_framework.py"))
        filtered = [arg for arg in sys.argv if arg != "--legacy"]
        old_argv = sys.argv[:]
        try:
            sys.argv = filtered
            legacy_cli.main()
        finally:
            sys.argv = old_argv
        raise SystemExit(0)
    try:
        code = _run_framework_first(cli_args)
        raise SystemExit(code)
    except (ValueError, FileNotFoundError, RuntimeError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

