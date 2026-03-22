from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


def sobel_edges(x: torch.Tensor) -> torch.Tensor:
    kernel_x = torch.tensor(
        [[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]]],
        device=x.device,
        dtype=x.dtype,
    ).unsqueeze(0)
    kernel_y = torch.tensor(
        [[[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]]],
        device=x.device,
        dtype=x.dtype,
    ).unsqueeze(0)
    channels = x.shape[1]
    kx = kernel_x.repeat(channels, 1, 1, 1)
    ky = kernel_y.repeat(channels, 1, 1, 1)
    gx = F.conv2d(x, kx, padding=1, groups=channels)
    gy = F.conv2d(x, ky, padding=1, groups=channels)
    return torch.sqrt(gx.pow(2) + gy.pow(2) + 1e-8)


@dataclass(frozen=True)
class CompositeLossWeights:
    pixel_weight: float = 1.0
    edge_weight: float = 0.15
    feature_weight: float = 0.1


def composite_denoising_loss(
    *,
    denoised: torch.Tensor,
    clean: torch.Tensor,
    yolo_feature_loss: torch.Tensor | None,
    weights: CompositeLossWeights,
) -> tuple[torch.Tensor, dict[str, float]]:
    pixel_loss = F.l1_loss(denoised, clean)
    edge_loss = F.l1_loss(sobel_edges(denoised), sobel_edges(clean))
    feature_loss = yolo_feature_loss if yolo_feature_loss is not None else denoised.new_zeros(())
    total = (
        (weights.pixel_weight * pixel_loss)
        + (weights.edge_weight * edge_loss)
        + (weights.feature_weight * feature_loss)
    )
    return total, {
        "pixel_loss": float(pixel_loss.detach().item()),
        "edge_loss": float(edge_loss.detach().item()),
        "feature_loss": float(feature_loss.detach().item()),
        "total_loss": float(total.detach().item()),
    }
