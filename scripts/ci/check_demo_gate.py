#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from lab.health_checks import assert_required_artifacts, log_event, run_and_require_success


def main() -> None:
    parser = argparse.ArgumentParser(description="CI demo gate for framework-first migration.")
    parser.add_argument("--profile", default="week1-demo")
    parser.add_argument("--output-root", default="outputs/demo-gate-ci")
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    command = [
        "bash",
        str(ROOT / "scripts/demo/run_demo_package.sh"),
        "fast",
        "--profile",
        args.profile,
        "--output-root",
        str(output_root),
    ]
    run_and_require_success(
        name="demo-package",
        command=command,
        cwd=ROOT,
        component="demo-gate",
    )
    artifacts = assert_required_artifacts(output_root=output_root, contract_name="demo_gate")
    empty = [path for path in artifacts if path.stat().st_size <= 0]
    if empty:
        rendered = ", ".join(str(path) for path in empty)
        raise RuntimeError(f"Demo gate failed: output artifacts are empty: {rendered}")
    print("NO CRITICAL FAILURES")
    log_event(component="demo-gate", severity="INFO", message="Demo gate PASS")


if __name__ == "__main__":
    main()
