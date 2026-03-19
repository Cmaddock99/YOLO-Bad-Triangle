from __future__ import annotations

import unittest

import numpy as np

from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    image_bgr_to_model_tensor,
    model_tensor_to_image_bgr,
    run_wrapper_on_bgr_image,
)


class DPCUNetWrapperIOTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
