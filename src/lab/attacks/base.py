from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class Attack(ABC):
    name: str = "attack"

    @abstractmethod
    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        """Transforms source images and returns the output directory."""

