from __future__ import annotations

from lab.core.plugin_registry import PluginRegistry

from .base_defense import BaseDefense

_registry: PluginRegistry[BaseDefense] = PluginRegistry("defense")

register_defense_plugin = _registry.register
get_defense_plugin = _registry.get
list_defense_plugins = _registry.list
