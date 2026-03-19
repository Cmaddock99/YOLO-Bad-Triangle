from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from lab.reporting import (
    build_comparison_rows,
    build_team_summary_payload,
    discover_framework_runs,
    generate_summary,
    render_markdown_report,
    write_team_summary,
)
from scripts import print_summary as print_summary_cli


class FrameworkReportingTest(unittest.TestCase):
    def _write_run(
        self,
        root: Path,
        run_name: str,
        *,
        attack: str,
        map50: float | None,
        defense: str = "none",
        seed: int = 42,
        model: str = "yolo",
    ) -> None:
        run_dir = root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "model": {"name": model},
                    "attack": {"name": attack},
                    "defense": {"name": defense},
                    "seed": seed,
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

    def test_generate_summary_interpretation_rules(self) -> None:
        baseline = {
            "predictions": {"total_detections": 100, "confidence": {"mean": 0.9}},
        }
        attack = {
            "predictions": {"total_detections": 70, "confidence": {"mean": 0.8}},
        }
        defense = {
            "predictions": {"total_detections": 72, "confidence": {"mean": 0.82}},
        }
        summary = generate_summary(baseline, attack, defense)
        self.assertEqual(summary["interpretation"], "Strong attack effect, weak defense")
        self.assertAlmostEqual(float(summary["attack_effectiveness"]), 0.3)
        self.assertAlmostEqual(float(summary["defense_recovery"]), 0.02)
        self.assertAlmostEqual(float(summary["confidence_drop"]), (0.9 - 0.8) / 0.9)

    def test_generate_summary_interpretation_insufficient_when_detection_missing(self) -> None:
        baseline = {"predictions": {"confidence": {"mean": 0.9}}}
        attack = {"predictions": {"confidence": {"mean": 0.8}}}
        summary = generate_summary(baseline, attack, None)
        self.assertIsNone(summary["attack_effectiveness"])
        self.assertEqual(summary["interpretation"], "Insufficient data for robustness interpretation")

    def test_print_summary_read_metrics_accepts_run_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            payload = print_summary_cli._read_metrics(str(root / "baseline_run"))
            self.assertIn("predictions", payload)
            self.assertIn("validation", payload)

    def test_print_summary_auto_discovers_latest_matching_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_old", attack="none", defense="none", seed=42, map50=0.6)
            self._write_run(root, "attack_old", attack="fgsm", defense="none", seed=42, map50=0.3)
            self._write_run(root, "baseline_new", attack="none", defense="none", seed=42, map50=0.62)
            self._write_run(root, "attack_new", attack="fgsm", defense="none", seed=42, map50=0.28)
            self._write_run(root, "defense_new", attack="fgsm", defense="blur", seed=42, map50=0.4)

            # Ensure deterministic "latest" ordering in auto mode.
            os.utime(root / "baseline_old", (1000, 1000))
            os.utime(root / "attack_old", (1001, 1001))
            os.utime(root / "baseline_new", (2000, 2000))
            os.utime(root / "attack_new", (2001, 2001))
            os.utime(root / "defense_new", (2002, 2002))

            baseline_dir, attack_dir, defense_dir = print_summary_cli._discover_auto_run_paths(root)
            self.assertEqual(baseline_dir.name, "baseline_new")
            self.assertEqual(attack_dir.name, "attack_new")
            self.assertEqual(defense_dir.name, "defense_new")

    def test_print_summary_auto_fail_fast_without_attack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_only", attack="none", defense="none", seed=42, map50=0.6)
            with self.assertRaises(ValueError) as context:
                print_summary_cli._discover_auto_run_paths(root)
            self.assertIn("Unable to auto-resolve attack run", str(context.exception))
            self.assertIn("scripts/print_summary.py --baseline", str(context.exception))

    def test_team_summary_payload_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            csv_path = report_root / "framework_run_summary.csv"
            csv_path.write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        "baseline_none,/tmp/baseline,yolo,none,none,42,8,8,21,0.76,missing,,,,",
                        "attack_blur,/tmp/blur,yolo,blur,none,42,8,8,16,0.72,missing,,,,",
                        "attack_fgsm,/tmp/fgsm,yolo,fgsm,none,42,8,8,17,0.75,missing,,,,",
                    ]
                ),
                encoding="utf-8",
            )
            (report_root / "summary_blur.txt").write_text(
                "----------------------------------\n"
                "Attack effectiveness: +23.8%\n"
                "Defense recovery: n/a\n"
                "Confidence drop: +5.0%\n"
                "\n"
                "Conclusion:\n"
                "Strong attack effect\n"
                "----------------------------------\n",
                encoding="utf-8",
            )
            payload = build_team_summary_payload(report_root)
            self.assertEqual(payload["total_attack_runs"], 2)
            strongest = payload["strongest_attack_by_detection_drop"]
            self.assertIsNotNone(strongest)
            self.assertEqual(strongest["attack"], "blur")
            json_path, md_path = write_team_summary(report_root)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

    def test_team_summary_baseline_requires_none_like_attack_and_defense(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            csv_path = report_root / "framework_run_summary.csv"
            csv_path.write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        "baseline_wrong,/tmp/baseline_wrong,identity,none,median_blur,42,8,8,40,0.76,missing,,,,",
                        "baseline_true,/tmp/baseline_true,yolo,identity,identity,42,8,8,50,0.76,missing,,,,",
                        "attack_blur,/tmp/blur,yolo,blur,none,42,8,8,25,0.72,missing,,,,",
                    ]
                ),
                encoding="utf-8",
            )
            payload = build_team_summary_payload(report_root)
            baseline = payload["baseline"]
            self.assertEqual(baseline["run_name"], "baseline_true")
            strongest = payload["strongest_attack_by_detection_drop"]
            self.assertIsNotNone(strongest)
            self.assertEqual(strongest["attack"], "blur")

    def test_build_comparison_rows_treats_identity_as_none_like(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_identity", attack="identity", map50=0.6)
            self._write_run(root, "fgsm_run", attack="fgsm", map50=0.2)
            records = discover_framework_runs(root)
            rows = build_comparison_rows(records)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mAP50_drop"]), 0.4)


if __name__ == "__main__":
    unittest.main()
