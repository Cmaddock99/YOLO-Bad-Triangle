from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks import build_attack
from lab.attacks.registry import list_available_attacks


class DummyDetectionModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stride = torch.tensor([32.0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        score = x.mean(dim=(1, 2, 3), keepdim=False).unsqueeze(-1)
        return score.unsqueeze(-1).repeat(1, 10, 6)


class AttackVariantTests(unittest.TestCase):
    def test_new_variants_are_registered(self) -> None:
        available = set(list_available_attacks())
        expected = {
            "fgsm_center_mask",
            "fgsm_edge_mask",
            "blur_anisotropic",
            "noise_blockwise",
            "deepfool_band_limited",
        }
        self.assertTrue(expected.issubset(available))

    def test_variants_write_mirrored_outputs_with_valid_images(self) -> None:
        model = DummyDetectionModel().eval()
        variants = [
            ("fgsm_center_mask", {"epsilon": 0.008, "radius_fraction": 0.3}),
            ("fgsm_edge_mask", {"epsilon": 0.008, "edge_threshold": 30, "edge_dilate": 1}),
            ("blur_anisotropic", {"kernel_x": 17, "kernel_y": 3}),
            ("noise_blockwise", {"stddev": 10.0, "block_size": 16, "scale_jitter": 0.3}),
            (
                "deepfool_band_limited",
                {"epsilon": 0.9, "steps": 2, "stripe_period": 24, "stripe_width": 8, "blur_kernel": 5},
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            nested = source / "nested"
            nested.mkdir(parents=True, exist_ok=True)
            sample = nested / "sample.jpg"
            image = np.random.randint(0, 255, size=(64, 80, 3), dtype=np.uint8)
            cv2.imwrite(str(sample), image)

            for name, params in variants:
                attack = build_attack(name, params)
                output = Path(tmp) / f"out_{name}"
                if name.startswith("fgsm_"):
                    attack.apply(source, output, seed=42, model=model)
                else:
                    attack.apply(source, output, seed=42)

                out_file = output / "nested" / "sample.jpg"
                self.assertTrue(out_file.exists(), f"Missing output for {name}")
                out_img = cv2.imread(str(out_file))
                self.assertIsNotNone(out_img, f"Unreadable output for {name}")
                self.assertEqual(out_img.shape, image.shape, f"Shape mismatch for {name}")
                self.assertEqual(out_img.dtype, np.uint8, f"dtype mismatch for {name}")
                self.assertGreaterEqual(int(out_img.min()), 0)
                self.assertLessEqual(int(out_img.max()), 255)

    def test_stochastic_variants_are_seed_deterministic(self) -> None:
        deterministic_variants = [
            ("noise_blockwise", {"stddev": 12.0, "block_size": 16, "scale_jitter": 0.5}),
            (
                "deepfool_band_limited",
                {"epsilon": 0.8, "steps": 3, "stripe_period": 20, "stripe_width": 10, "blur_kernel": 5},
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir(parents=True, exist_ok=True)
            img_path = source / "img.jpg"
            image = np.random.randint(0, 255, size=(72, 88, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), image)

            for name, params in deterministic_variants:
                attack = build_attack(name, params)
                out_a = Path(tmp) / f"{name}_a"
                out_b = Path(tmp) / f"{name}_b"
                attack.apply(source, out_a, seed=123)
                attack.apply(source, out_b, seed=123)
                file_a = out_a / "img.jpg"
                file_b = out_b / "img.jpg"
                hash_a = hashlib.sha256(file_a.read_bytes()).hexdigest()
                hash_b = hashlib.sha256(file_b.read_bytes()).hexdigest()
                self.assertEqual(hash_a, hash_b, f"Expected deterministic output for {name}")


if __name__ == "__main__":
    unittest.main()
