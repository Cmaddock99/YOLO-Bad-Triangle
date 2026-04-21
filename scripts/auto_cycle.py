#!/usr/bin/env python3
"""Compatibility wrapper for ``scripts.automation.auto_cycle``.

New code should prefer ``scripts.automation.auto_cycle``. The public
``scripts/auto_cycle.py`` entrypoint remains supported.
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
    return import_module("scripts.automation.auto_cycle")


if __name__ == "__main__":
    _load_module().main()
else:
    sys.modules[__name__] = _load_module()
