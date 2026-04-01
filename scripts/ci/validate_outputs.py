#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from lab.health_checks import assert_required_artifacts, log_event, validate_output_bundle


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate framework output artifacts and schemas."
    )
    parser.add_argument("--output-root", required=True, help="Run output directory.")
    parser.add_argument(
        "--contract-name",
        default="framework_run",
        help="Artifact contract to enforce (default: framework_run).",
    )
    parser.add_argument("--framework-run-dir", help="Framework run dir for schema validation.")
    parser.add_argument("--legacy-compat-csv", help="Legacy compat CSV for schema validation.")
    parser.add_argument(
        "--require-schema",
        action="store_true",
        help="Require schema validation bundle inputs; fail if args are missing.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    assert_required_artifacts(output_root=output_root, contract_name=args.contract_name)
    log_event(component="artifact-gate", severity="INFO", message="Artifact gate PASS")

    if args.require_schema and (not args.framework_run_dir or not args.legacy_compat_csv):
        raise SystemExit(
            "--require-schema needs both --framework-run-dir and --legacy-compat-csv."
        )

    if args.framework_run_dir and args.legacy_compat_csv:
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
