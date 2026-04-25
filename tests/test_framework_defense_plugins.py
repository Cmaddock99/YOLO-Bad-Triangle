from __future__ import annotations

import unittest

import numpy as np

from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins


class FrameworkDefensePluginTest(unittest.TestCase):
    def test_plugin_list_is_non_empty(self) -> None:
        available = list_available_defense_plugins()
        self.assertGreater(len(available), 0, "At least one defense adapter plugin must be loaded")

    def test_registry_contains_new_plugins(self) -> None:
        available = set(list_available_defense_plugins())
        self.assertIn("preprocess_median_blur", available)
        self.assertIn("blind_patch_recover", available)
        self.assertIn("confidence_filter", available)
        self.assertIn("oracle_patch_recover", available)

    def test_core_only_plugin_list_excludes_extra_defense_aliases(self) -> None:
        available = set(list_available_defense_plugins(include_extra=False))
        self.assertIn("none", available)
        self.assertIn("identity", available)
        self.assertIn("bit_depth", available)
        self.assertIn("jpeg_preprocess", available)
        self.assertIn("median_preprocess", available)
        self.assertNotIn("c_dog", available)
        self.assertNotIn("c_dog_ensemble", available)
        self.assertNotIn("blind_patch_recover", available)
        self.assertNotIn("confidence_filter", available)
        self.assertNotIn("oracle_patch_recover", available)
        self.assertNotIn("random_resize", available)

    def test_core_only_build_succeeds_for_core_defense(self) -> None:
        defense = build_defense_plugin(
            "preprocess_median_blur",
            include_extra=False,
            kernel_size=3,
        )
        self.assertEqual(type(defense).__name__, "PreprocessMedianBlurDefenseAdapter")

    def test_core_only_build_rejects_extra_defense(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "Unsupported defense plugin 'confidence_filter'"
        ):
            build_defense_plugin("confidence_filter", include_extra=False, threshold=0.5)

    def test_preprocess_median_blur_runs(self) -> None:
        defense = build_defense_plugin("preprocess_median_blur", kernel_size=3)
        image = np.full((16, 16, 3), 127, dtype=np.uint8)
        processed, meta = defense.preprocess(image)
        self.assertEqual(processed.shape, image.shape)
        self.assertEqual(processed.dtype, np.uint8)
        self.assertEqual(meta["defense"], "preprocess_median_blur")

    def test_confidence_filter_postprocess(self) -> None:
        defense = build_defense_plugin("confidence_filter", threshold=0.5)
        rows = [
            {
                "image_id": "img.jpg",
                "boxes": [[0, 0, 10, 10], [1, 1, 11, 11]],
                "scores": [0.9, 0.2],
                "class_ids": [0, 1],
                "metadata": {"source": "test"},
            }
        ]
        filtered, meta = defense.postprocess(rows)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["scores"], [0.9])
        self.assertEqual(filtered[0]["class_ids"], [0])
        self.assertEqual(meta["removed_detections"], 1)

    def test_blind_patch_recover_inpaints_visible_patch_region(self) -> None:
        defense = build_defense_plugin(
            "blind_patch_recover",
            score_percentile=98.0,
            min_area_frac=0.01,
            max_area_frac=0.25,
            dilate_px=4,
            inpaint_radius=3,
            inpaint_method="telea",
        )
        image = np.full((64, 64, 3), 120, dtype=np.uint8)
        checker = np.indices((20, 20)).sum(axis=0) % 2
        patch = np.where(
            checker[..., None] == 0,
            np.array([255, 0, 0], dtype=np.uint8),
            np.array([0, 255, 255], dtype=np.uint8),
        )
        image[20:40, 20:40] = patch

        processed, meta = defense.preprocess(image)

        self.assertEqual(processed.shape, image.shape)
        self.assertEqual(processed.dtype, np.uint8)
        self.assertTrue(meta["applied"])
        self.assertEqual(meta["defense"], "blind_patch_recover")
        self.assertEqual(meta["stage"], "preprocess")
        self.assertIn("component_bbox_xywh", meta)
        self.assertIn("mask_area_px", meta)
        self.assertIn("inpaint_method", meta)
        self.assertGreater(np.abs(processed[20:40, 20:40].astype(int) - image[20:40, 20:40].astype(int)).sum(), 0)

    def test_blind_patch_recover_noops_on_low_anomaly_image(self) -> None:
        defense = build_defense_plugin("blind_patch_recover")
        image = np.full((32, 32, 3), 77, dtype=np.uint8)

        processed, meta = defense.preprocess(image)

        np.testing.assert_array_equal(processed, image)
        self.assertFalse(meta["applied"])
        self.assertEqual(meta["defense"], "blind_patch_recover")

    def test_oracle_patch_recover_inpaints_attack_region(self) -> None:
        defense = build_defense_plugin("oracle_patch_recover", dilate_px=0, inpaint_radius=3, inpaint_method="telea")
        image = np.zeros((24, 24, 3), dtype=np.uint8)
        image[4:12, 4:12] = np.array([255, 255, 255], dtype=np.uint8)

        processed, meta = defense.preprocess(
            image,
            attack_metadata={"top": 4, "left": 4, "applied_patch_size": [8, 8]},
        )

        self.assertEqual(processed.shape, image.shape)
        self.assertEqual(processed.dtype, np.uint8)
        self.assertTrue(meta["applied"])
        self.assertTrue(meta["oracle_upper_bound"])
        self.assertFalse(np.array_equal(processed[6, 6], np.array([255, 255, 255], dtype=np.uint8)))

    def test_oracle_patch_recover_passthrough_without_attack_metadata(self) -> None:
        defense = build_defense_plugin("oracle_patch_recover")
        image = np.full((8, 8, 3), 17, dtype=np.uint8)

        processed, meta = defense.preprocess(image)

        np.testing.assert_array_equal(processed, image)
        self.assertFalse(meta["applied"])


if __name__ == "__main__":
    unittest.main()
