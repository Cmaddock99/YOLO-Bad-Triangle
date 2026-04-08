from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

import numpy as np

from lab.eval.prediction_schema import PredictionRecord


class BaseDefense(ABC):
    """Framework-level defense interface with pre/post hooks."""

    name: str = "base_defense"
    is_trainable: bool = False

    @abstractmethod
    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        """Return `(processed_image, metadata)` before model inference."""

    @abstractmethod
    def postprocess(
        self,
        predictions: Sequence[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[Sequence[PredictionRecord], dict[str, Any]]:
        """Return `(processed_predictions, metadata)` after model inference."""

    def checkpoint_provenance(self) -> list[dict[str, str]]:
        """Return checkpoint records loaded by this defense.

        Each record: {"path": "<absolute path>", "sha256": "<hex digest>"}.
        Default returns empty list for defenses that load no checkpoints.
        """
        return []
