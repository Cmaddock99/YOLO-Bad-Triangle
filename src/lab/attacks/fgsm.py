from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from .base import Attack, register_attack
from .utils import iter_images


LOGGER = logging.getLogger(__name__)


@register_attack("fgsm")
class FGSMAttack(Attack):
    def __init__(self, epsilon: float = 0.01):
        self.epsilon = float(epsilon)
        if self.epsilon <= 0.0:
            raise ValueError("epsilon must be > 0.")
        LOGGER.info("FGSM attack initialized (epsilon=%s)", self.epsilon)

    @staticmethod
    def _iter_output_tensors(outputs: Any) -> list[torch.Tensor]:
        if isinstance(outputs, torch.Tensor):
            return [outputs]
        if isinstance(outputs, dict):
            tensors: list[torch.Tensor] = []
            for value in outputs.values():
                tensors.extend(FGSMAttack._iter_output_tensors(value))
            return tensors
        if isinstance(outputs, (list, tuple)):
            tensors = []
            for value in outputs:
                tensors.extend(FGSMAttack._iter_output_tensors(value))
            return tensors
        return []

    @staticmethod
    def _resolve_torch_model(model: Any) -> torch.nn.Module:
        # Resolve wrapped YOLO objects down to a torch.nn.Module.
        model_obj = getattr(model, "_model", model)
        torch_model = getattr(model_obj, "model", model_obj)
        if not isinstance(torch_model, torch.nn.Module):
            raise TypeError("FGSMAttack requires a torch.nn.Module-compatible model.")
        return torch_model

    def _compute_loss(
        self,
        outputs: Any,
        *,
        image: torch.Tensor,
        target: torch.Tensor | None,
    ) -> torch.Tensor:
        # Targeted mode: pull predictions toward a specific tensor.
        tensor_outputs = self._iter_output_tensors(outputs)
        if target is not None and tensor_outputs:
            return F.mse_loss(tensor_outputs[0].float(), target.float())

        # Untargeted mode: reduce detection confidence/objectness by maximizing
        # a negative confidence proxy. For common detection tensors this uses
        # objectness logits at index 4.
        if tensor_outputs:
            confidence_terms: list[torch.Tensor] = []
            for out in tensor_outputs:
                if out.ndim >= 3 and out.shape[-1] >= 5:
                    confidence_terms.append(out[..., 4].float().mean())
            if confidence_terms:
                return -torch.stack(confidence_terms).mean()

            # Fallback: if no confidence axis is detectable, use negative mean
            # to still push outputs downward in untargeted mode.
            LOGGER.debug(
                "FGSM using fallback untargeted loss (no confidence axis found in model output)."
            )
            return -torch.stack([out.float().mean() for out in tensor_outputs]).mean()

        # Fallback for Ultralytics Results-like outputs.
        # Note: these are often post-processed and may not carry gradients, but we
        # still try to build a loss from prediction tensors when available.
        if isinstance(outputs, (list, tuple)) and outputs:
            first = outputs[0]
            logits = getattr(first, "logits", None)
            if isinstance(logits, torch.Tensor):
                if target is not None and target.shape == logits.shape:
                    return F.mse_loss(logits.float(), target.float())
                return logits.float().mean()
            pred = getattr(first, "pred", None)
            if isinstance(pred, torch.Tensor):
                if target is not None and target.shape == pred.shape:
                    return F.mse_loss(pred.float(), target.float())
                return pred.float().mean()
            boxes = getattr(first, "boxes", None)
            if boxes is not None:
                box_data = getattr(boxes, "data", None)
                if isinstance(box_data, torch.Tensor):
                    if target is not None and target.shape == box_data.shape:
                        return F.mse_loss(box_data.float(), target.float())
                    return box_data.float().mean()
            probs = getattr(first, "probs", None)
            if isinstance(probs, torch.Tensor):
                if target is not None and target.shape == probs.shape:
                    return F.mse_loss(probs.float(), target.float())
                return probs.float().mean()

        raise TypeError(
            "Unable to compute FGSM loss from model outputs (no differentiable tensor found)."
        )

    def _apply_to_tensor(
        self,
        image: torch.Tensor,
        model: Any,
        target: torch.Tensor | None = None,
    ) -> torch.Tensor:
        torch_model = self._resolve_torch_model(model)

        # Select a device that works for CPU or MPS execution.
        if image.device.type in {"cpu", "mps"}:
            device = image.device
        else:
            try:
                device = next(torch_model.parameters()).device
            except StopIteration:
                device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        torch_model = torch_model.to(device)
        image = image.to(device)
        if target is not None:
            target = target.to(device)

        # FGSM requires gradients wrt input, so we must explicitly enable them.
        # YOLO backbones also expect stride-aligned spatial dimensions, so pad
        # to a multiple of stride for the forward/backward pass and crop later.
        base_image = image.clone().detach()
        _, _, orig_h, orig_w = base_image.shape
        stride = int(getattr(torch_model, "stride", torch.tensor([32])).max().item())
        pad_h = (stride - (orig_h % stride)) % stride
        pad_w = (stride - (orig_w % stride)) % stride
        if pad_h or pad_w:
            base_image = F.pad(base_image, (0, pad_w, 0, pad_h), mode="replicate")
        image = base_image.clone().detach().requires_grad_(True)

        # YOLO forward paths may be wrapped in inference_mode(); disable it
        # locally while preserving the model's existing train/eval state.
        torch_model.zero_grad(set_to_none=True)
        with torch.inference_mode(False):
            with torch.enable_grad():
                outputs = torch_model(image)
                loss = self._compute_loss(outputs, image=image, target=target)
                # Backpropagate to get image gradients.
                loss.backward()

        if image.grad is None:
            raise RuntimeError("FGSM failed: image gradients are unavailable.")

        # FGSM perturbation: x_adv = x + epsilon * sign(gradient)
        grad = image.grad
        perturbed = image + (self.epsilon * grad.sign())

        # Keep pixels in valid image range.
        perturbed = torch.clamp(perturbed, 0.0, 1.0)
        if pad_h or pad_w:
            perturbed = perturbed[:, :, :orig_h, :orig_w]
        return perturbed.detach()

    def apply(
        self,
        source_dir: Path | torch.Tensor,
        output_dir: Path | Any | None = None,
        *,
        seed: int | None = None,
        model: Any | None = None,
        target: torch.Tensor | None = None,
    ) -> Path | torch.Tensor:
        # Backward-compatible tensor mode: apply(image_tensor, model, target=...)
        if isinstance(source_dir, torch.Tensor):
            image = source_dir
            model_for_tensor = model if model is not None else output_dir
            if model_for_tensor is None:
                raise ValueError("FGSMAttack tensor mode requires a model argument.")
            return self._apply_to_tensor(image, model=model_for_tensor, target=target)

        # Pipeline mode: apply(source_dir, output_dir, seed=..., model=...)
        if output_dir is None:
            raise ValueError("FGSMAttack requires output_dir in pipeline mode.")
        if model is None:
            raise ValueError("FGSMAttack requires model in pipeline mode.")
        del seed

        source_path = Path(source_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Running FGSM attack on '%s' with epsilon=%s", source_path, self.epsilon)

        for image_path in iter_images(source_path):
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                continue

            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            image_tensor = (
                torch.from_numpy(image_rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            )
            adv_tensor = self._apply_to_tensor(image_tensor, model=model, target=target)
            adv_rgb = (
                adv_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255.0
            ).clip(0, 255).astype(np.uint8)
            adv_bgr = cv2.cvtColor(adv_rgb, cv2.COLOR_RGB2BGR)

            relative = image_path.relative_to(source_path)
            out_file = output_path / relative
            out_file.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_file), adv_bgr)

        return output_path


