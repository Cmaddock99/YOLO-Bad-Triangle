from __future__ import annotations

from typing import Any

from .base import Defense
from .median_blur import MedianBlurDefense
from .none import NoDefense


def build_defense(name: str, params: dict[str, Any] | None = None) -> Defense:
    params = params or {}
    key = name.lower()

    if key in {"none", "identity"}:
        return NoDefense()
    if key in {"median_blur", "median"}:
        return MedianBlurDefense(**params)

    raise ValueError(f"Unsupported defense '{name}'.")

