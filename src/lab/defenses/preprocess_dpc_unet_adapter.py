"""Compatibility shim for ``lab.plugins.extra.defenses.preprocess_dpc_unet_adapter``.

New code should prefer the moved plugin path. The public flat module path
remains supported.
"""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("lab.plugins.extra.defenses.preprocess_dpc_unet_adapter")
