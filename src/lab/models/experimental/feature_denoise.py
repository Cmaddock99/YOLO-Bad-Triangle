from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


class FeatureDenoiseBlock(nn.Module):
    """Small residual denoiser intended for early YOLO feature maps."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.SiLU(),
            nn.Conv2d(channels, channels, kernel_size=1, bias=False),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


@dataclass(frozen=True)
class FeatureSpikeGate:
    min_robustness_gain: float = 0.01
    max_latency_increase_pct: float = 15.0
    max_maintainability_score: float = 3.0


def evaluate_spike_gate(
    *,
    baseline_map50: float,
    robust_map50: float,
    baseline_latency_ms: float,
    robust_latency_ms: float,
    maintainability_score: float,
    gate: FeatureSpikeGate,
) -> tuple[bool, dict[str, float]]:
    robustness_gain = robust_map50 - baseline_map50
    latency_increase_pct = (
        ((robust_latency_ms - baseline_latency_ms) / max(baseline_latency_ms, 1e-6)) * 100.0
    )
    passed = (
        robustness_gain >= gate.min_robustness_gain
        and latency_increase_pct <= gate.max_latency_increase_pct
        and maintainability_score <= gate.max_maintainability_score
    )
    return passed, {
        "robustness_gain": robustness_gain,
        "latency_increase_pct": latency_increase_pct,
        "maintainability_score": maintainability_score,
    }
