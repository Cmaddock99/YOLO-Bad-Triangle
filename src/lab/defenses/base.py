from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class Defense(ABC):
    name: str = "defense"

    @abstractmethod
    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        """Applies defense preprocessing and returns output directory."""

