from __future__ import annotations

from importlib import import_module

ADAPTER_MODULES = (
    "lab.plugins.extra.attacks.cw_adapter",
    "lab.plugins.extra.attacks.fgsm_center_mask_adapter",
    "lab.plugins.extra.attacks.fgsm_edge_mask_adapter",
    "lab.plugins.extra.attacks.jpeg_attack_adapter",
    "lab.plugins.extra.attacks.pretrained_patch_adapter",
)

for module_name in ADAPTER_MODULES:
    import_module(module_name)
