from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = (
    "lab.plugins.extra.defenses.confidence_filter_adapter",
    "lab.plugins.extra.defenses.preprocess_dpc_unet_adapter",
    "lab.plugins.extra.defenses.preprocess_random_resize_adapter",
)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
