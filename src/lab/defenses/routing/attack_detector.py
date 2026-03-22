from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class AttackSignal:
    std_intensity: float
    high_freq_energy: float
    laplacian_var: float

    def as_dict(self) -> dict[str, float]:
        return {
            "std_intensity": self.std_intensity,
            "high_freq_energy": self.high_freq_energy,
            "laplacian_var": self.laplacian_var,
        }


def detect_attack_signal(image_bgr: np.ndarray) -> AttackSignal:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    blur = cv2.GaussianBlur(gray, (5, 5), sigmaX=1.2)
    high_freq = gray - blur
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    return AttackSignal(
        std_intensity=float(np.std(gray)),
        high_freq_energy=float(np.mean(np.abs(high_freq))),
        laplacian_var=float(np.var(lap)),
    )
