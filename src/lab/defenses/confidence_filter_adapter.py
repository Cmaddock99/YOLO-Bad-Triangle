from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.extra.defenses.confidence_filter_adapter")
