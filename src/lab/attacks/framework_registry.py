from __future__ import annotations

from lab.core.adapter_loader import AdapterLoader

from .base_attack import BaseAttack
from .plugin_registry import _registry

_loader: AdapterLoader[BaseAttack] = AdapterLoader("lab.attacks", "attack", _registry)

build_attack_plugin = _loader.build
list_available_attack_plugins = _loader.list_available
