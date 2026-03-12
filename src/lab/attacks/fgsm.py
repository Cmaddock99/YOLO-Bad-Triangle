from __future__ import annotations

import logging
from typing import Any

import torch

try:
    # Preferred import path requested by the spec.
    from lab.attacks.base import AttackRegistry, BaseAttack
except ImportError:
    # Repository compatibility layer:
    # this project exposes Attack/register_attack instead of BaseAttack/AttackRegistry.
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
        LOGGER.info("FGSMAttack epsilon=%s", self.epsilon)

    def apply(self, image: torch.Tensor, model, target=None):
        # Resolve wrappers (such as YOLOModel/Ultralytics YOLO) into a torch.nn.Module.
        model_obj: Any = getattr(model, "_model", model)
        torch_model: Any = getattr(model_obj, "model", model_obj)
        if not isinstance(torch_model, torch.nn.Module):
            raise TypeError("FGSMAttack requires a torch.nn.Module-compatible model.")

        # Choose a device that works on CPU or MPS and place model/tensors there.
        if image.device.type in {"cpu", "mps"}:
            device = image.device
        else:
            first_param = next(torch_model.parameters(), None)
            if first_param is not None:
                device = first_param.device
            else:
                device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        torch_model = torch_model.to(device)
        image = image.to(device)
        if target is not None:
            target = target.to(device)

        # Enable gradient tracking on the input image.
        image = image.detach().clone().requires_grad_(True)

        # Forward pass through the model to produce predictions.
        torch_model.eval()
        outputs = torch_model(image)

        # Compute a loss against predictions (or target if provided) for backprop.
        if target is not None:
            if isinstance(outputs, torch.Tensor):
                loss = torch.nn.functional.mse_loss(outputs, target)
            elif isinstance(outputs, (list, tuple)):
                tensor_outputs = [out for out in outputs if isinstance(out, torch.Tensor)]
                if not tensor_outputs:
                    raise TypeError("Model output does not contain tensors for targeted FGSM.")
                loss = torch.nn.functional.mse_loss(tensor_outputs[0], target)
            else:
                raise TypeError("Unsupported output type for targeted FGSM loss.")
        else:
            if isinstance(outputs, torch.Tensor):
                loss = outputs.float().mean()
            elif isinstance(outputs, (list, tuple)):
                tensor_losses = [out.float().mean() for out in outputs if isinstance(out, torch.Tensor)]
                if not tensor_losses:
                    raise TypeError("Model output does not contain tensors for FGSM loss.")
                loss = torch.stack(tensor_losses).mean()
            else:
                raise TypeError("Unsupported model output type for FGSM loss computation.")

        # Backpropagate to obtain the gradient with respect to the input image.
        torch_model.zero_grad(set_to_none=True)
        loss.backward()
        if image.grad is None:
            raise RuntimeError("FGSM failed because image gradients were not produced.")

        # Apply FGSM perturbation: x_adv = x + epsilon * sign(grad).
        perturbed = image + self.epsilon * image.grad.sign()

        # Clamp back into the valid image range [0, 1].
        perturbed = torch.clamp(perturbed, 0.0, 1.0)

        # Return the perturbed image tensor.
        return perturbed.detach()


AttackRegistry.register("fgsm", FGSMAttack)
