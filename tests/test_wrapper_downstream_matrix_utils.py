from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.verify_wrapper_downstream_matrix import _detector_stats


class _DummyBoxes:
    def __init__(self, values: list[float]) -> None:
        self.conf = torch.tensor(values, dtype=torch.float32)


class _DummyResult:
    def __init__(self, values: list[float]) -> None:
        self.boxes = _DummyBoxes(values)


class _DummyDetector:
    def __init__(self, rows: list[list[float]]) -> None:
        self._rows = rows

    def predict(self, **kwargs: object) -> list[_DummyResult]:
        del kwargs
        return [_DummyResult(values) for values in self._rows]


class WrapperDownstreamMatrixUtilTests(unittest.TestCase):
    def test_detector_stats_handles_confidence_values(self) -> None:
        detector = _DummyDetector([[0.9, 0.7], [], [0.3]])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            stats = _detector_stats(detector, source, conf=0.25, iou=0.7, imgsz=640)
        self.assertEqual(stats["images_with_detections"], 2.0)
        self.assertEqual(stats["total_detections"], 3.0)
        self.assertAlmostEqual(stats["mean_conf"], (0.9 + 0.7 + 0.3) / 3.0)

    def test_detector_stats_handles_empty_predictions(self) -> None:
        detector = _DummyDetector([[]])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            stats = _detector_stats(detector, source, conf=0.25, iou=0.7, imgsz=640)
        self.assertEqual(stats["images_with_detections"], 0.0)
        self.assertEqual(stats["total_detections"], 0.0)
        self.assertEqual(stats["mean_conf"], 0.0)


if __name__ == "__main__":
    unittest.main()
