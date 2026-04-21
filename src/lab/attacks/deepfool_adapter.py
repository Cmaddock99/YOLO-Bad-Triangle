from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.core.attacks.deepfool_adapter")
