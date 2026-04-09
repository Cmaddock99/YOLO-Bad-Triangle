from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
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


def _sha256_file(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


@dataclass
class _BaseCDogAdapter(BaseDefense):
    """Shared checkpoint loading, routing, and postprocess logic for DPC-UNet defenses."""

    is_trainable: bool = True

    checkpoint_path: str = field(
        default_factory=lambda: os.environ.get("DPC_UNET_CHECKPOINT_PATH", "")
    )
    sharpen_alpha: float = 0.0
    routing_enabled: bool = False
    attack_hint: str = ""
    low_noise_hf: float = 0.03
    strong_hf: float = 0.08
    strong_laplacian: float = 0.02
    color_order: str = "bgr"
    scaling: str = "zero_one"
    normalize: bool = False
    device: str = "cpu"
    name: str = ""
    _model: DPCUNet = field(init=False, repr=False)
    _cfg: WrapperInputConfig = field(init=False, repr=False)
    _loaded: bool = field(default=False, init=False, repr=False)
    _checkpoint_sha256: str | None = field(default=None, init=False, repr=False)

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
        # Hash at load time so checkpoint_provenance() returns a stable value even if
        # the file is later modified or replaced on disk.
        self._checkpoint_sha256 = _sha256_file(checkpoint)
        self._loaded = True

    def _routing_thresholds(self) -> RoutingThresholds:
        return RoutingThresholds(
            low_noise_hf=float(self.low_noise_hf),
            strong_hf=float(self.strong_hf),
            strong_laplacian=float(self.strong_laplacian),
        )

    def checkpoint_provenance(self) -> list[dict[str, str]]:
        raw = (self.checkpoint_path or "").strip()
        if not raw:
            return []
        resolved = Path(raw).expanduser().resolve()
        if not resolved.is_file():
            return []
        # Use cached hash from load time; fall back to re-hashing if not loaded yet.
        digest = self._checkpoint_sha256 if self._loaded else _sha256_file(resolved)
        if digest is None:
            return []
        return [{"path": str(resolved), "sha256": digest}]

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        return predictions, adapter_stage_metadata(
            self._stage_name,
            "postprocess",
            note="identity_postprocess",
        )


@dataclass
@register_defense_plugin("preprocess_dpc_unet", "c_dog")
class CDogDefenseAdapter(_BaseCDogAdapter):
    """DPC-UNet preprocessing defense (single or multi-pass).

    Runs the DPC-UNet denoiser at a given timestep before YOLO inference to
    remove adversarial perturbations while preserving object structure.
    """

    timestep: float = 25.0   # cycle-11 Phase 3 tuned (was 50.0); literature: 25–35 optimal for detection
    sharpen_alpha: float = 0.55  # cycle-11 Phase 3 tuned (was 0.0)
    # Multi-pass: comma-separated timesteps e.g. "75,50,25". When set,
    # overrides `timestep` and runs the model once per value in sequence.
    timestep_schedule: str = ""
    name: str = "c_dog"
    _stage_name: str = field(default="preprocess_dpc_unet", init=False, repr=False)

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
                thresholds=self._routing_thresholds(),
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
                self._stage_name, "preprocess",
                checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
                routing_enabled=bool(self.routing_enabled),
                routing_route=route,
                attack_hint=runtime_attack_hint or None,
                **signal.as_dict(),
                **stats,
            )
        schedule = self._parse_timestep_schedule()
        if schedule:
            output, stats = run_wrapper_multipass_on_bgr_image(
                image, self._model, timestep_schedule=schedule, cfg=self._cfg, device=self.device,
            )
        else:
            output, stats = run_wrapper_on_bgr_image(
                image, self._model, timestep=float(self.timestep), cfg=self._cfg, device=self.device,
            )
        if not bool(stats["finite"]):
            raise RuntimeError("DPC-UNet defense produced non-finite output.")
        if output.shape != image.shape:
            raise RuntimeError(
                f"DPC-UNet defense changed image shape: input={image.shape} output={output.shape}"
            )
        if self.sharpen_alpha > 0.0:
            output = sharpen_image(output, alpha=float(self.sharpen_alpha))
        if schedule:
            # Multipass: timestep is meaningless (multiple values were used); report schedule instead.
            timestep_meta: float | None = None
            schedule_meta: str | None = self.timestep_schedule or None
            passes_meta: int = len(schedule)
        else:
            timestep_meta = float(self.timestep)
            schedule_meta = None
            passes_meta = 1
        return output, adapter_stage_metadata(
            self._stage_name, "preprocess",
            checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
            timestep=timestep_meta,
            timestep_schedule=schedule_meta,
            passes=passes_meta,
            sharpen_alpha=float(self.sharpen_alpha),
            color_order=self._cfg.color_order,
            scaling=self._cfg.scaling,
            normalize=self._cfg.normalize,
            **stats,
        )


@dataclass
@register_defense_plugin("preprocess_ensemble_c_dog", "c_dog_ensemble")
class EnsembleCDogDefenseAdapter(_BaseCDogAdapter):
    """Ensemble defense: median blur → DPC-UNet → optional sharpening.

    Median blur removes pixel-level adversarial noise (FGSM/PGD perturbations).
    DPC-UNet at t=50 handles residual structured adversarial patterns without
    over-smoothing. Unsharp masking (optional) recovers edges softened by the UNet.
    """

    # Median blur kernel applied before DPC-UNet (must be odd, >= 3).
    median_kernel: int = 3
    # DPC-UNet timestep(s). Single pass at t=50 is the sweet spot.
    timestep_schedule: str = "50"
    sharpen_alpha: float = 0.3
    name: str = "c_dog_ensemble"
    _stage_name: str = field(default="preprocess_ensemble_c_dog", init=False, repr=False)

    def __post_init__(self) -> None:
        k = int(self.median_kernel)
        if k < 3 or k % 2 == 0:
            raise ValueError("median_kernel must be odd and >= 3.")
        self.median_kernel = k
        super().__post_init__()

    def _parse_schedule(self) -> list[float]:
        return [float(t.strip()) for t in self.timestep_schedule.split(",") if t.strip()]

    def preprocess(self, image: np.ndarray, **kwargs: Any) -> tuple[np.ndarray, dict[str, Any]]:
        runtime_attack_hint = str(kwargs.get("attack_hint", "") or self.attack_hint)
        self._ensure_loaded()
        signal = detect_attack_signal(image)
        route = "median_cdog"
        if self.routing_enabled:
            route = choose_route(
                signal=signal,
                attack_hint=runtime_attack_hint,
                thresholds=self._routing_thresholds(),
            )

        stage_input = image
        if route in {"median_only", "median_cdog"}:
            stage_input = cv2.medianBlur(image, self.median_kernel)

        if route == "passthrough":
            output = image.copy()
            stats = {
                "finite": bool(np.isfinite(output).all()),
                "tensor_min": float(output.min()),
                "tensor_max": float(output.max()),
                "tensor_mean": float(output.mean()),
                "tensor_std": float(output.std()),
            }
        elif route == "median_only":
            output = stage_input
            stats = {
                "finite": bool(np.isfinite(output).all()),
                "tensor_min": float(output.min()),
                "tensor_max": float(output.max()),
                "tensor_mean": float(output.mean()),
                "tensor_std": float(output.std()),
            }
        else:
            schedule = self._parse_schedule()
            if route == "cdog_only":
                stage_input = image
            output, stats = run_wrapper_multipass_on_bgr_image(
                stage_input, self._model, timestep_schedule=schedule, cfg=self._cfg, device=self.device,
            )
            if not bool(stats["finite"]):
                raise RuntimeError("DPC-UNet (ensemble) produced non-finite output.")
            if output.shape != image.shape:
                raise RuntimeError(
                    f"DPC-UNet (ensemble) changed image shape: input={image.shape} output={output.shape}"
                )
            if self.sharpen_alpha > 0.0:
                output = sharpen_image(output, alpha=float(self.sharpen_alpha))

        return output, adapter_stage_metadata(
            self._stage_name, "preprocess",
            checkpoint_path=str(Path(self.checkpoint_path).expanduser()),
            median_kernel=self.median_kernel,
            timestep_schedule=self.timestep_schedule,
            sharpen_alpha=float(self.sharpen_alpha),
            routing_enabled=bool(self.routing_enabled),
            routing_route=route,
            attack_hint=runtime_attack_hint or None,
            **signal.as_dict(),
            color_order=self._cfg.color_order,
            scaling=self._cfg.scaling,
            normalize=self._cfg.normalize,
            **stats,
        )
