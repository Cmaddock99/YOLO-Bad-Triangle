#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PATHS = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATE.md",
    ROOT / "scripts" / "demo" / "README.md",
]

FORBIDDEN_PATTERNS = [
    r"python\s+run_experiment_api\.py\s",
    r"legacy-first",
    r"legacy runtime default",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail if operator docs contain legacy-first/non-framework instructions.")
    parser.add_argument("--paths", nargs="*", default=[str(path) for path in DOC_PATHS])
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            violations.append(f"{path}: missing required documentation file")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                violations.append(f"{path}: forbidden pattern matched /{pattern}/")
        if "scripts/run_unified.py" not in text and "run_experiment.py" not in text:
            violations.append(f"{path}: missing framework operator command guidance")

    if violations:
        raise RuntimeError("Operator docs enforcement failed:\n" + "\n".join(f"- {item}" for item in violations))
    print("Operator docs enforcement PASS")


if __name__ == "__main__":
    main()
