from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["ExperimentRunner", "ExperimentSpec", "ExperimentRegistry", "ResolvedExperiment"]


def __getattr__(name: str) -> Any:
    if name in {"ExperimentRunner", "ExperimentSpec"}:
        module = import_module(".experiment_runner", __name__)
        return getattr(module, name)
    if name in {"ExperimentRegistry", "ResolvedExperiment"}:
        module = import_module(".experiment_registry", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

