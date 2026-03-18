from __future__ import annotations

import math
import unittest

from lab.eval.framework_metrics import (
    sanitize_validation_metrics,
    summarize_prediction_metrics,
    validation_status,
)


class FrameworkMetricsTest(unittest.TestCase):
    def test_sanitize_validation_metrics_filters_nan(self) -> None:
        cleaned = sanitize_validation_metrics(
            {
                "precision": 0.4,
                "recall": "nan",
                "mAP50": math.inf,
                "mAP50-95": "0.2",
            }
        )
        self.assertEqual(cleaned["precision"], 0.4)
        self.assertIsNone(cleaned["recall"])
        self.assertIsNone(cleaned["mAP50"])
        self.assertEqual(cleaned["mAP50-95"], 0.2)
        self.assertEqual(validation_status(cleaned), "partial")

    def test_summarize_prediction_metrics(self) -> None:
        rows = [
            {
                "image_id": "a.jpg",
                "boxes": [[0.0, 0.0, 1.0, 1.0]],
                "scores": [0.9],
                "class_ids": [0],
                "metadata": {},
            },
            {
                "image_id": "b.jpg",
                "boxes": [],
                "scores": [],
                "class_ids": [],
                "metadata": {},
            },
        ]
        summary = summarize_prediction_metrics(rows)
        self.assertEqual(summary["image_count"], 2)
        self.assertEqual(summary["images_with_detections"], 1)
        self.assertEqual(summary["images_without_detections"], 1)
        self.assertEqual(summary["total_detections"], 1)
        self.assertAlmostEqual(summary["detections_per_image_mean"], 0.5)
        self.assertEqual(summary["confidence"]["count"], 1)
        self.assertAlmostEqual(summary["confidence"]["mean"], 0.9)


if __name__ == "__main__":
    unittest.main()
