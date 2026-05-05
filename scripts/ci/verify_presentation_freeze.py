#!/usr/bin/env python3
"""Verify frozen presentation artifact directories exist and contain key files.

See outputs/presentation_frozen/STATUS.md and docs/superpowers/plans/2026-04-30-presentation-readiness.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FROZEN = REPO / "outputs" / "presentation_frozen"

REQUIRED_FILES = (
    FROZEN / "STATUS.md",
    FROZEN / "core_demo" / "demo_manifest.json",
    FROZEN / "auto_cycle" / "cycle_report.md",
)


def main() -> int:
    missing = [p for p in REQUIRED_FILES if not p.is_file()]
    if missing:
        print("verify_presentation_freeze: missing required files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path.relative_to(REPO)}", file=sys.stderr)
        return 1
    print("verify_presentation_freeze: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
