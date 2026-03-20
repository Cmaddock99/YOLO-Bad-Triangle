from __future__ import annotations

import sys
import unittest
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks.fgsm_adapter import FGSMAttack, FGSMAttackAdapter


class DummyDetectionModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stride = torch.tensor([32.0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Shape [B, N, 6] with a confidence-like channel at index 4.
        score = x.mean(dim=(1, 2, 3), keepdim=False).unsqueeze(-1)
        return score.unsqueeze(-1).repeat(1, 10, 6)


class FGSMSmokeTests(unittest.TestCase):
    def test_apply_to_tensor_preserves_shape_and_clamps(self) -> None:
        model = DummyDetectionModel().eval()
        attack = FGSMAttack(epsilon=0.01)
        image = torch.rand(1, 3, 65, 79)

        adv = attack._apply_to_tensor(image, model)

        self.assertIsInstance(adv, torch.Tensor)
        self.assertEqual(tuple(adv.shape), tuple(image.shape))
        self.assertFalse(model.training)
        self.assertGreaterEqual(float(adv.min().item()), 0.0)
        self.assertLessEqual(float(adv.max().item()), 1.0)

    def test_adapter_apply_returns_valid_image(self) -> None:
        model = DummyDetectionModel().eval()
        adapter = FGSMAttackAdapter(epsilon=0.01)
        image_bgr = np.random.randint(0, 255, size=(63, 81, 3), dtype=np.uint8)

        attacked, metadata = adapter.apply(image_bgr, model=model)

        self.assertIsInstance(attacked, np.ndarray)
        self.assertEqual(attacked.shape, image_bgr.shape)
        self.assertEqual(metadata["attack"], "fgsm")
        self.assertIn("epsilon", metadata)

    def test_uint8_conversion_uses_rounding_not_truncation(self) -> None:
        # Tiny +/- deltas around an exact integer level should remain unchanged
        # after conversion to uint8.
        base = 10.0 / 255.0
        tensor = torch.tensor(
            [[[[base - 1e-5]], [[base + 1e-5]], [[base]]]],
            dtype=torch.float32,
        )
        converted = FGSMAttack._tensor_to_uint8_rgb(tensor)

        self.assertEqual(converted.shape, (1, 1, 3))
        self.assertEqual(int(converted[0, 0, 0]), 10)
        self.assertEqual(int(converted[0, 0, 1]), 10)
        self.assertEqual(int(converted[0, 0, 2]), 10)


if __name__ == "__main__":
    unittest.main()
