#!/usr/bin/env python3
"""Compatibility wrapper for ``scripts.automation.cleanup_stale_runs``.

New code should prefer ``scripts.automation.cleanup_stale_runs``. The public
``scripts/cleanup_stale_runs.py`` entrypoint remains supported.
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
    return import_module("scripts.automation.cleanup_stale_runs")


if __name__ == "__main__":
    raise SystemExit(_load_module().main())
else:
    sys.modules[__name__] = _load_module()
