from __future__ import annotations

import logging
from typing import Any

import torch
import torch.nn.functional as F

from .objective import AttackObjective
from .pgd_adapter import PGDAttack, _validate_finite_range, _validate_positive_int


LOGGER = logging.getLogger(__name__)


class EOTPGDAttack(PGDAttack):
    """PGD attack that averages gradients over random image transformations."""

    def __init__(
        self,
        epsilon: float = 0.016,
        alpha: float = 0.0015,
        steps: int = 20,
        random_start: bool = True,
        restarts: int = 1,
        objective: AttackObjective | None = None,
        eot_samples: int = 4,
        scale_jitter: float = 0.1,
        translate_frac: float = 0.03,
        brightness_jitter: float = 0.08,
        contrast_jitter: float = 0.08,
        blur_prob: float = 0.25,
    ) -> None:
        super().__init__(
            epsilon=epsilon,
            alpha=alpha,
            steps=steps,
            random_start=random_start,
            restarts=restarts,
            objective=objective,
        )
        self.eot_samples = _validate_positive_int("eot_samples", eot_samples)
        self.scale_jitter = _validate_finite_range(
            "scale_jitter",
            scale_jitter,
            min_value=0.0,
            max_value=0.5,
        )
        self.translate_frac = _validate_finite_range(
            "translate_frac",
            translate_frac,
            min_value=0.0,
            max_value=0.25,
        )
        self.brightness_jitter = _validate_finite_range(
            "brightness_jitter",
            brightness_jitter,
            min_value=0.0,
            max_value=0.5,
        )
        self.contrast_jitter = _validate_finite_range(
            "contrast_jitter",
            contrast_jitter,
            min_value=0.0,
            max_value=0.5,
        )
        self.blur_prob = _validate_finite_range(
            "blur_prob",
            blur_prob,
            min_value=0.0,
            max_value=1.0,
        )
        LOGGER.info(
            "EOT-PGD initialized (epsilon=%s alpha=%s steps=%s random_start=%s restarts=%s "
            "eot_samples=%s scale_jitter=%s translate_frac=%s brightness_jitter=%s "
            "contrast_jitter=%s blur_prob=%s)",
            self.epsilon,
            self.alpha,
            self.steps,
            self.random_start,
            self.restarts,
            self.eot_samples,
            self.scale_jitter,
            self.translate_frac,
            self.brightness_jitter,
            self.contrast_jitter,
            self.blur_prob,
        )

    @staticmethod
    def _rand_unit(generator: torch.Generator) -> float:
        return float(torch.rand((), generator=generator).item())

    def _random_transform(self, x: torch.Tensor, *, generator: torch.Generator) -> torch.Tensor:
        _, _, h, w = x.shape
        scale = 1.0 + ((2.0 * self._rand_unit(generator) - 1.0) * self.scale_jitter)
        nh = max(4, int(round(h * scale)))
        nw = max(4, int(round(w * scale)))
        y = F.interpolate(x, size=(nh, nw), mode="bilinear", align_corners=False)
        if nh > h:
            top = (nh - h) // 2
            y = y[:, :, top : top + h, :]
        elif nh < h:
            pad_top = (h - nh) // 2
            pad_bottom = h - nh - pad_top
            y = F.pad(y, (0, 0, pad_top, pad_bottom), mode="replicate")
        if nw > w:
            left = (nw - w) // 2
            y = y[:, :, :, left : left + w]
        elif nw < w:
            pad_left = (w - nw) // 2
            pad_right = w - nw - pad_left
            y = F.pad(y, (pad_left, pad_right, 0, 0), mode="replicate")

        max_tx = int(round(self.translate_frac * w))
        max_ty = int(round(self.translate_frac * h))
        tx = int(round((2.0 * self._rand_unit(generator) - 1.0) * max_tx))
        ty = int(round((2.0 * self._rand_unit(generator) - 1.0) * max_ty))
        if tx or ty:
            y = torch.roll(y, shifts=(ty, tx), dims=(2, 3))

        contrast = 1.0 + ((2.0 * self._rand_unit(generator) - 1.0) * self.contrast_jitter)
        brightness = (2.0 * self._rand_unit(generator) - 1.0) * self.brightness_jitter
        y = torch.clamp((y * contrast) + brightness, 0.0, 1.0)

        if self._rand_unit(generator) < self.blur_prob:
            y = F.avg_pool2d(y, kernel_size=3, stride=1, padding=1)
        return y

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

            LOGGER.debug("EOT-PGD restart %s/%s started.", restart_idx + 1, self.restarts)
            for step_idx in range(self.steps):
                x_adv = x_adv.detach().requires_grad_(True)
                torch_model.zero_grad(set_to_none=True)
                loss_sum: torch.Tensor | None = None
                with torch.inference_mode(False):
                    with torch.enable_grad():
                        for _sample_idx in range(self.eot_samples):
                            view = self._random_transform(x_adv, generator=generator)
                            outputs = torch_model(view)
                            loss = self._compute_loss(outputs, image=view, target=target)
                            loss_sum = loss if loss_sum is None else (loss_sum + loss)
                        assert loss_sum is not None
                        avg_loss = loss_sum / float(self.eot_samples)
                        avg_loss.backward()
                if x_adv.grad is None:
                    raise RuntimeError("EOT-PGD failed: gradients are unavailable.")
                grad = x_adv.grad
                _, _, padded_h, padded_w = grad.shape
                grad_mask = self.objective.gradient_mask(
                    height=padded_h, width=padded_w, device=grad.device
                )
                if grad_mask is not None:
                    grad = grad * grad_mask
                x_adv = x_adv + (self.alpha * grad.sign())
                delta = torch.clamp(x_adv - x0, min=-self.epsilon, max=self.epsilon)
                self._log_step_stats(
                    step_idx=step_idx,
                    steps_total=self.steps,
                    delta=delta,
                    loss=avg_loss.detach(),
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
