from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.core.attacks.eot_pgd_adapter")
