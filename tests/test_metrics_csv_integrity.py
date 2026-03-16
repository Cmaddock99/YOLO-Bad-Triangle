from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.eval.metrics import _parse_detection_stats, append_run_metrics


class MetricsCsvIntegrityTests(unittest.TestCase):
    def test_append_run_metrics_upgrades_schema_and_preserves_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run_a"
            labels_dir = run_dir / "labels"
            val_dir = run_dir / "val"
            labels_dir.mkdir(parents=True, exist_ok=True)
            val_dir.mkdir(parents=True, exist_ok=True)
            (labels_dir / "img1.txt").write_text("0 0.5 0.5 0.2 0.2 0.9\n")
            (val_dir / "metrics.json").write_text(
                '{"precision": 0.5, "recall": 0.4, "mAP50": 0.3, "mAP50-95": 0.2}'
            )

            csv_path = root / "metrics_summary.csv"

            append_run_metrics(
                run_dir=run_dir,
                csv_path=csv_path,
                run_name="run_a",
                model="yolo8",
                attack="none",
                defense="none",
                conf=0.25,
                iou=0.7,
                imgsz=640,
                seed=42,
                extra_metadata={
                    "validation_enabled": True,
                    "config_fingerprint": "abc123",
                },
            )
            append_run_metrics(
                run_dir=run_dir,
                csv_path=csv_path,
                run_name="run_b",
                model="yolo8",
                attack="fgsm",
                defense="none",
                conf=0.25,
                iou=0.7,
                imgsz=640,
                seed=42,
                extra_metadata={
                    "validation_enabled": True,
                    "config_fingerprint": "def456",
                    "new_probe_field": "probe",
                },
            )

            with csv_path.open(newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = list(reader.fieldnames or [])

            self.assertEqual(len(rows), 2)
            self.assertIn("config_fingerprint", fieldnames)
            self.assertIn("new_probe_field", fieldnames)
            self.assertEqual(rows[0]["run_name"], "run_a")
            self.assertEqual(rows[1]["run_name"], "run_b")
            self.assertEqual(rows[0]["new_probe_field"], "")
            self.assertEqual(rows[1]["new_probe_field"], "probe")

    def test_confidence_stats_ignore_non_prediction_text_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run_a"
            labels_dir = run_dir / "labels"
            labels_dir.mkdir(parents=True, exist_ok=True)
            (labels_dir / "img1.txt").write_text("0 0.5 0.5 0.2 0.2 0.9\n")
            # This should not be parsed because only prediction label paths are allowed.
            (run_dir / "notes.txt").write_text("0 0.1 0.1 0.1 0.1 0.01\n")

            stats = _parse_detection_stats(run_dir)
            self.assertEqual(stats["images_with_detections"], 1)
            self.assertEqual(stats["total_detections"], 1)
            self.assertAlmostEqual(float(stats["avg_conf"]), 0.9)

    def test_confidence_stats_require_six_column_prediction_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run_bad_conf"
            labels_dir = run_dir / "labels"
            labels_dir.mkdir(parents=True, exist_ok=True)
            # Five-column rows are valid GT labels but not prediction labels with confidence.
            (labels_dir / "img1.txt").write_text("0 0.5 0.5 0.2 0.2\n")

            stats = _parse_detection_stats(run_dir)
            self.assertEqual(stats["images_with_detections"], 1)
            self.assertEqual(stats["total_detections"], 1)
            self.assertIsNone(stats["avg_conf"])
            self.assertIsNone(stats["median_conf"])


if __name__ == "__main__":
    unittest.main()
