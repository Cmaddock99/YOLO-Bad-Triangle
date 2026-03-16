from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks.fgsm import FGSMAttack


class DummyDetectionModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stride = torch.tensor([32.0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Shape [B, N, 6] with a confidence-like channel at index 4.
        score = x.mean(dim=(1, 2, 3), keepdim=False).unsqueeze(-1)
        return score.unsqueeze(-1).repeat(1, 10, 6)


class FGSMSmokeTests(unittest.TestCase):
    def test_tensor_mode_preserves_shape_and_clamps(self) -> None:
        model = DummyDetectionModel().eval()
        attack = FGSMAttack(epsilon=0.01)
        image = torch.rand(1, 3, 65, 79)

        adv = attack.apply(image, model)

        self.assertIsInstance(adv, torch.Tensor)
        self.assertEqual(tuple(adv.shape), tuple(image.shape))
        self.assertFalse(model.training)
        self.assertGreaterEqual(float(adv.min().item()), 0.0)
        self.assertLessEqual(float(adv.max().item()), 1.0)

    def test_pipeline_mode_writes_output_tree(self) -> None:
        model = DummyDetectionModel().eval()
        attack = FGSMAttack(epsilon=0.01)

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            output = Path(tmp) / "output"
            nested = source / "nested"
            nested.mkdir(parents=True, exist_ok=True)
            image_path = nested / "sample.jpg"
            image = np.random.randint(0, 255, size=(63, 81, 3), dtype=np.uint8)
            cv2.imwrite(str(image_path), image)

            result_path = attack.apply(source, output, model=model)

            self.assertEqual(result_path, output)
            out_file = output / "nested" / "sample.jpg"
            self.assertTrue(out_file.exists())

            out_image = cv2.imread(str(out_file))
            self.assertIsNotNone(out_image)
            self.assertEqual(tuple(out_image.shape), tuple(image.shape))

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
