from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image
import torch

from lab.attacks.framework_registry import build_attack_plugin, list_available_attack_plugins


class _DummyGradModel(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Keep shape >= 3 dims and last dim >= 5 for FGSM/PGD confidence proxy.
        return x


def _write_patch_artifact(
    path: Path,
    *,
    size: tuple[int, int],
    color_rgb: tuple[int, int, int],
) -> None:
    height, width = size
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    rgb[:, :] = np.asarray(color_rgb, dtype=np.uint8)
    Image.fromarray(rgb, mode="RGB").save(path)


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

    def test_pretrained_patch_registered_with_alias(self) -> None:
        available = set(list_available_attack_plugins())
        self.assertIn("pretrained_patch", available)
        self.assertIn("adv_patch", available)

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "patch.png"
            _write_patch_artifact(artifact, size=(8, 6), color_rgb=(255, 0, 0))
            canonical = build_attack_plugin("pretrained_patch", artifact_path=str(artifact))
            alias = build_attack_plugin("adv_patch", artifact_path=str(artifact))

        self.assertEqual(type(canonical), type(alias))


class _StubBoxes:
    def __init__(self, xyxy: list[list[float]], cls: list[float] | None = None) -> None:
        self.xyxy = np.asarray(xyxy, dtype=np.float32)
        classes = cls if cls is not None else [0.0] * len(xyxy)
        self.cls = np.asarray(classes, dtype=np.float32)


class _StubResult:
    def __init__(self, boxes: _StubBoxes) -> None:
        self.boxes = boxes


class _StubInnerYOLO:
    def __init__(self, xyxy: list[list[float]], cls: list[float] | None = None) -> None:
        self._boxes = _StubBoxes(xyxy, cls=cls)
        self.last_kwargs: dict[str, object] | None = None

    def predict(self, **kwargs: object) -> list[_StubResult]:
        self.last_kwargs = dict(kwargs)
        return [_StubResult(self._boxes)]


class _StubYOLOAdapter:
    def __init__(self, xyxy: list[list[float]], cls: list[float] | None = None) -> None:
        self._model = _StubInnerYOLO(xyxy, cls=cls)


class PretrainedPatchAttackTest(unittest.TestCase):
    def setUp(self) -> None:
        self.image = np.full((64, 64, 3), 127, dtype=np.uint8)

    def _build_attack(
        self,
        *,
        size: tuple[int, int] = (10, 8),
        color_rgb: tuple[int, int, int] = (255, 0, 0),
        **kwargs: object,
    ):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        artifact = Path(tmp.name) / "patch.png"
        _write_patch_artifact(artifact, size=size, color_rgb=color_rgb)
        return build_attack_plugin("pretrained_patch", artifact_path=str(artifact), **kwargs)

    def test_pretrained_patch_output_shape_dtype_and_metadata_keys(self) -> None:
        attack = self._build_attack()

        attacked, meta = attack.apply(self.image, model=None, seed=7)

        self.assertEqual(attacked.shape, self.image.shape)
        self.assertEqual(attacked.dtype, np.uint8)
        self.assertEqual(meta["attack"], "pretrained_patch")
        self.assertEqual(
            set(meta),
            {
                "attack",
                "artifact_path",
                "artifact_sha256",
                "artifact_size",
                "applied_patch_size",
                "placement_mode",
                "fallback_mode",
                "clean_detect_conf",
                "clean_detect_iou",
                "prediction_metadata",
            },
        )

    def test_pretrained_patch_is_deterministic(self) -> None:
        attack = self._build_attack()

        out_a, meta_a = attack.apply(self.image, model=None, seed=1)
        out_b, meta_b = attack.apply(self.image, model=None, seed=999)

        np.testing.assert_array_equal(out_a, out_b)
        self.assertEqual(meta_a["prediction_metadata"], meta_b["prediction_metadata"])

    def test_pretrained_patch_center_fallback_and_bgr_conversion(self) -> None:
        attack = self._build_attack(size=(10, 8), color_rgb=(255, 0, 0))

        attacked, meta = attack.apply(np.zeros((20, 20, 3), dtype=np.uint8), model=None)

        prediction_meta = meta["prediction_metadata"]
        self.assertEqual(prediction_meta["top"], 5)
        self.assertEqual(prediction_meta["left"], 6)
        self.assertFalse(prediction_meta["person_found"])
        self.assertTrue(prediction_meta["fallback_used"])
        np.testing.assert_array_equal(attacked[5, 6], np.array([0, 0, 255], dtype=np.uint8))

    def test_pretrained_patch_placement_uses_largest_person_torso(self) -> None:
        attack = self._build_attack(size=(20, 20), color_rgb=(0, 255, 0))
        model = _StubYOLOAdapter([[100, 50, 200, 300], [5, 10, 15, 20]])
        image = np.zeros((320, 320, 3), dtype=np.uint8)
        image[:, :] = np.array([10, 20, 30], dtype=np.uint8)

        attacked, meta = attack.apply(image, model=model)

        prediction_meta = meta["prediction_metadata"]
        self.assertEqual(prediction_meta["top"], 127)
        self.assertEqual(prediction_meta["left"], 140)
        self.assertTrue(prediction_meta["person_found"])
        self.assertFalse(prediction_meta["fallback_used"])
        np.testing.assert_array_equal(attacked[127, 140], np.array([0, 255, 0], dtype=np.uint8))

        assert model._model.last_kwargs is not None
        source = model._model.last_kwargs["source"]
        self.assertIsInstance(source, np.ndarray)
        np.testing.assert_array_equal(source[0, 0], np.array([30, 20, 10], dtype=np.uint8))

    def test_pretrained_patch_downscales_to_fit_small_images(self) -> None:
        attack = self._build_attack(size=(80, 120), color_rgb=(0, 0, 255))
        image = np.zeros((40, 60, 3), dtype=np.uint8)

        attacked, meta = attack.apply(image, model=None)

        prediction_meta = meta["prediction_metadata"]
        self.assertEqual(prediction_meta["applied_patch_size"], [40, 60])
        self.assertEqual(prediction_meta["top"], 0)
        self.assertEqual(prediction_meta["left"], 0)
        np.testing.assert_array_equal(attacked[0, 0], np.array([255, 0, 0], dtype=np.uint8))
        np.testing.assert_array_equal(attacked[-1, -1], np.array([255, 0, 0], dtype=np.uint8))


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


class WS4AttackCorrectnessTest(unittest.TestCase):
    """WS4 tests: CPU generator fix, DR seed determinism, threshold constant, objective contracts."""

    def setUp(self) -> None:
        self.image = np.full((64, 64, 3), 127, dtype=np.uint8)

    def test_square_sign_generated_on_cpu_not_device(self) -> None:
        """SquareAttack must not pass a device= arg to torch.randint for the sign tensor.

        Previously: generator=generator, device=device was passed, causing CUDA/MPS crash
        when generator is CPU-pinned but device is GPU.  The fix generates on CPU then .to(device).
        """
        from lab.attacks.square_adapter import SquareAttack
        attack = SquareAttack(eps=0.05, n_queries=2, p_init=0.5)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(42)
        model = _DummyDetectionModel()
        # Run on CPU — this should complete without error (device mismatch would raise).
        x = torch.zeros(1, 3, 64, 64)
        result, _ = attack._apply_to_tensor(x, model, generator=generator)
        self.assertEqual(result.shape, x.shape)

    def test_dr_seed_produces_identical_output(self) -> None:
        """DispersionReduction with the same seed must produce identical outputs."""
        from lab.attacks.dispersion_reduction_adapter import _DispersionReductionCore

        class _TinyModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.model = torch.nn.ModuleList([torch.nn.Identity()])

            def forward(self, x):
                return x

        impl = _DispersionReductionCore(epsilon=0.1, steps=2, alpha=0.05, layer_indices=[0])
        x0 = torch.full((1, 3, 32, 32), 0.5)
        model = _TinyModel()
        out_a = impl.apply_to_tensor(x0.clone(), model, seed=7)
        out_b = impl.apply_to_tensor(x0.clone(), model, seed=7)
        self.assertTrue(torch.allclose(out_a, out_b), "Same seed must give identical DR output")

    def test_dr_different_seeds_produce_different_output(self) -> None:
        """Different seeds must produce different DR outputs (probabilistic check)."""
        from lab.attacks.dispersion_reduction_adapter import _DispersionReductionCore

        class _TinyModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.model = torch.nn.ModuleList([torch.nn.Identity()])

            def forward(self, x):
                return x

        impl = _DispersionReductionCore(epsilon=0.1, steps=2, alpha=0.05, layer_indices=[0])
        x0 = torch.full((1, 3, 32, 32), 0.5)
        model = _TinyModel()
        out_a = impl.apply_to_tensor(x0.clone(), model, seed=1)
        out_b = impl.apply_to_tensor(x0.clone(), model, seed=2)
        self.assertFalse(torch.allclose(out_a, out_b), "Different seeds must give different DR output")

    def test_detection_conf_threshold_constant_visible(self) -> None:
        """_DETECTION_CONF_THRESHOLD must be a named constant in both square and cw modules."""
        from lab.attacks import square_adapter, cw_adapter
        self.assertEqual(square_adapter._DETECTION_CONF_THRESHOLD, 0.1)
        self.assertEqual(cw_adapter._DETECTION_CONF_THRESHOLD, 0.1)

    def test_fgsm_uses_contract_objective_constants(self) -> None:
        """FGSM loss function must branch on contract constants, not raw string literals."""
        import lab.attacks.fgsm_adapter as fgsm_mod
        import inspect
        source = inspect.getsource(fgsm_mod.FGSMAttack._compute_loss)
        # Must reference the contract constant, not the bare string
        self.assertIn("ATTACK_OBJECTIVE_TARGET_CLASS", source)
        self.assertIn("ATTACK_OBJECTIVE_CLASS_HIDE", source)
        self.assertNotIn('"target_class_misclassification"', source)
        self.assertNotIn('"class_conditional_hiding"', source)

    def test_deepfool_uses_contract_objective_constants(self) -> None:
        """DeepFool _detection_confidence must use contract constants, not raw strings."""
        import lab.attacks.deepfool_adapter as df_mod
        import inspect
        source = inspect.getsource(df_mod.DeepFoolAttack._detection_confidence)
        self.assertIn("ATTACK_OBJECTIVE_TARGET_CLASS", source)
        self.assertIn("ATTACK_OBJECTIVE_CLASS_HIDE", source)
        self.assertNotIn('"target_class_misclassification"', source)
        self.assertNotIn('"class_conditional_hiding"', source)

    def test_cw_metadata_includes_confidence_used_false(self) -> None:
        """CW _apply_to_tensor metadata must include confidence_used=False."""
        from lab.attacks.cw_adapter import CWAttack
        model = _DummyCWModel()
        attack = CWAttack(c=1.0, max_iter=2, lr=0.01, binary_search_steps=1, early_stop=False)
        x = torch.zeros(1, 3, 64, 64)
        with mock.patch.object(
            CWAttack, "_count_detections",
            side_effect=[0],  # baseline=0 → skipped path
        ):
            _, meta = attack._apply_to_tensor(x, model)
        # skipped path does not include confidence_used
        # Test the non-skipped path instead
        with mock.patch.object(
            CWAttack, "_count_detections",
            side_effect=[5] + [3] * 20,
        ):
            _, meta = attack._apply_to_tensor(x, model)
        self.assertIn("confidence_used", meta)
        self.assertFalse(meta["confidence_used"])


if __name__ == "__main__":
    unittest.main()
