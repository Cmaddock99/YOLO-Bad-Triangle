from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from .base import register_attack
from .fgsm import FGSMAttack
from .utils import iter_images


LOGGER = logging.getLogger(__name__)


def _validate_finite_range(name: str, value: float, *, min_value: float, max_value: float) -> float:
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{name} must be finite.")
    if normalized < min_value or normalized > max_value:
        raise ValueError(f"{name} must be in [{min_value}, {max_value}].")
    return normalized


def _validate_positive_int(name: str, value: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer >= 1.")
    try:
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"{name} must be an integer >= 1.")
            normalized = int(value)
        else:
            normalized = int(value)
            if str(normalized) != str(value):
                raise ValueError(f"{name} must be an integer >= 1.")
    except (TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc) == f"{name} must be an integer >= 1.":
            raise
        raise ValueError(f"{name} must be an integer >= 1.") from exc
    if normalized < 1:
        raise ValueError(f"{name} must be >= 1.")
    return normalized


@register_attack("pgd", "ifgsm", "bim")
class PGDAttack(FGSMAttack):
    """Projected gradient descent attack under an L_inf constraint."""

    def __init__(
        self,
        epsilon: float = 0.016,
        alpha: float = 0.002,
        steps: int = 20,
        random_start: bool = True,
        restarts: int = 1,
    ) -> None:
        super().__init__(epsilon=epsilon)
        self.epsilon = _validate_finite_range("epsilon", self.epsilon, min_value=0.0, max_value=1.0)
        if self.epsilon <= 0.0:
            raise ValueError("epsilon must be > 0.")
        self.alpha = _validate_finite_range("alpha", alpha, min_value=0.0, max_value=1.0)
        if self.alpha <= 0.0:
            raise ValueError("alpha must be > 0.")
        self.steps = _validate_positive_int("steps", steps)
        self.random_start = bool(random_start)
        self.restarts = _validate_positive_int("restarts", restarts)
        LOGGER.info(
            "PGD attack initialized (epsilon=%s alpha=%s steps=%s random_start=%s restarts=%s)",
            self.epsilon,
            self.alpha,
            self.steps,
            self.random_start,
            self.restarts,
        )

    @staticmethod
    def _random_generator(seed: int | None) -> torch.Generator:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(torch.seed() if seed is None else int(seed))
        return generator

    def _random_start_delta(
        self,
        reference: torch.Tensor,
        *,
        generator: torch.Generator,
    ) -> torch.Tensor:
        noise = (
            torch.rand(reference.shape, generator=generator, dtype=torch.float32)
            .mul_(2.0)
            .sub_(1.0)
            .mul_(self.epsilon)
            .to(device=reference.device, dtype=reference.dtype)
        )
        return noise

    def _log_step_stats(
        self,
        *,
        step_idx: int,
        steps_total: int,
        delta: torch.Tensor,
        loss: torch.Tensor,
    ) -> None:
        if not LOGGER.isEnabledFor(logging.DEBUG):
            return
        linf = float(delta.abs().amax().item())
        LOGGER.debug(
            "PGD step %s/%s loss=%.6f linf=%.6f delta_min=%.6f delta_max=%.6f",
            step_idx + 1,
            steps_total,
            float(loss.item()),
            linf,
            float(delta.min().item()),
            float(delta.max().item()),
        )

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
        *,
        seed: int | None = None,
    ) -> torch.Tensor:
        torch_model = self._resolve_torch_model(model)
        if image.device.type in {"cpu", "mps"}:
            device = image.device
        else:
            try:
                device = next(torch_model.parameters()).device
            except StopIteration:
                device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        torch_model = torch_model.to(device)
        x0 = image.to(device).clone().detach()
        if target is not None:
            target = target.to(device)

        _, _, orig_h, orig_w = x0.shape
        stride = int(getattr(torch_model, "stride", torch.tensor([32])).max().item())
        pad_h = (stride - (orig_h % stride)) % stride
        pad_w = (stride - (orig_w % stride)) % stride
        if pad_h or pad_w:
            x0 = F.pad(x0, (0, pad_w, 0, pad_h), mode="replicate")

        best_adv = x0.clone().detach()
        best_loss: torch.Tensor | None = None
        generator = self._random_generator(seed)

        for restart_idx in range(self.restarts):
            if self.random_start:
                noise = self._random_start_delta(x0, generator=generator)
                x_adv = torch.clamp(x0 + noise, 0.0, 1.0).detach()
            else:
                x_adv = x0.clone().detach()

            LOGGER.debug("PGD restart %s/%s started.", restart_idx + 1, self.restarts)
            for step_idx in range(self.steps):
                x_adv = x_adv.detach().requires_grad_(True)
                torch_model.zero_grad(set_to_none=True)
                with torch.inference_mode(False):
                    with torch.enable_grad():
                        outputs = torch_model(x_adv)
                        loss = self._compute_loss(outputs, image=x_adv, target=target)
                        loss.backward()
                if x_adv.grad is None:
                    raise RuntimeError("PGD failed: gradients are unavailable.")
                grad_sign = x_adv.grad.sign()
                x_adv = x_adv + (self.alpha * grad_sign)
                delta = torch.clamp(x_adv - x0, min=-self.epsilon, max=self.epsilon)
                self._log_step_stats(
                    step_idx=step_idx,
                    steps_total=self.steps,
                    delta=delta,
                    loss=loss.detach(),
                )
                x_adv = torch.clamp(x0 + delta, 0.0, 1.0).detach()

            with torch.inference_mode(False):
                with torch.enable_grad():
                    final = x_adv.detach().requires_grad_(True)
                    outputs = torch_model(final)
                    final_loss = self._compute_loss(outputs, image=final, target=target).detach()
            if best_loss is None or final_loss.item() > best_loss.item():
                best_loss = final_loss
                best_adv = x_adv

        if pad_h or pad_w:
            best_adv = best_adv[:, :, :orig_h, :orig_w]
        return best_adv.detach()

    def apply(
        self,
        source_dir: Path | torch.Tensor,
        output_dir: Path | Any | None = None,
        *,
        seed: int | None = None,
        model: Any | None = None,
        target: torch.Tensor | None = None,
    ) -> Path | torch.Tensor:
        if isinstance(source_dir, torch.Tensor):
            image = source_dir
            model_for_tensor = model if model is not None else output_dir
            if model_for_tensor is None:
                raise ValueError("PGDAttack tensor mode requires a model argument.")
            return self._apply_to_tensor(image, model=model_for_tensor, target=target, seed=seed)

        if output_dir is None:
            raise ValueError("PGDAttack requires output_dir in pipeline mode.")
        if model is None:
            raise ValueError("PGDAttack requires model in pipeline mode.")

        source_path = Path(source_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        LOGGER.info(
            "Running PGD attack on '%s' (epsilon=%s alpha=%s steps=%s random_start=%s restarts=%s)",
            source_path,
            self.epsilon,
            self.alpha,
            self.steps,
            self.random_start,
            self.restarts,
        )

        for image_path in iter_images(source_path):
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                continue
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            image_tensor = (
                torch.from_numpy(image_rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            )
            adv_tensor = self._apply_to_tensor(image_tensor, model=model, target=target, seed=seed)
            adv_rgb = self._tensor_to_uint8_rgb(adv_tensor)
            adv_bgr = cv2.cvtColor(adv_rgb, cv2.COLOR_RGB2BGR)
            relative = image_path.relative_to(source_path)
            out_file = output_path / relative
            out_file.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_file), adv_bgr)
        return output_path
