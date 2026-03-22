from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class FeatureLossConfig:
    layer_names: tuple[str, ...]
    reduction: str = "mean"


class YOLOFeatureExtractor:
    """Frozen backbone hook helper for feature-map matching losses."""

    def __init__(self, yolo_model: Any, *, config: FeatureLossConfig) -> None:
        self.config = config
        model_obj = getattr(yolo_model, "_model", yolo_model)
        self.model = getattr(model_obj, "model", model_obj)
        if not isinstance(self.model, torch.nn.Module):
            raise TypeError("YOLOFeatureExtractor requires torch.nn.Module-compatible model.")
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad_(False)

        self._hooks: list[Any] = []
        self._features: dict[str, torch.Tensor] = {}
        self._register_hooks()

    def _register_hooks(self) -> None:
        by_name = dict(self.model.named_modules())
        for name in self.config.layer_names:
            module = by_name.get(name)
            if module is None:
                raise ValueError(f"Feature layer '{name}' not found in YOLO model.")

            def _capture(_module: Any, _inputs: Any, output: Any, *, key: str = name) -> None:
                if isinstance(output, torch.Tensor):
                    self._features[key] = output

            self._hooks.append(module.register_forward_hook(_capture))

    def close(self) -> None:
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()
        self._features.clear()

    def extract(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        self._features = {}
        _ = self.model(x)
        return dict(self._features)


def yolo_feature_matching_loss(
    *,
    extractor: YOLOFeatureExtractor,
    denoised: torch.Tensor,
    clean: torch.Tensor,
) -> torch.Tensor:
    den_feat = extractor.extract(denoised)
    clean_feat = extractor.extract(clean)
    losses: list[torch.Tensor] = []
    for name in extractor.config.layer_names:
        if name not in den_feat or name not in clean_feat:
            continue
        losses.append(F.l1_loss(den_feat[name], clean_feat[name].detach()))
    if not losses:
        return denoised.new_zeros(())
    stacked = torch.stack(losses)
    if extractor.config.reduction == "sum":
        return stacked.sum()
    return stacked.mean()
