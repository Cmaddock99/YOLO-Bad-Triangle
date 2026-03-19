#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def _python_files(root: Path) -> list[Path]:
    return sorted([path for path in root.rglob("*.py") if ".venv" not in path.parts and ".git" not in path.parts])


def _count_references(root: Path, target_filename: str) -> int:
    total = 0
    for path in _python_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        total += text.count(target_filename)
    return total


def _sample_dependency_hints(root: Path, target_filename: str, limit: int = 3) -> list[str]:
    hints: list[str] = []
    for path in _python_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if target_filename in text:
            hints.append(str(path.relative_to(root)))
        if len(hints) >= limit:
            break
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(description="Report potentially unused migration compatibility wrappers.")
    parser.add_argument("--output", default="outputs/migration_state/cleanup_candidates.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        "run_experiment.py",
        "scripts/run_framework.py",
        "scripts/run_unified.py",
    ]
    lines = [
        "# Wrapper Cleanup Candidates",
        "",
        "This report flags wrappers with low code references for retirement review.",
        "",
        "| Wrapper | Owner | Reference count | Candidate | Safe removal confidence | Dependency hints |",
        "|---|---|---:|---|---|---|",
    ]
    owner_map = {
        "run_experiment.py": "runtime",
        "scripts/run_framework.py": "runtime",
        "scripts/run_unified.py": "platform",
    }
    for item in candidates:
        count = _count_references(repo_root, item)
        candidate = "yes" if count <= 1 else "no"
        if count <= 1:
            confidence = "high"
        elif count <= 3:
            confidence = "medium"
        else:
            confidence = "low"
        hints = _sample_dependency_hints(repo_root, item)
        hints_text = ", ".join(f"`{hint}`" for hint in hints) if hints else "none"
        lines.append(
            f"| `{item}` | {owner_map.get(item, 'unknown')} | {count} | {candidate} | {confidence} | {hints_text} |"
        )

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote cleanup candidate report: {output_path}")


if __name__ == "__main__":
    main()
