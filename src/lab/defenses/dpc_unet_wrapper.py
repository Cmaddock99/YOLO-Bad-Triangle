from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import torch
from torch import Tensor, nn
import torch.nn.functional as F


def sinusoidal_timestep_embedding(timesteps: Tensor, dim: int = 64) -> Tensor:
    """Create sinusoidal timestep embeddings with shape [B, dim]."""
    if timesteps.ndim == 0:
        timesteps = timesteps.unsqueeze(0)
    timesteps = timesteps.float()
    half = dim // 2
    if half == 0:
        return timesteps.unsqueeze(-1)
    device = timesteps.device
    exponent = torch.arange(half, device=device, dtype=torch.float32) / max(half - 1, 1)
    freq = torch.exp(-torch.log(torch.tensor(10000.0, device=device)) * exponent)
    args = timesteps.unsqueeze(-1) * freq.unsqueeze(0)
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


def _num_groups(channels: int) -> int:
    for groups in (8, 4, 2, 1):
        if channels % groups == 0:
            return groups
    return 1


class DPCResidualBlock(nn.Module):
    """U-Net block with simple time conditioning."""

    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.mlp = nn.Sequential(nn.SiLU(), nn.Linear(64, out_ch))
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.norm1 = nn.GroupNorm(_num_groups(out_ch), out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.norm2 = nn.GroupNorm(_num_groups(out_ch), out_ch)

    def forward(self, x: Tensor, t_embed: Tensor) -> Tensor:
        h = self.conv1(x)
        h = h + self.mlp(t_embed).unsqueeze(-1).unsqueeze(-1)
        h = F.silu(self.norm1(h))
        h = self.conv2(h)
        h = F.silu(self.norm2(h))
        return h


class DPCUNet(nn.Module):
    """Best-effort architecture inferred from dpc_unet_final_golden checkpoint keys."""

    def __init__(self) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(nn.SiLU(), nn.Linear(64, 64))
        self.down1 = DPCResidualBlock(3, 32)
        self.down2 = DPCResidualBlock(32, 64)
        self.bottleneck = DPCResidualBlock(64, 128)
        self.up2_conv = nn.Sequential(nn.Conv2d(128, 256, kernel_size=1), nn.PixelShuffle(2))
        self.up2_block = DPCResidualBlock(128, 64)
        self.up1_conv = nn.Sequential(nn.Conv2d(64, 128, kernel_size=1), nn.PixelShuffle(2))
        self.up1_block = DPCResidualBlock(64, 32)
        self.final = nn.Conv2d(32, 3, kernel_size=1)

    def _as_timestep_tensor(self, timestep: int | float | Tensor, batch: int, device: torch.device) -> Tensor:
        if isinstance(timestep, Tensor):
            if timestep.ndim == 0:
                return timestep.to(device=device).repeat(batch)
            if timestep.numel() == 1:
                return timestep.to(device=device).reshape(1).repeat(batch)
            if timestep.shape[0] != batch:
                raise ValueError(
                    f"Timestep tensor first dimension must match batch. got={timestep.shape[0]} batch={batch}"
                )
            return timestep.to(device=device)
        return torch.full((batch,), float(timestep), device=device, dtype=torch.float32)

    def forward(self, x: Tensor, timestep: int | float | Tensor = 100) -> Tensor:
        batch = x.shape[0]
        t = self._as_timestep_tensor(timestep, batch=batch, device=x.device)
        t_embed = self.time_mlp(sinusoidal_timestep_embedding(t, dim=64))

        x1 = self.down1(x, t_embed)
        x2 = self.down2(F.avg_pool2d(x1, kernel_size=2), t_embed)
        x3 = self.bottleneck(F.avg_pool2d(x2, kernel_size=2), t_embed)

        up2 = self.up2_conv(x3)
        if up2.shape[-2:] != x2.shape[-2:]:
            up2 = F.interpolate(up2, size=x2.shape[-2:], mode="bilinear", align_corners=False)
        up2 = self.up2_block(torch.cat([up2, x2], dim=1), t_embed)

        up1 = self.up1_conv(up2)
        if up1.shape[-2:] != x1.shape[-2:]:
            up1 = F.interpolate(up1, size=x1.shape[-2:], mode="bilinear", align_corners=False)
        up1 = self.up1_block(torch.cat([up1, x1], dim=1), t_embed)
        return self.final(up1)


def load_checkpoint_state_dict(checkpoint_path: str | Path) -> dict[str, Tensor]:
    loaded = torch.load(str(checkpoint_path), map_location="cpu", weights_only=True)
    if not isinstance(loaded, dict):
        raise TypeError(f"Expected checkpoint state_dict mapping, got {type(loaded).__name__}.")
    if not loaded:
        raise ValueError("Checkpoint state_dict is empty.")
    for key, value in loaded.items():
        if not isinstance(key, str):
            raise TypeError(f"Checkpoint contains non-string key: {key!r}")
        if not isinstance(value, Tensor):
            raise TypeError(f"Checkpoint key '{key}' does not map to a tensor.")
    return loaded


@dataclass
class StrictLoadReport:
    strict_passed: bool
    missing_keys: list[str]
    unexpected_keys: list[str]
    error_message: str | None


def strict_load_with_report(model: nn.Module, state_dict: dict[str, Tensor]) -> StrictLoadReport:
    """Run a strict load and capture key-level details for adapter error reporting."""
    try:
        incompatible = model.load_state_dict(state_dict, strict=True)
        return StrictLoadReport(
            strict_passed=True,
            missing_keys=list(incompatible.missing_keys),
            unexpected_keys=list(incompatible.unexpected_keys),
            error_message=None,
        )
    except RuntimeError as exc:
        model_keys = set(model.state_dict().keys())
        loaded_keys = set(state_dict.keys())
        return StrictLoadReport(
            strict_passed=False,
            missing_keys=sorted(model_keys - loaded_keys),
            unexpected_keys=sorted(loaded_keys - model_keys),
            error_message=str(exc),
        )


@dataclass(frozen=True)
class WrapperInputConfig:
    color_order: str = "rgb"  # "rgb" or "bgr"
    scaling: str = "zero_one"  # "zero_one" or "minus_one_one"
    normalize: bool = False
    mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: tuple[float, float, float] = (0.229, 0.224, 0.225)

    def validate(self) -> None:
        if self.color_order not in {"rgb", "bgr"}:
            raise ValueError(f"Unsupported color_order: {self.color_order}")
        if self.scaling not in {"zero_one", "minus_one_one"}:
            raise ValueError(f"Unsupported scaling: {self.scaling}")
        if any(value <= 0 for value in self.std):
            raise ValueError("std values must be positive.")


def image_bgr_to_model_tensor(image_bgr: np.ndarray, cfg: WrapperInputConfig) -> Tensor:
    cfg.validate()
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("Expected HxWx3 BGR image.")
    image = image_bgr
    if cfg.color_order == "rgb":
        image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    arr = image.astype(np.float32) / 255.0
    if cfg.scaling == "minus_one_one":
        arr = (arr * 2.0) - 1.0
    if cfg.normalize:
        mean = np.asarray(cfg.mean, dtype=np.float32).reshape(1, 1, 3)
        std = np.asarray(cfg.std, dtype=np.float32).reshape(1, 1, 3)
        arr = (arr - mean) / std
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).contiguous()
    return tensor


def model_tensor_to_image_bgr(tensor: Tensor, cfg: WrapperInputConfig) -> np.ndarray:
    cfg.validate()
    if tensor.ndim != 4 or tensor.shape[0] != 1 or tensor.shape[1] != 3:
        raise ValueError("Expected tensor shape [1, 3, H, W].")
    arr = tensor.squeeze(0).permute(1, 2, 0).detach().cpu().numpy().astype(np.float32)
    if cfg.normalize:
        mean = np.asarray(cfg.mean, dtype=np.float32).reshape(1, 1, 3)
        std = np.asarray(cfg.std, dtype=np.float32).reshape(1, 1, 3)
        arr = (arr * std) + mean
    if cfg.scaling == "minus_one_one":
        arr = (arr + 1.0) / 2.0
    arr = np.clip(arr, 0.0, 1.0)
    image = np.rint(arr * 255.0).astype(np.uint8)
    if cfg.color_order == "rgb":
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image


@torch.no_grad()
def run_wrapper_on_bgr_image(
    image_bgr: np.ndarray,
    model: DPCUNet,
    *,
    timestep: int | float | Tensor = 100,
    cfg: WrapperInputConfig,
    device: str = "cpu",
) -> tuple[np.ndarray, dict[str, float | bool | str]]:
    tensor = image_bgr_to_model_tensor(image_bgr, cfg=cfg).to(device=device)
    model = model.to(device=device)
    model.eval()
    output = model(tensor, timestep=timestep)
    finite = bool(torch.isfinite(output).all().item())
    stats = {
        "finite": finite,
        "tensor_min": float(output.min().item()),
        "tensor_max": float(output.max().item()),
        "tensor_mean": float(output.mean().item()),
        "tensor_std": float(output.std(unbiased=False).item()),
    }
    image_out = model_tensor_to_image_bgr(output, cfg=cfg)
    return image_out, stats


@torch.no_grad()
def run_wrapper_multipass_on_bgr_image(
    image_bgr: np.ndarray,
    model: DPCUNet,
    *,
    timestep_schedule: list[float],
    cfg: WrapperInputConfig,
    device: str = "cpu",
) -> tuple[np.ndarray, dict[str, float | bool | str]]:
    """Run DPC-UNet multiple times at decreasing timesteps.

    Each pass feeds its output into the next, progressively cleaning
    adversarial perturbations from coarse (high timestep) to fine (low timestep).
    """
    if not timestep_schedule:
        raise ValueError("timestep_schedule must be a non-empty list.")
    model = model.to(device=device)
    model.eval()
    current = image_bgr_to_model_tensor(image_bgr, cfg=cfg).to(device=device)
    output = current  # initialise so final_output is defined even if schedule is empty
    for t in timestep_schedule:
        output = model(current, timestep=float(t))
        # NaN guard: catch non-finite output before the round-trip clamp.
        arr = output.squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.float32)
        if not np.isfinite(arr).all():
            raise RuntimeError(f"DPC-UNet produced non-finite output at timestep {t}")
        # Re-encode via uint8 round-trip to stay in valid image space between passes.
        if cfg.normalize:
            mean = np.asarray(cfg.mean, dtype=np.float32).reshape(1, 1, 3)
            std = np.asarray(cfg.std, dtype=np.float32).reshape(1, 1, 3)
            arr = (arr * std) + mean
        if cfg.scaling == "minus_one_one":
            arr = (arr + 1.0) / 2.0
        arr = np.clip(arr, 0.0, 1.0)
        intermediate = np.rint(arr * 255.0).astype(np.uint8)
        if cfg.color_order == "rgb":
            intermediate = cv2.cvtColor(intermediate, cv2.COLOR_RGB2BGR)
        current = image_bgr_to_model_tensor(intermediate, cfg=cfg).to(device=device)
    # Use the output from the last loop iteration — no extra model call after the schedule.
    final_output = output
    finite = bool(torch.isfinite(final_output).all().item())
    stats = {
        "finite": finite,
        "tensor_min": float(final_output.min().item()),
        "tensor_max": float(final_output.max().item()),
        "tensor_mean": float(final_output.mean().item()),
        "tensor_std": float(final_output.std(unbiased=False).item()),
        "passes": len(timestep_schedule),
    }
    image_out = model_tensor_to_image_bgr(final_output, cfg=cfg)
    return image_out, stats


def sharpen_image(image_bgr: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Apply unsharp masking to recover edges softened by denoising.

    alpha controls sharpening strength (0.0 = no-op, 1.0 = strong).
    """
    if alpha <= 0.0:
        return image_bgr
    blurred = cv2.GaussianBlur(image_bgr, (0, 0), sigmaX=1.0)
    return cv2.addWeighted(image_bgr, 1.0 + alpha, blurred, -alpha, 0)
