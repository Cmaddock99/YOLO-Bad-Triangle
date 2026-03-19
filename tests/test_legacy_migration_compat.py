from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from lab.migration import write_legacy_compat_artifacts


class LegacyMigrationCompatTest(unittest.TestCase):
    def _write_framework_run(
        self,
        runs_root: Path,
        run_name: str,
        *,
        attack: str,
        defense: str = "none",
    ) -> None:
        run_dir = runs_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "model": {"name": "yolo11n"},
                    "attack": {"name": attack, "params": {"epsilon": 0.03}},
                    "defense": {"name": defense, "params": {}},
                    "run": {
                        "conf": 0.25,
                        "iou": 0.7,
                        "imgsz": 640,
                        "session_id": "session_1",
                        "started_at_utc": "2026-03-19T00:00:00Z",
                    },
                    "seed": 42,
                    "config_fingerprint": "abc123",
                    "validation": {"enabled": True},
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "metrics.json").write_text(
            json.dumps(
                {
                    "predictions": {
                        "images_with_detections": 2,
                        "total_detections": 7,
                        "confidence": {
                            "mean": 0.6,
                            "median": 0.61,
                            "p25": 0.5,
                            "p75": 0.7,
                        },
                    },
                    "validation": {
                        "status": "ok",
                        "precision": 0.8,
                        "recall": 0.7,
                        "mAP50": 0.6,
                        "mAP50-95": 0.5,
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_write_legacy_compat_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "framework_runs"
            output_root = root / "compat"
            self._write_framework_run(runs_root, "baseline_none", attack="none")
            self._write_framework_run(runs_root, "attack_fgsm", attack="fgsm")

            result = write_legacy_compat_artifacts(
                runs_root=runs_root,
                output_root=output_root,
            )
            self.assertEqual(result.row_count, 2)
            self.assertTrue(result.metrics_csv.is_file())
            self.assertTrue(result.experiment_table_md.is_file())

            with result.metrics_csv.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertIn("MODEL", rows[0])
            self.assertIn("mAP50", rows[0])
            self.assertIn("fgsm", {row["attack"] for row in rows})


if __name__ == "__main__":
    unittest.main()
