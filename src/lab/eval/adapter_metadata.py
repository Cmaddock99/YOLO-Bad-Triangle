from __future__ import annotations

from typing import Any


def adapter_stage_metadata(defense: str, stage: str, **extra: Any) -> dict[str, Any]:
    return {
        "defense": defense,
        "stage": stage,
        **extra,
    }
