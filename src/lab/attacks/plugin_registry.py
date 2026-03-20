from __future__ import annotations

from lab.core.plugin_registry import PluginRegistry

from .base_attack import BaseAttack

_registry: PluginRegistry[BaseAttack] = PluginRegistry("attack")

register_attack_plugin = _registry.register
get_attack_plugin = _registry.get
list_attack_plugins = _registry.list
