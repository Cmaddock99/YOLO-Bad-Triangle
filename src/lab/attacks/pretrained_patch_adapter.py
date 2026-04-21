from importlib import import_module
import sys

sys.modules[__name__] = import_module("lab.plugins.extra.attacks.pretrained_patch_adapter")
