from __future__ import annotations

from lab.core.adapter_loader import AdapterLoader
from lab.core.plugin_registry import PluginRegistry

from .base_defense import BaseDefense

_registry: PluginRegistry[BaseDefense] = PluginRegistry("defense")

# Adapters self-register via: @register_defense_plugin("none")
register_defense_plugin = _registry.register
get_defense_plugin = _registry.get
list_defense_plugins = _registry.list

# Runner uses these (triggers lazy adapter discovery on first call)
_loader: AdapterLoader[BaseDefense] = AdapterLoader(
    ("lab.plugins.core.defenses", "lab.plugins.extra.defenses"),
    "defense",
    _registry,
    core_package_names=("lab.plugins.core.defenses",),
    extra_package_names=("lab.plugins.extra.defenses",),
)
build_defense_plugin = _loader.build
list_available_defense_plugins = _loader.list_available
