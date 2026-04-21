from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = ("lab.plugins.core.models.yolo_adapter",)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
