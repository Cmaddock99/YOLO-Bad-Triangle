#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from lab.health_checks import assert_required_artifacts, log_event


def main() -> None:
    parser = argparse.ArgumentParser(description="CI Artifact gate for migration outputs.")
    parser.add_argument(
        "--output-root",
        required=True,
        help="Directory expected to contain legacy-compatible artifacts.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    assert_required_artifacts(output_root=output_root, contract_name="demo_gate")
    log_event(component="artifact-gate", severity="INFO", message="Artifact gate PASS")


if __name__ == "__main__":
    main()
