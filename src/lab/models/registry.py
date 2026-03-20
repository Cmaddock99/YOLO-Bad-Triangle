from __future__ import annotations

from lab.core.adapter_loader import AdapterLoader

from .base_model import BaseModel
from .plugin_registry import _registry

_loader: AdapterLoader[BaseModel] = AdapterLoader("lab.models", "model", _registry)

build_model = _loader.build
list_available_models = _loader.list_available
