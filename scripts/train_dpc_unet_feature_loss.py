#!/usr/bin/env python3
"""Compatibility wrapper for ``scripts.training.train_dpc_unet_feature_loss``.

New code should prefer ``scripts.training.train_dpc_unet_feature_loss``. The
public ``scripts/train_dpc_unet_feature_loss.py`` entrypoint remains supported.
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
    return import_module("scripts.training.train_dpc_unet_feature_loss")


def _run_main() -> None:
    result = _load_module().main()
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    _run_main()
else:
    sys.modules[__name__] = _load_module()
