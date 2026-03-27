from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from lab.config.contracts import PIXEL_MAX

from .base_attack import BaseAttack
from .fgsm_adapter import FGSMAttack
from .framework_registry import register_attack_plugin


LOGGER = logging.getLogger(__name__)

_ARCTANH_EPS = 1e-6


class CWAttack(FGSMAttack):
    """Carlini-Wagner L2 attack.

    Uses the arctanh reparameterisation to keep adversarial examples in [0,1]
    and minimises  L2_distortion + c * attack_loss  with Adam.  Inherits
    _compute_loss / _resolve_torch_model / _iter_output_tensors from FGSMAttack.
    """

    def __init__(
        self,
        c: float = 1.0,
        max_iter: int = 200,
        lr: float = 0.01,
        binary_search_steps: int = 1,
        confidence: float = 0.0,
        early_stop: bool = True,
    ) -> None:
        # FGSMAttack.__init__ requires epsilon > 0; we pass a dummy value because
        # C&W does not use epsilon — it uses the L2 term instead.
        super().__init__(epsilon=1.0)
        self.c = float(c)
        self.max_iter = int(max_iter)
        self.lr = float(lr)
        self.binary_search_steps = int(binary_search_steps)
        self.confidence = float(confidence)
        self.early_stop = bool(early_stop)
        LOGGER.info(
            "CW attack initialised (c=%s max_iter=%s lr=%s binary_search_steps=%s early_stop=%s)",
            self.c, self.max_iter, self.lr, self.binary_search_steps, self.early_stop,
        )

    # ------------------------------------------------------------------
    # Detection counting
    # ------------------------------------------------------------------

    def _count_detections(self, outputs: Any) -> int:
        """Count detections above a low confidence threshold."""
        count = 0
        for t in self._iter_output_tensors(outputs):
            if t.ndim >= 2 and t.shape[-1] >= 5:
                conf = t[..., 4]
                count += int((conf > 0.1).sum().item())
        return count

    # ------------------------------------------------------------------
    # Core optimisation
    # ------------------------------------------------------------------

    def _apply_to_tensor(
        self,
        x_orig: torch.Tensor,
        torch_model: torch.nn.Module,
    ) -> tuple[torch.Tensor, dict[str, Any]]:
        """
        Args:
            x_orig: BCHW float32 tensor in [0, 1], stride-aligned.
            torch_model: bare torch.nn.Module in eval() mode.
        Returns:
            (adversarial_tensor, metadata_dict)
        """
        # 1. Baseline detection check — nothing to attack if model sees nothing.
        with torch.no_grad():
            with torch.inference_mode(False):
                baseline_out = torch_model(x_orig)
        baseline_det = self._count_detections(baseline_out)
        if baseline_det == 0:
            LOGGER.debug("CW skipping: no baseline detections.")
            return x_orig.clone(), {"skipped": True, "l2": 0.0, "success": False}

        # 2. Initialise w in unconstrained space via arctanh.
        #    x = tanh(w)*0.5 + 0.5  maps R -> (0,1)
        #    w = arctanh(2*x - 1)
        w_init = torch.arctanh(
            torch.clamp(2.0 * x_orig - 1.0, -1.0 + _ARCTANH_EPS, 1.0 - _ARCTANH_EPS)
        ).detach()

        best_adv = x_orig.clone().detach()
        best_l2 = float("inf")
        best_det = baseline_det
        best_success = False
        c_current = self.c

        # 3. Outer binary search over c (1 iteration = fixed c, no search).
        c_lo, c_hi = 0.0, self.c * 10.0
        for bs_step in range(self.binary_search_steps):
            if self.binary_search_steps > 1:
                c_current = (c_lo + c_hi) / 2.0

            # 4. Adam inner loop.
            w_var = w_init.clone().detach().requires_grad_(True)
            optimizer = torch.optim.Adam([w_var], lr=self.lr)
            step_success = False

            for step in range(self.max_iter):
                optimizer.zero_grad()

                # Map back to image space.
                # .contiguous() required for MPS: tanh can produce non-contiguous
                # tensors that break YOLO's internal .view() calls.
                x_adv = (torch.tanh(w_var) * 0.5 + 0.5).contiguous()

                # Forward pass with gradient tracking.
                torch_model.zero_grad(set_to_none=True)
                with torch.inference_mode(False):
                    with torch.enable_grad():
                        outputs = torch_model(x_adv)

                l2_sq = ((x_adv - x_orig) ** 2).sum()
                # _compute_loss returns -confidence.mean() for untargeted mode.
                # Minimising (l2_sq + c * (-conf)) drives conf → 0.
                attack_loss = self._compute_loss(outputs, image=x_adv)
                total_loss = l2_sq + c_current * attack_loss
                total_loss.backward()

                # Guard against NaN/Inf gradients (can occur on some YOLO heads).
                if w_var.grad is not None and torch.isfinite(w_var.grad).all():
                    optimizer.step()
                else:
                    LOGGER.debug("CW step %s: non-finite gradient, skipping update.", step)

                # Evaluate result with no_grad.
                with torch.no_grad():
                    x_check = (torch.tanh(w_var) * 0.5 + 0.5).contiguous()
                    l2_val = float(((x_check - x_orig) ** 2).sum().sqrt().item())
                    with torch.inference_mode(False):
                        check_out = torch_model(x_check)
                    n_det = self._count_detections(check_out)
                    # Treat detection reduction as progress, not only total elimination.
                    improved = n_det < best_det or (n_det == best_det and l2_val < best_l2)
                    if improved:
                        best_det = n_det
                        best_l2 = l2_val
                        best_adv = x_check.clone()
                        best_success = best_det < baseline_det
                        step_success = True

                # Early stopping once attack has succeeded for >half the budget.
                if self.early_stop and step_success and step > self.max_iter // 2:
                    LOGGER.debug("CW early stop at step %s/%s.", step, self.max_iter)
                    break

            # Binary search adjustment.
            if self.binary_search_steps > 1:
                if step_success:
                    c_hi = c_current   # succeeded — try smaller c (less distortion)
                else:
                    c_lo = c_current   # failed — try larger c (more pressure)

        return best_adv.detach(), {
            "success": best_success,
            "l2": best_l2,
            "baseline_detections": baseline_det,
            "final_detections": best_det,
            "c": c_current,
            "max_iter": self.max_iter,
            "binary_search_steps": self.binary_search_steps,
        }


@dataclass
@register_attack_plugin("cw", "cw_l2")
class CWAttackAdapter(BaseAttack):
    """Framework C&W L2 plugin.

    Suitable for manual sweeps on GPU/Apple-Silicon hardware.
    Do NOT add to auto_cycle.py ALL_ATTACKS — it is too slow for CPU-only runs.

    Effectiveness note: CW L2 was evaluated against YOLO detection in March 2026
    across all parameter settings (c, max_iter, binary_search_steps) and achieved
    0% detection suppression. It is designed to minimise classifier logit margins,
    not detection confidence landscapes. Kept for research reference only.
    """

    c: float = 1.0
    max_iter: int = 200
    lr: float = 0.01
    binary_search_steps: int = 1
    confidence: float = 0.0
    early_stop: bool = True
    device: str = "cpu"
    name: str = "cw"
    _impl: CWAttack = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._impl = CWAttack(
            c=self.c,
            max_iter=self.max_iter,
            lr=self.lr,
            binary_search_steps=self.binary_search_steps,
            confidence=self.confidence,
            early_stop=self.early_stop,
        )

    @staticmethod
    def _resolve_model(model: Any | None) -> Any:
        if model is None:
            raise ValueError("CW framework plugin requires a model for gradient computation.")
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
        torch_model = self._impl._resolve_torch_model(resolved_model)

        # Device selection — prefer MPS on Apple Silicon, fall back to CPU.
        if self.device == "cpu":
            device = torch.device("cpu")
        elif self.device == "mps":
            device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        elif self.device == "cuda":
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            device = torch.device(self.device)

        torch_model = torch_model.to(device)

        # Convert image and apply stride padding (required by YOLO backbones).
        x_orig = self._image_to_tensor(image).to(device)
        _, _, orig_h, orig_w = x_orig.shape
        stride = int(getattr(torch_model, "stride", torch.tensor([32])).max().item())
        pad_h = (stride - (orig_h % stride)) % stride
        pad_w = (stride - (orig_w % stride)) % stride
        if pad_h or pad_w:
            x_orig = F.pad(x_orig, (0, pad_w, 0, pad_h), mode="replicate")

        x_adv_t, stats = self._impl._apply_to_tensor(x_orig, torch_model)

        # Crop padding before converting back.
        if pad_h or pad_w:
            x_adv_t = x_adv_t[:, :, :orig_h, :orig_w]

        adv_image = self._tensor_to_image(x_adv_t)
        return adv_image, {
            "attack": "cw",
            "c": self.c,
            "max_iter": self.max_iter,
            "lr": self.lr,
            "binary_search_steps": self.binary_search_steps,
            **stats,
        }
