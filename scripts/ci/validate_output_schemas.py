#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from lab.health_checks import (
    log_event,
    validate_output_bundle,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate versioned output schemas for framework and compatibility artifacts."
    )
    parser.add_argument("--framework-run-dir", required=True)
    parser.add_argument("--legacy-compat-csv", required=True)
    args = parser.parse_args()

    run_dir = Path(args.framework_run_dir).expanduser().resolve()
    legacy_csv = Path(args.legacy_compat_csv).expanduser().resolve()
    validate_output_bundle(
        repo_root=ROOT,
        framework_run_dir=run_dir,
        legacy_compat_csv=legacy_csv,
    )
    log_event(component="schema-gate", severity="INFO", message="Schema validation PASS")


if __name__ == "__main__":
    main()
