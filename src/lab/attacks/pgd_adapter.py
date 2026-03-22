from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.config.contracts import ATTACK_OBJECTIVE_UNTARGETED
from lab.config.contracts import PIXEL_MAX

from .base_attack import BaseAttack
from .fgsm_adapter import FGSMAttack
from .framework_registry import register_attack_plugin
from .objective import AttackObjective


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


class PGDAttack(FGSMAttack):
    """Projected gradient descent attack under an L_inf constraint."""

    def __init__(
        self,
        epsilon: float = 0.016,
        alpha: float = 0.002,
        steps: int = 20,
        random_start: bool = True,
        restarts: int = 1,
        *,
        objective: AttackObjective | None = None,
    ) -> None:
        super().__init__(epsilon=epsilon, objective=objective)
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
                grad = x_adv.grad
                _, _, padded_h, padded_w = grad.shape
                grad_mask = self.objective.gradient_mask(
                    height=padded_h, width=padded_w, device=grad.device
                )
                if grad_mask is not None:
                    grad = grad * grad_mask
                grad_sign = grad.sign()
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


@dataclass
@register_attack_plugin("pgd", "ifgsm", "bim")
class PGDAttackAdapter(BaseAttack):
    """Framework PGD plugin."""

    epsilon: float = 0.016
    alpha: float = 0.002
    steps: int = 20
    random_start: bool = True
    restarts: int = 1
    objective_mode: str = ATTACK_OBJECTIVE_UNTARGETED
    target_class: int | None = None
    preserve_weight: float = 0.25
    attack_roi: tuple[float, float, float, float] | list[float] | str | None = None
    name: str = "pgd_adapter"
    _impl: PGDAttack = field(init=False, repr=False)
    _objective: AttackObjective = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._objective = AttackObjective.from_kwargs(
            mode=self.objective_mode,
            target_class=self.target_class,
            preserve_weight=self.preserve_weight,
            attack_roi=self.attack_roi,
        )
        self._impl = PGDAttack(
            epsilon=self.epsilon,
            alpha=self.alpha,
            steps=self.steps,
            random_start=self.random_start,
            restarts=self.restarts,
            objective=self._objective,
        )

    @staticmethod
    def _resolve_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError(
                "PGD framework plugin requires a model for gradient computation."
            )
        return model

    @staticmethod
    def _image_to_tensor(image: np.ndarray) -> torch.Tensor:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return torch.from_numpy(rgb).float().permute(2, 0, 1).unsqueeze(0) / PIXEL_MAX

    @staticmethod
    def _tensor_to_image(tensor: torch.Tensor) -> np.ndarray:
        rgb = np.rint(
            tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * PIXEL_MAX
        ).clip(0, 255).astype(np.uint8)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        resolved_model = self._resolve_model(model)
        target = kwargs.get("target")
        seed = kwargs.get("seed")
        tensor = self._image_to_tensor(image)
        adv_tensor = self._impl._apply_to_tensor(tensor, resolved_model, target=target, seed=seed)
        attacked = self._tensor_to_image(adv_tensor)
        return attacked, {
            "attack": "pgd",
            "epsilon": self._impl.epsilon,
            "alpha": self._impl.alpha,
            "steps": self._impl.steps,
            "random_start": self._impl.random_start,
            "restarts": self._impl.restarts,
            **self._objective.to_dict(),
        }
