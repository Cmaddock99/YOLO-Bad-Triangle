from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = (
    "lab.plugins.core.defenses.none_adapter",
    "lab.plugins.core.defenses.preprocess_bitdepth_adapter",
    "lab.plugins.core.defenses.preprocess_jpeg_adapter",
    "lab.plugins.core.defenses.preprocess_median_blur_adapter",
)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
