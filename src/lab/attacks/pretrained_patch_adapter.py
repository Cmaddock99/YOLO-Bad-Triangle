"""Compatibility shim for ``lab.plugins.extra.attacks.pretrained_patch_adapter``.

New code should prefer the moved plugin path. The public flat module path
remains supported.
"""
from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.extra.attacks.pretrained_patch_adapter")
