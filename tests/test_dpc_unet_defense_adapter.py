from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from lab.defenses.dpc_unet_wrapper import DPCUNet
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins


class DPCUNetDefenseAdapterTests(unittest.TestCase):
    def _write_checkpoint(self, path: Path) -> None:
        model = DPCUNet()
        torch.save(model.state_dict(), path)

    def test_plugin_registered(self) -> None:
        names = list_available_defense_plugins()
        self.assertIn("preprocess_dpc_unet", names)
        self.assertIn("dpc_unet_wrapper", names)

    def test_preprocess_runs_with_valid_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin(
                "preprocess_dpc_unet",
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
