from __future__ import annotations

from typing import Any

from .base import Attack
from .blur import GaussianBlurAttack
from .noise import GaussianNoiseAttack
from .none import NoAttack


def build_attack(name: str, params: dict[str, Any] | None = None) -> Attack:
    params = params or {}
    key = name.lower()

    if key in {"none", "identity"}:
        return NoAttack()
    if key in {"blur", "gaussian_blur"}:
        return GaussianBlurAttack(**params)
    if key in {"gaussian_noise", "noise"}:
        return GaussianNoiseAttack(**params)

    raise ValueError(f"Unsupported attack '{name}'.")

