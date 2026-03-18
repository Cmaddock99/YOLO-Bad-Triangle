from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lab.reporting import build_comparison_rows, discover_framework_runs, render_markdown_report


class FrameworkReportingTest(unittest.TestCase):
    def _write_run(self, root: Path, run_name: str, *, attack: str, map50: float | None) -> None:
        run_dir = root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "model": {"name": "yolo"},
                    "attack": {"name": attack},
                    "defense": {"name": "none"},
                    "seed": 42,
                    "prediction_record_count": 5,
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "metrics.json").write_text(
            json.dumps(
                {
                    "predictions": {
                        "images_with_detections": 5,
                        "total_detections": 10,
                        "confidence": {"mean": 0.5},
                    },
                    "validation": {
                        "status": "complete",
                        "precision": 0.7,
                        "recall": 0.6,
                        "mAP50": map50,
                        "mAP50-95": 0.4,
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_discover_and_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            self._write_run(root, "fgsm_run", attack="fgsm", map50=0.2)
            records = discover_framework_runs(root)
            self.assertEqual(len(records), 2)
            rows = build_comparison_rows(records)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mAP50_drop"]), 0.4)

    def test_markdown_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            records = discover_framework_runs(root)
            report = render_markdown_report(records)
            self.assertIn("# Framework Run Comparison Report", report)
            self.assertIn("baseline_run", report)


if __name__ == "__main__":
    unittest.main()
