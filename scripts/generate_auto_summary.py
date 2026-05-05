#!/usr/bin/env python3
"""Compatibility wrapper for ``scripts.reporting.generate_auto_summary``.

New code should prefer ``scripts.reporting.generate_auto_summary``. The public
``scripts/generate_auto_summary.py`` entrypoint remains supported.
"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys


def _load_module():
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return import_module("scripts.reporting.generate_auto_summary")


def _run_main() -> None:
    result = _load_module().main()
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    _run_main()
else:
    sys.modules[__name__] = _load_module()
