from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from lab.migration import write_legacy_compat_artifacts


class AdapterMetricSemanticsTest(unittest.TestCase):
    def test_legacy_adapter_preserves_metric_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "framework_runs" / "run_1"
            run_dir.mkdir(parents=True, exist_ok=True)
            metrics_payload = {
                "predictions": {
                    "images_with_detections": 4,
                    "total_detections": 9,
                    "confidence": {"mean": 0.55, "median": 0.56, "p25": 0.5, "p75": 0.6},
                },
                "validation": {
                    "status": "complete",
                    "precision": 0.71,
                    "recall": 0.63,
                    "mAP50": 0.58,
                    "mAP50-95": 0.44,
                },
            }
            summary_payload = {
                "model": {"name": "yolo11n"},
                "attack": {"name": "fgsm", "params": {"eps": 0.03}},
                "defense": {"name": "none", "params": {}},
                "run": {"conf": 0.25, "iou": 0.7, "imgsz": 640, "session_id": "sess_1", "started_at_utc": "now"},
                "seed": 7,
                "config_fingerprint": "fp_1",
                "validation": {"enabled": True},
            }
            (run_dir / "metrics.json").write_text(json.dumps(metrics_payload), encoding="utf-8")
            (run_dir / "run_summary.json").write_text(json.dumps(summary_payload), encoding="utf-8")

            output_root = root / "compat"
            write_legacy_compat_artifacts(runs_root=root / "framework_runs", output_root=output_root)

            with (output_root / "metrics_summary.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(float(row["precision"]), metrics_payload["validation"]["precision"])
            self.assertEqual(float(row["recall"]), metrics_payload["validation"]["recall"])
            self.assertEqual(float(row["mAP50"]), metrics_payload["validation"]["mAP50"])
            self.assertEqual(float(row["mAP50-95"]), metrics_payload["validation"]["mAP50-95"])
            self.assertEqual(int(float(row["total_detections"])), metrics_payload["predictions"]["total_detections"])
            self.assertEqual(
                int(float(row["images_with_detections"])), metrics_payload["predictions"]["images_with_detections"]
            )


if __name__ == "__main__":
    unittest.main()
