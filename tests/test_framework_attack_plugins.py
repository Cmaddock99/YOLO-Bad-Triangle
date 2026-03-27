from __future__ import annotations

import unittest
from unittest import mock

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


class _DummyDetectionModel(torch.nn.Module):
    """Returns a fixed high-confidence detection tensor for any input."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Shape (batch, anchors, 85): last dim has conf at index 4
        batch = x.shape[0]
        # 1 anchor, conf=0.9
        out = torch.zeros(batch, 1, 85)
        out[:, :, 4] = 0.9
        return out


class SquareAttackTest(unittest.TestCase):
    def setUp(self) -> None:
        self.image = np.full((64, 64, 3), 127, dtype=np.uint8)

    def test_square_attack_registered(self) -> None:
        available = set(list_available_attack_plugins())
        self.assertIn("square", available)

    def test_square_attack_output_shape_and_dtype(self) -> None:
        model = _DummyDetectionModel()
        attack = build_attack_plugin("square", eps=0.05, n_queries=10, p_init=0.1)
        out_img, meta = attack.apply(self.image, model=model, seed=42)
        self.assertEqual(out_img.shape, self.image.shape)
        self.assertEqual(out_img.dtype, np.uint8)
        self.assertEqual(meta["attack"], "square")
        self.assertIn("queries_used", meta)

    def test_square_attack_is_black_box(self) -> None:
        """Square Attack must never call .backward() or access .grad."""
        backward_called = []
        grad_accessed = []

        class _GradSentinelModel(torch.nn.Module):
            def forward(self, x: torch.Tensor) -> torch.Tensor:
                # Record any gradient-related access
                if x.requires_grad:
                    backward_called.append(True)
                out = torch.zeros(x.shape[0], 1, 85)
                out[:, :, 4] = 0.9
                return out

        model = _GradSentinelModel()
        attack = build_attack_plugin("square", eps=0.05, n_queries=5, p_init=0.1)
        attack.apply(self.image, model=model, seed=0)

        # A black-box attack never enables requires_grad on its input
        self.assertEqual(backward_called, [],
                         "Square Attack must not enable requires_grad on inputs")

    def test_square_attack_is_deterministic_with_seed(self) -> None:
        model = _DummyDetectionModel()
        attack = build_attack_plugin("square", eps=0.05, n_queries=10, p_init=0.1)
        img_a, _ = attack.apply(self.image, model=model, seed=123)
        img_b, _ = attack.apply(self.image, model=model, seed=123)
        np.testing.assert_array_equal(img_a, img_b)


class _DummyCWModel(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch = x.shape[0]
        out = torch.zeros(batch, 1, 85, device=x.device, dtype=x.dtype)
        out[:, :, 4] = x.mean(dim=(1, 2, 3)).unsqueeze(-1)
        return out


class CWAttackBehaviorTest(unittest.TestCase):
    def test_cw_marks_success_when_detections_drop_without_hitting_zero(self) -> None:
        image = np.full((64, 64, 3), 127, dtype=np.uint8)
        model = _DummyCWModel()
        attack = build_attack_plugin("cw", c=10.0, max_iter=4, lr=0.01, binary_search_steps=1, device="cpu")

        with mock.patch(
            "lab.attacks.cw_adapter.CWAttack._count_detections",
            side_effect=[5] + [3] * 32,
        ):
            attacked, meta = attack.apply(image, model=model)

        self.assertEqual(attacked.shape, image.shape)
        self.assertEqual(attacked.dtype, np.uint8)
        self.assertTrue(meta.get("success"))


if __name__ == "__main__":
    unittest.main()
