from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch

from lab.config.contracts import (
    ATTACK_OBJECTIVE_CLASS_HIDE,
    ATTACK_OBJECTIVE_MODES,
    ATTACK_OBJECTIVE_TARGET_CLASS,
    ATTACK_OBJECTIVE_UNTARGETED,
)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _normalize_roi(roi: Any) -> tuple[float, float, float, float] | None:
    if roi is None:
        return None
    if isinstance(roi, str):
        parts = [part.strip() for part in roi.split(",") if part.strip()]
        if len(parts) != 4:
            raise ValueError("attack ROI must contain 4 values: x,y,w,h")
        values = [float(part) for part in parts]
    elif isinstance(roi, (list, tuple)) and len(roi) == 4:
        values = [float(v) for v in roi]
    else:
        raise ValueError("attack ROI must be a list/tuple/string with 4 normalized values.")
    x, y, w, h = values
    if min(x, y, w, h) < 0.0 or max(x, y, w, h) > 1.0:
        raise ValueError("attack ROI values must be normalized in [0, 1].")
    if w <= 0.0 or h <= 0.0:
        raise ValueError("attack ROI width/height must be > 0.")
    return x, y, w, h


@dataclass(frozen=True)
class AttackObjective:
    mode: str = ATTACK_OBJECTIVE_UNTARGETED
    target_class: int | None = None
    preserve_weight: float = 0.25
    roi: tuple[float, float, float, float] | None = None

    @classmethod
    def from_params(cls, params: dict[str, Any]) -> "AttackObjective":
        mode = str(params.get("objective_mode", ATTACK_OBJECTIVE_UNTARGETED)).strip().lower()
        if mode not in ATTACK_OBJECTIVE_MODES:
            raise ValueError(
                f"Unsupported objective_mode '{mode}'. Supported: {', '.join(ATTACK_OBJECTIVE_MODES)}"
            )
        target_class = _optional_int(params.get("target_class"))
        preserve_weight = float(params.get("preserve_weight", 0.25))
        roi = _normalize_roi(params.get("attack_roi"))

        if mode in {ATTACK_OBJECTIVE_TARGET_CLASS, ATTACK_OBJECTIVE_CLASS_HIDE} and target_class is None:
            raise ValueError(f"objective_mode '{mode}' requires target_class.")
        if preserve_weight < 0.0:
            raise ValueError("preserve_weight must be >= 0.")
        return cls(mode=mode, target_class=target_class, preserve_weight=preserve_weight, roi=roi)

    @classmethod
    def from_kwargs(
        cls,
        *,
        mode: str = ATTACK_OBJECTIVE_UNTARGETED,
        target_class: int | None = None,
        preserve_weight: float = 0.25,
        attack_roi: tuple[float, float, float, float] | list[float] | str | None = None,
    ) -> "AttackObjective":
        return cls.from_params(
            {
                "objective_mode": mode,
                "target_class": target_class,
                "preserve_weight": preserve_weight,
                "attack_roi": attack_roi,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "objective_mode": self.mode,
            "target_class": self.target_class,
            "preserve_weight": self.preserve_weight,
            "attack_roi": list(self.roi) if self.roi is not None else None,
        }
        return payload

    def gradient_mask(self, *, height: int, width: int, device: torch.device) -> torch.Tensor | None:
        if self.roi is None:
            return None
        x, y, w, h = self.roi
        left = max(0, min(width, int(round(x * width))))
        top = max(0, min(height, int(round(y * height))))
        right = max(left + 1, min(width, int(round((x + w) * width))))
        bottom = max(top + 1, min(height, int(round((y + h) * height))))
        mask = torch.zeros((1, 1, height, width), device=device, dtype=torch.float32)
        mask[:, :, top:bottom, left:right] = 1.0
        return mask
