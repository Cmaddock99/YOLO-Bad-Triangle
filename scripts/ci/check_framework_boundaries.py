#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ATTACK_METRIC_LOGIC_DIR = ROOT / "src" / "lab" / "runners"
MIGRATION_DIR = ROOT / "src" / "lab" / "migration"
SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", "outputs", "tests"}
FORBIDDEN_MIGRATION_PATTERNS = [
    "build_attack_plugin(",
    "summarize_prediction_metrics(",
    "model.predict(",
]


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        files.append(path)
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enforce framework-only attack/metric logic boundaries.")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    repo_root = Path(args.root).expanduser().resolve()

    violations: list[str] = []
    for path in _iter_python_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root)
        in_migration = str(path).startswith(str(MIGRATION_DIR))
        if in_migration:
            for pattern in FORBIDDEN_MIGRATION_PATTERNS:
                if pattern in text:
                    violations.append(f"{rel}: adapters must not contain framework attack/metric logic '{pattern}'")

    if violations:
        raise RuntimeError("Framework boundary enforcement failed:\n" + "\n".join(f"- {item}" for item in violations))
    print("Framework boundary enforcement PASS")


if __name__ == "__main__":
    main()
