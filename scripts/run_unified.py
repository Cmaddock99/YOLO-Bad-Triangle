#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.cli_utils import resolve_python_bin, with_src_pythonpath


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified framework-first entry surface for single runs and sweeps."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    run_one = subparsers.add_parser("run-one", help="Run one framework experiment.")
    run_one.add_argument("--config", default="configs/default.yaml")
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

    sweep = subparsers.add_parser("sweep", help="Run baseline + attack sweep with reports.")
    sweep.add_argument("--config", default="configs/default.yaml")
    sweep.add_argument("--runs-root", default=None)
    sweep.add_argument("--report-root", default=None)
    sweep.add_argument("--attacks", default=None)
    sweep.add_argument("--validation-enabled", action="store_true")

    args = parser.parse_args()
    python_bin = resolve_python_bin(ROOT)
    runtime_env = with_src_pythonpath(ROOT)

    if args.mode == "run-one":
        command = [
            python_bin,
            str(ROOT / "src/lab/runners/run_experiment.py"),
            "--config",
            str(args.config),
        ]
        for override in args.overrides:
            command.extend(["--set", override])
        if args.seed is not None:
            command.extend(["--set", f"runner.seed={args.seed}"])
        if args.dry_run:
            command.append("--dry-run")
        if args.list_plugins:
            command.append("--list-plugins")
        raise SystemExit(_run(command, component="run-unified", env=runtime_env))

    command = [
        python_bin,
        str(ROOT / "scripts/sweep_and_report.py"),
        "--config",
        str(args.config),
    ]
    if args.runs_root:
        command.extend(["--runs-root", str(args.runs_root)])
    if args.report_root:
        command.extend(["--report-root", str(args.report_root)])
    if args.attacks:
        command.extend(["--attacks", str(args.attacks)])
    if args.validation_enabled:
        command.append("--validation-enabled")
    raise SystemExit(_run(command, component="run-unified", env=runtime_env))


if __name__ == "__main__":
    main()
