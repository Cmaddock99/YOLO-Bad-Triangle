from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lab.eval.adapter_metadata import adapter_stage_metadata
from lab.eval.prediction_schema import PredictionRecord
from .base_defense import BaseDefense
from .dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    load_checkpoint_state_dict,
    run_wrapper_on_bgr_image,
)
from .framework_registry import register_defense_plugin


@dataclass
@register_defense_plugin("preprocess_dpc_unet", "c_dog")
class PreprocessDPCUNetDefenseAdapter(BaseDefense):
    """Provisional wrapper-based preprocessing defense with strict safety checks."""

    checkpoint_path: str = field(
        default_factory=lambda: os.environ.get("DPC_UNET_CHECKPOINT_PATH", "")
    )
    timestep: float = 50.0
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

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        self._ensure_loaded()
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
        return output, adapter_stage_metadata(
            "preprocess_dpc_unet",
            "preprocess",
            checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
            timestep=float(self.timestep),
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
