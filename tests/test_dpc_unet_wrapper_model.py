from __future__ import annotations

import unittest

import torch

from lab.defenses.dpc_unet_wrapper import DPCUNet, sinusoidal_timestep_embedding


class DPCUNetWrapperModelTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
