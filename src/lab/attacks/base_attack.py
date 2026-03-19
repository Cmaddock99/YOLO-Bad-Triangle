from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseAttack(ABC):
    """Framework-level single-sample attack interface."""

    name: str = "base_attack"

    @abstractmethod
    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Return `(perturbed_image, metadata)` for one image."""
