from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.core.attacks.dispersion_reduction_adapter")
