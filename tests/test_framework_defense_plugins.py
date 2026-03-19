from __future__ import annotations

import unittest

import numpy as np

from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins


class FrameworkDefensePluginTest(unittest.TestCase):
    def test_registry_contains_new_plugins(self) -> None:
        available = set(list_available_defense_plugins())
        self.assertIn("preprocess_median_blur", available)
        self.assertIn("confidence_filter", available)

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


if __name__ == "__main__":
    unittest.main()
