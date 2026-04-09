from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from lab.eval.bootstrap import bootstrap_paired_ci
from lab.eval.framework_metrics import (
    VALIDATION_STATUS_COMPLETE,
    VALIDATION_STATUS_MISSING,
    is_validation_success,
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

    def test_is_validation_success_helper(self) -> None:
        self.assertTrue(is_validation_success(VALIDATION_STATUS_COMPLETE))
        self.assertFalse(is_validation_success(VALIDATION_STATUS_MISSING))


class BootstrapSkippedLinesTest(unittest.TestCase):
    """Tests for the skipped_lines visibility fix in bootstrap_paired_ci."""

    def _write_jsonl(self, path: Path, records: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(records) + "\n", encoding="utf-8")

    def _valid_record(self, image_id: str, score: float = 0.9) -> str:
        return json.dumps({
            "image_id": image_id,
            "boxes": [[0.1, 0.1, 0.5, 0.5]],
            "scores": [score],
            "class_ids": [0],
            "metadata": {},
        })

    def test_skipped_lines_zero_on_clean_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.jsonl"
            attack = Path(tmp) / "attack.jsonl"
            ids = [f"img_{i}.jpg" for i in range(10)]
            self._write_jsonl(baseline, [self._valid_record(i, 0.9) for i in ids])
            self._write_jsonl(attack, [self._valid_record(i, 0.6) for i in ids])
            result = bootstrap_paired_ci(baseline, attack)
            self.assertEqual(result["skipped_lines"], 0)

    def test_skipped_lines_nonzero_on_corrupt_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.jsonl"
            attack = Path(tmp) / "attack.jsonl"
            ids = [f"img_{i}.jpg" for i in range(10)]
            # Insert two corrupt lines into baseline
            lines = [self._valid_record(i, 0.9) for i in ids]
            lines.insert(3, "NOT_VALID_JSON{{{")
            lines.insert(7, "another bad line")
            self._write_jsonl(baseline, lines)
            self._write_jsonl(attack, [self._valid_record(i, 0.6) for i in ids])
            result = bootstrap_paired_ci(baseline, attack)
            self.assertGreaterEqual(result["skipped_lines"], 2)

    def test_skipped_lines_present_in_result_dict(self) -> None:
        """skipped_lines key must always be present even when no lines are skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.jsonl"
            attack = Path(tmp) / "attack.jsonl"
            baseline.write_text("", encoding="utf-8")
            attack.write_text("", encoding="utf-8")
            result = bootstrap_paired_ci(baseline, attack)
            self.assertIn("skipped_lines", result)

    def test_skipped_lines_counts_across_both_files(self) -> None:
        """Corrupt lines in both baseline and attack are summed."""
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.jsonl"
            attack = Path(tmp) / "attack.jsonl"
            ids = [f"img_{i}.jpg" for i in range(6)]
            baseline_lines = [self._valid_record(i, 0.9) for i in ids] + ["BAD_JSON_B"]
            attack_lines = [self._valid_record(i, 0.6) for i in ids] + ["BAD_JSON_A"]
            self._write_jsonl(baseline, baseline_lines)
            self._write_jsonl(attack, attack_lines)
            result = bootstrap_paired_ci(baseline, attack)
            self.assertEqual(result["skipped_lines"], 2)


if __name__ == "__main__":
    unittest.main()
