from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = (
    "lab.plugins.core.attacks.blur_adapter",
    "lab.plugins.core.attacks.deepfool_adapter",
    "lab.plugins.core.attacks.dispersion_reduction_adapter",
    "lab.plugins.core.attacks.eot_pgd_adapter",
    "lab.plugins.core.attacks.fgsm_adapter",
    "lab.plugins.core.attacks.pgd_adapter",
    "lab.plugins.core.attacks.square_adapter",
)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
