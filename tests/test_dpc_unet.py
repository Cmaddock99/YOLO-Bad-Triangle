from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    image_bgr_to_model_tensor,
    model_tensor_to_image_bgr,
    run_wrapper_on_bgr_image,
    sinusoidal_timestep_embedding,
)
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins


class DPCUNetModelTests(unittest.TestCase):
    def test_sinusoidal_embedding_shape(self) -> None:
        t = torch.tensor([0.0, 10.0, 100.0])
        emb = sinusoidal_timestep_embedding(t, dim=64)
        self.assertEqual(tuple(emb.shape), (3, 64))

    def test_forward_accepts_scalar_and_tensor_timestep(self) -> None:
        model = DPCUNet().eval()
        x = torch.zeros((2, 3, 64, 64), dtype=torch.float32)
        y_scalar = model(x, timestep=100)
        y_tensor = model(x, timestep=torch.tensor([10.0, 20.0]))
        self.assertEqual(tuple(y_scalar.shape), (2, 3, 64, 64))
        self.assertEqual(tuple(y_tensor.shape), (2, 3, 64, 64))
        self.assertTrue(torch.isfinite(y_scalar).all().item())
        self.assertTrue(torch.isfinite(y_tensor).all().item())


class DPCUNetIOTests(unittest.TestCase):
    def test_roundtrip_conversion_preserves_shape(self) -> None:
        image = np.random.randint(0, 256, size=(48, 64, 3), dtype=np.uint8)
        cfg = WrapperInputConfig(color_order="rgb", scaling="zero_one", normalize=False)
        tensor = image_bgr_to_model_tensor(image, cfg=cfg)
        rebuilt = model_tensor_to_image_bgr(tensor, cfg=cfg)
        self.assertEqual(rebuilt.shape, image.shape)
        self.assertEqual(rebuilt.dtype, np.uint8)

    def test_minus_one_one_with_normalize_roundtrip(self) -> None:
        image = np.random.randint(0, 256, size=(32, 40, 3), dtype=np.uint8)
        cfg = WrapperInputConfig(color_order="bgr", scaling="minus_one_one", normalize=True)
        tensor = image_bgr_to_model_tensor(image, cfg=cfg)
        rebuilt = model_tensor_to_image_bgr(tensor, cfg=cfg)
        self.assertEqual(rebuilt.shape, image.shape)
        self.assertEqual(rebuilt.dtype, np.uint8)

    def test_wrapper_run_returns_image_and_finite_stats(self) -> None:
        image = np.full((32, 32, 3), 127, dtype=np.uint8)
        model = DPCUNet()
        cfg = WrapperInputConfig(color_order="rgb", scaling="zero_one", normalize=False)
        output, stats = run_wrapper_on_bgr_image(image, model, timestep=100, cfg=cfg, device="cpu")
        self.assertEqual(output.shape, image.shape)
        self.assertIsInstance(stats["finite"], bool)
        self.assertIn("tensor_mean", stats)

    def test_wrapper_run_is_deterministic_for_same_input(self) -> None:
        image = np.full((40, 48, 3), 96, dtype=np.uint8)
        model = DPCUNet()
        cfg = WrapperInputConfig(color_order="bgr", scaling="zero_one", normalize=True)
        out1, _ = run_wrapper_on_bgr_image(image, model, timestep=50, cfg=cfg, device="cpu")
        out2, _ = run_wrapper_on_bgr_image(image, model, timestep=50, cfg=cfg, device="cpu")
        self.assertTrue(np.array_equal(out1, out2))


class DPCUNetAdapterTests(unittest.TestCase):
    def _write_checkpoint(self, path: Path) -> None:
        model = DPCUNet()
        torch.save(model.state_dict(), path)

    def test_plugin_registered(self) -> None:
        names = list_available_defense_plugins()
        self.assertIn("preprocess_dpc_unet", names)
        self.assertIn("c_dog", names)

    def test_preprocess_runs_with_valid_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin(
                "c_dog",
                checkpoint_path=str(ckpt),
                timestep=50,
                color_order="bgr",
                scaling="zero_one",
                normalize=True,
            )
            image = np.full((40, 60, 3), 120, dtype=np.uint8)
            output, meta = defense.preprocess(image)
            self.assertEqual(output.shape, image.shape)
            self.assertEqual(meta["defense"], "preprocess_dpc_unet")
            self.assertTrue(meta["finite"])

    def test_preprocess_rejects_non_finite_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin("preprocess_dpc_unet", checkpoint_path=str(ckpt))
            image = np.zeros((32, 32, 3), dtype=np.uint8)
            with patch(
                "lab.defenses.preprocess_dpc_unet_adapter.run_wrapper_on_bgr_image",
                return_value=(image.copy(), {"finite": False, "tensor_min": 0.0, "tensor_max": 0.0, "tensor_mean": 0.0, "tensor_std": 0.0}),
            ):
                with self.assertRaises(RuntimeError):
                    defense.preprocess(image)


if __name__ == "__main__":
    unittest.main()
