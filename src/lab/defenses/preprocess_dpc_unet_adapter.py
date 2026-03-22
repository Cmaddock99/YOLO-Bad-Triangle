from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lab.eval.prediction_utils import adapter_stage_metadata
from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    load_checkpoint_state_dict,
    run_wrapper_multipass_on_bgr_image,
    run_wrapper_on_bgr_image,
    sharpen_image,
)
from .framework_registry import register_defense_plugin
from .routing import RoutingThresholds, choose_route, detect_attack_signal


@dataclass
@register_defense_plugin("preprocess_dpc_unet", "c_dog")
class PreprocessDPCUNetDefenseAdapter(BaseDefense):
    """Provisional wrapper-based preprocessing defense with strict safety checks."""

    checkpoint_path: str = field(
        default_factory=lambda: os.environ.get("DPC_UNET_CHECKPOINT_PATH", "")
    )
    timestep: float = 50.0
    # Multi-pass: comma-separated timesteps e.g. "75,50,25". When set,
    # overrides `timestep` and runs the model once per value in sequence.
    timestep_schedule: str = ""
    # Sharpening applied after DPC-UNet output (0.0 = disabled, 0.5 = moderate).
    sharpen_alpha: float = 0.0
    routing_enabled: bool = False
    attack_hint: str = ""
    low_noise_hf: float = 0.03
    strong_hf: float = 0.08
    strong_laplacian: float = 0.02
    color_order: str = "bgr"
    scaling: str = "zero_one"
    normalize: bool = True
    device: str = "cpu"
    name: str = "c_dog"
    _model: DPCUNet = field(init=False, repr=False)
    _cfg: WrapperInputConfig = field(init=False, repr=False)
    _loaded: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._cfg = WrapperInputConfig(
            color_order=self.color_order,
            scaling=self.scaling,
            normalize=bool(self.normalize),
        )
        self._cfg.validate()

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if not self.checkpoint_path:
            raise ValueError(
                "DPC-UNet checkpoint path is not set. "
                "Pass checkpoint_path= when building the plugin, "
                "or set the DPC_UNET_CHECKPOINT_PATH environment variable."
            )
        checkpoint = Path(self.checkpoint_path).expanduser().resolve()
        if not checkpoint.exists():
            raise FileNotFoundError(f"DPC-UNet checkpoint not found: {checkpoint}")
        model = DPCUNet()
        state_dict = load_checkpoint_state_dict(checkpoint)
        model.load_state_dict(state_dict, strict=True)
        model.eval()
        self._model = model
        self._loaded = True

    def _parse_timestep_schedule(self) -> list[float] | None:
        if not self.timestep_schedule.strip():
            return None
        return [float(t.strip()) for t in self.timestep_schedule.split(",") if t.strip()]

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        runtime_attack_hint = str(kwargs.get("attack_hint", "") or self.attack_hint)
        self._ensure_loaded()
        signal = detect_attack_signal(image)
        route = "cdog_only"
        if self.routing_enabled:
            route = choose_route(
                signal=signal,
                attack_hint=runtime_attack_hint,
                thresholds=RoutingThresholds(
                    low_noise_hf=float(self.low_noise_hf),
                    strong_hf=float(self.strong_hf),
                    strong_laplacian=float(self.strong_laplacian),
                ),
            )
        if route == "passthrough":
            output = image.copy()
            stats = {
                "finite": bool(np.isfinite(output).all()),
                "tensor_min": float(output.min()),
                "tensor_max": float(output.max()),
                "tensor_mean": float(output.mean()),
                "tensor_std": float(output.std()),
            }
            return output, adapter_stage_metadata(
                "preprocess_dpc_unet",
                "preprocess",
                checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
                routing_enabled=bool(self.routing_enabled),
                routing_route=route,
                attack_hint=runtime_attack_hint or None,
                **signal.as_dict(),
                finite=bool(stats["finite"]),
                tensor_min=float(stats["tensor_min"]),
                tensor_max=float(stats["tensor_max"]),
                tensor_mean=float(stats["tensor_mean"]),
                tensor_std=float(stats["tensor_std"]),
            )
        schedule = self._parse_timestep_schedule()
        if schedule:
            output, stats = run_wrapper_multipass_on_bgr_image(
                image,
                self._model,
                timestep_schedule=schedule,
                cfg=self._cfg,
                device=self.device,
            )
        else:
            output, stats = run_wrapper_on_bgr_image(
                image,
                self._model,
                timestep=float(self.timestep),
                cfg=self._cfg,
                device=self.device,
            )
        if not bool(stats["finite"]):
            raise RuntimeError("DPC-UNet defense produced non-finite output.")
        if output.shape != image.shape:
            raise RuntimeError(
                f"DPC-UNet defense changed image shape: input={image.shape} output={output.shape}"
            )
        if self.sharpen_alpha > 0.0:
            output = sharpen_image(output, alpha=float(self.sharpen_alpha))
        return output, adapter_stage_metadata(
            "preprocess_dpc_unet",
            "preprocess",
            checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
            timestep=float(self.timestep),
            timestep_schedule=self.timestep_schedule or None,
            sharpen_alpha=float(self.sharpen_alpha),
            color_order=self._cfg.color_order,
            scaling=self._cfg.scaling,
            normalize=self._cfg.normalize,
            finite=bool(stats["finite"]),
            tensor_min=float(stats["tensor_min"]),
            tensor_max=float(stats["tensor_max"]),
            tensor_mean=float(stats["tensor_mean"]),
            tensor_std=float(stats["tensor_std"]),
        )

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            "preprocess_dpc_unet",
            "postprocess",
            note="identity_postprocess",
        )
