from __future__ import annotations

import logging
from typing import Any

import torch
import torch.nn.functional as F

try:
    # Preferred API requested by the user.
    from lab.attacks.base import AttackRegistry, BaseAttack
except ImportError:
    # Compatibility path for this repository.
    from .base import Attack as BaseAttack
    from .base import register_attack

    class AttackRegistry:  # type: ignore[override]
        @staticmethod
        def register(name: str, attack_cls: type[BaseAttack]) -> None:
            register_attack(name)(attack_cls)


LOGGER = logging.getLogger(__name__)


class FGSMAttack(BaseAttack):
    def __init__(self, epsilon: float = 0.01):
        self.epsilon = float(epsilon)
        if self.epsilon <= 0:
            raise ValueError("epsilon must be > 0.")
        LOGGER.info("FGSMAttack initialized with epsilon=%s", self.epsilon)

    def _resolve_torch_model(self, model: Any) -> torch.nn.Module:
        # Support the lab's YOLO wrapper (YOLOModel -> _model -> model),
        # while still accepting raw torch.nn.Module models.
        model_obj = getattr(model, "_model", model)
        torch_model = getattr(model_obj, "model", model_obj)
        if not isinstance(torch_model, torch.nn.Module):
            raise TypeError(
                "FGSMAttack requires a torch.nn.Module or YOLO wrapper exposing one."
            )
        return torch_model

    def _pick_device(self, image: torch.Tensor, torch_model: torch.nn.Module) -> torch.device:
        # Keep the image's current device when possible; otherwise follow model device.
        if image.device.type in {"cpu", "mps", "cuda"}:
            return image.device
        try:
            return next(torch_model.parameters()).device
        except StopIteration:
            # Fallback keeps attack working for models without parameters.
            return torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    def _loss_from_outputs(self, outputs: Any, target: torch.Tensor | None) -> torch.Tensor:
        # Compute supervised loss when target is provided.
        if target is not None:
            if isinstance(outputs, torch.Tensor):
                return F.mse_loss(outputs, target)
            if isinstance(outputs, (list, tuple)):
                tensors = [out for out in outputs if isinstance(out, torch.Tensor)]
                if not tensors:
                    raise TypeError("No tensor outputs available to compute supervised FGSM loss.")
                return F.mse_loss(tensors[0], target)
            raise TypeError("Unsupported model output type for supervised FGSM loss.")

        # Untargeted fallback: maximize model response magnitude.
        if isinstance(outputs, torch.Tensor):
            return outputs.float().mean()
        if isinstance(outputs, (list, tuple)):
            terms = [out.float().mean() for out in outputs if isinstance(out, torch.Tensor)]
            if not terms:
                raise TypeError("No tensor outputs available for untargeted FGSM loss.")
            return torch.stack(terms).mean()
        raise TypeError("Unsupported model output type for untargeted FGSM loss.")

    def apply(self, image: torch.Tensor, model, target=None):
        # Resolve the underlying torch model from wrapper/plain model inputs.
        torch_model = self._resolve_torch_model(model)

        # Choose a device that works on CPU/MPS/CUDA and align tensors there.
        device = self._pick_device(image, torch_model)
        torch_model = torch_model.to(device)
        image = image.to(device)
        if target is not None and isinstance(target, torch.Tensor):
            target = target.to(device)

        # Enable gradient tracking on the input image.
        image = image.detach().clone().requires_grad_(True)

        # Forward pass through the model.
        torch_model.eval()
        outputs = torch_model(image)

        # Compute loss against model predictions (or target when provided).
        loss = self._loss_from_outputs(outputs, target)

        # Backpropagate to get gradients with respect to the input image.
        torch_model.zero_grad(set_to_none=True)
        loss.backward()
        if image.grad is None:
            raise RuntimeError("FGSM failed: image gradients were not produced.")

        # FGSM perturbation: x_adv = x + epsilon * sign(gradient).
        perturbed = image + self.epsilon * image.grad.sign()

        # Clamp to valid image range [0, 1] and return the perturbed tensor.
        perturbed = torch.clamp(perturbed, 0.0, 1.0).detach()
        return perturbed


AttackRegistry.register("fgsm", FGSMAttack)
