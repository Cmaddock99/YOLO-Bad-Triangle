from __future__ import annotations

from lab.core.plugin_registry import PluginRegistry

from .base_model import BaseModel

_registry: PluginRegistry[BaseModel] = PluginRegistry("model")

register_model = _registry.register
get_model_class = _registry.get
list_registered_models = _registry.list
