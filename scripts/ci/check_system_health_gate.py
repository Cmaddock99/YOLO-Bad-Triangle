#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="CI system health gate wrapper.")
    parser.add_argument("--parity-config", default="configs/parity_test.yaml")
    parser.add_argument("--demo-profile", default="demo")
    parser.add_argument("--demo-output-root", default="outputs/demo-gate-ci")
    parser.add_argument("--health-output-root", default="outputs/system_health")
    parser.add_argument("--allow-missing-baseline", action="store_true")
    parser.add_argument("--auto-fix", action="store_true")
    args = parser.parse_args()

    command = [
        sys.executable,
        str(ROOT / "run_system_health_check.py"),
        "--parity-config",
        str(Path(args.parity_config).expanduser().resolve()),
        "--demo-profile",
        args.demo_profile,
        "--demo-output-root",
        str(Path(args.demo_output_root).expanduser().resolve()),
        "--health-output-root",
        str(Path(args.health_output_root).expanduser().resolve()),
    ]
    if args.allow_missing_baseline:
        command.append("--allow-missing-baseline")
    if args.auto_fix:
        command.append("--auto-fix")
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    proc = subprocess.run(command, cwd=str(ROOT), env=env, check=False)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
