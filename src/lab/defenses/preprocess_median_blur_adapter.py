from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.core.defenses.preprocess_median_blur_adapter")
