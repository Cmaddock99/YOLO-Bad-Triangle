"""Compatibility shim for ``lab.plugins.extra.attacks.fgsm_center_mask_adapter``.

New code should prefer the moved plugin path. The public flat module path
remains supported.
"""
import sys
from importlib import import_module

sys.modules[__name__] = import_module("lab.plugins.extra.attacks.fgsm_center_mask_adapter")
