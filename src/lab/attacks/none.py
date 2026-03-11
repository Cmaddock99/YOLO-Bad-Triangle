from __future__ import annotations

from pathlib import Path

from .base import Attack, register_attack


@register_attack("none", "identity")
class NoAttack(Attack):
    name = "none"

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        del output_dir, seed
        return source_dir

