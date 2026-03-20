from __future__ import annotations

from lab.core.adapter_loader import AdapterLoader

from .base_defense import BaseDefense
from .plugin_registry import _registry

_loader: AdapterLoader[BaseDefense] = AdapterLoader("lab.defenses", "defense", _registry)

build_defense_plugin = _loader.build
list_available_defense_plugins = _loader.list_available
