#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION_DIR = ROOT / "src" / "lab" / "migration"
SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", "outputs", "tests"}


class ForbiddenCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.matches: list[tuple[str, int]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        forbidden = {"build_attack_plugin", "summarize_prediction_metrics"}
        if name in forbidden:
            self.matches.append((name, node.lineno))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "predict" and isinstance(node.func.value, ast.Name) and node.func.value.id == "model":
                self.matches.append(("model.predict", node.lineno))
        self.generic_visit(node)


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        files.append(path)
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AST-level enforcement: adapters must not duplicate framework attack/metrics logic."
    )
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    repo_root = Path(args.root).expanduser().resolve()
    violations: list[str] = []
    for path in _iter_python_files(repo_root):
        if not str(path).startswith(str(MIGRATION_DIR)):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            violations.append(f"{path.relative_to(repo_root)}: syntax parse failure: {exc}")
            continue
        visitor = ForbiddenCallVisitor()
        visitor.visit(tree)
        for name, lineno in visitor.matches:
            violations.append(f"{path.relative_to(repo_root)}:{lineno} forbidden adapter call '{name}'")

    if violations:
        raise RuntimeError(
            "Framework duplication AST enforcement failed:\n" + "\n".join(f"- {item}" for item in violations)
        )
    print("Framework duplication AST enforcement PASS")


if __name__ == "__main__":
    main()
