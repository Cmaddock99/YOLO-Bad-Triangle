from __future__ import annotations

import unittest

import numpy as np
import torch

from lab.attacks.framework_registry import build_attack_plugin, list_available_attack_plugins


class _DummyGradModel(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Keep shape >= 3 dims and last dim >= 5 for FGSM/PGD confidence proxy.
        return x


class FrameworkAttackPluginTest(unittest.TestCase):
    def setUp(self) -> None:
        self.image = np.full((64, 64, 3), 127, dtype=np.uint8)

    def test_plugin_list_is_non_empty(self) -> None:
        available = list_available_attack_plugins()
        self.assertGreater(len(available), 0, "At least one attack adapter plugin must be loaded")

    def test_plugin_registry_contains_phase7_attacks(self) -> None:
        available = set(list_available_attack_plugins())
        self.assertIn("fgsm", available)
        self.assertIn("pgd", available)
        self.assertIn("deepfool", available)
        self.assertIn("eot_pgd", available)
        self.assertIn("fgsm_center_mask", available)
        self.assertIn("fgsm_edge_mask", available)

    def test_fgsm_pgd_deepfool_adapters_run_with_torch_model(self) -> None:
        model = _DummyGradModel()
        fgsm = build_attack_plugin("fgsm", epsilon=0.005)
        pgd = build_attack_plugin("pgd", epsilon=0.01, alpha=0.002, steps=2, restarts=1)
        deepfool = build_attack_plugin("deepfool", epsilon=0.05, steps=2)

        fgsm_img, fgsm_meta = fgsm.apply(self.image, model=model)
        pgd_img, pgd_meta = pgd.apply(self.image, model=model, seed=7)
        df_img, df_meta = deepfool.apply(self.image, model=model)

        for img, meta, name in [
            (fgsm_img, fgsm_meta, "fgsm"),
            (pgd_img, pgd_meta, "pgd"),
            (df_img, df_meta, "deepfool"),
        ]:
            self.assertEqual(img.shape, self.image.shape)
            self.assertEqual(img.dtype, np.uint8)
            self.assertEqual(meta["attack"], name)

    def test_semantic_objective_metadata_is_reported(self) -> None:
        model = _DummyGradModel()
        attack = build_attack_plugin(
            "fgsm",
            epsilon=0.005,
            objective_mode="class_conditional_hiding",
            target_class=1,
            attack_roi=[0.25, 0.25, 0.5, 0.5],
        )
        _, meta = attack.apply(self.image, model=model)
        self.assertEqual(meta["objective_mode"], "class_conditional_hiding")
        self.assertEqual(meta["target_class"], 1)
        self.assertEqual(meta["attack_roi"], [0.25, 0.25, 0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
