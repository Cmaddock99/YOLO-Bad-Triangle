from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = ("lab.plugins.extra.models.torchvision_adapter",)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
