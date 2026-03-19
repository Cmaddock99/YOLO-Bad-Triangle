#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_ALLOWED_ENV_FILES = {
    "src/lab/migration/runtime_policy.py",
    "scripts/ci/check_legacy_usage_enforcement.py",
}

_ALLOWED_POLICY_KEY_FILES = {
    "src/lab/migration/runtime_policy.py",
    "src/lab/migration/cycle_tracker.py",
    "configs/migration_runtime.yaml",
    "scripts/ci/check_legacy_policy_branch_guard.py",
    "scripts/ci/check_legacy_usage_enforcement.py",
}

_ALLOWED_RUNTIME_CALL_FILES = {
    "src/lab/migration/runtime_policy.py",
    "scripts/ci/check_legacy_usage_enforcement.py",
    "run_experiment.py",
    "scripts/run_framework.py",
    "src/lab/runners/cli.py",
    "src/lab/eval/metrics.py",
}

_PY_SKIP_DIRS = {".git", ".venv", "__pycache__", "outputs"}


def _allow_runtime_calls(path: Path, text: str) -> list[ast.Call]:
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "allow_legacy_runtime":
            calls.append(node)
    return calls


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if any(part in _PY_SKIP_DIRS for part in rel.parts):
            continue
        files.append(path)
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enforce legacy runtime access through allow_legacy_runtime() helper."
    )
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    repo_root = Path(args.root).expanduser().resolve()
    violations: list[str] = []

    for path in _iter_python_files(repo_root):
        rel = str(path.relative_to(repo_root))
        text = path.read_text(encoding="utf-8")

        if 'os.environ.get("USE_LEGACY_RUNTIME")' in text and rel not in _ALLOWED_ENV_FILES:
            violations.append(f"{rel}: direct USE_LEGACY_RUNTIME access forbidden")

        if '.get("use_legacy_runtime"' in text and rel not in _ALLOWED_POLICY_KEY_FILES:
            violations.append(f"{rel}: policy key use_legacy_runtime used outside policy/tracker")

        if re.search(r"\blegacy_cli\.main\(", text) and "allow_legacy_runtime(" not in text:
            violations.append(f"{rel}: direct legacy CLI dispatch missing allow_legacy_runtime() gate")

        runtime_calls = _allow_runtime_calls(path, text)
        if runtime_calls and rel not in _ALLOWED_RUNTIME_CALL_FILES:
            violations.append(f"{rel}: unexpected allow_legacy_runtime() usage")
        for call in runtime_calls:
            has_context = any(keyword.arg == "context" for keyword in call.keywords if keyword.arg is not None)
            if not has_context:
                violations.append(f"{rel}:{call.lineno}: allow_legacy_runtime() missing context= argument")

    if violations:
        joined = "\n".join(f"- {item}" for item in violations)
        raise RuntimeError(f"Legacy usage enforcement failed:\n{joined}")
    print("Legacy usage enforcement PASS")


if __name__ == "__main__":
    main()
