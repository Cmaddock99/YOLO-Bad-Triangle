from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from lab.eval.prediction_schema import PredictionRecord


class BaseModel(ABC):
    """Framework-level model interface for normalized inference/validation."""

    name: str = "base_model"

    @abstractmethod
    def load(self) -> None:
        """Load model resources and make the model ready for use."""

    @abstractmethod
    def predict(self, images: Iterable[Path], **kwargs: Any) -> Sequence[PredictionRecord]:
        """Run inference and return predictions in framework schema."""

    @abstractmethod
    def validate(self, dataset: Path | str, **kwargs: Any) -> dict[str, Any]:
        """Run validation and return framework-level metric payload."""
