from __future__ import annotations

from lab.core.adapter_loader import AdapterLoader
from lab.core.plugin_registry import PluginRegistry

from .base_attack import BaseAttack

_registry: PluginRegistry[BaseAttack] = PluginRegistry("attack")

# Adapters self-register via: @register_attack_plugin("fgsm")
register_attack_plugin = _registry.register
get_attack_plugin = _registry.get
list_attack_plugins = _registry.list

# Runner uses these (triggers lazy adapter discovery on first call)
_loader: AdapterLoader[BaseAttack] = AdapterLoader(
    ("lab.plugins.core.attacks", "lab.plugins.extra.attacks"),
    "attack",
    _registry,
    core_package_names=("lab.plugins.core.attacks",),
    extra_package_names=("lab.plugins.extra.attacks",),
)
build_attack_plugin = _loader.build
list_available_attack_plugins = _loader.list_available
