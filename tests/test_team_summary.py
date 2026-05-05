from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from lab.reporting.team_summary import (
    build_team_summary_payload,
    render_team_summary_markdown,
    write_team_summary,
)


CSV_HEADER = [
    "run_name",
    "run_dir",
    "model",
    "attack",
    "defense",
    "seed",
    "run_role",
    "authority",
    "source_phase",
    "dataset_scope",
    "authoritative_metric",
    "pipeline_profile",
    "total_detections",
    "avg_confidence",
    "validation_status",
    "mAP50",
]


def _row(**overrides: object) -> dict[str, str]:
    defaults = {
        "run_name": "",
        "run_dir": "",
        "model": "yolo",
        "attack": "none",
        "defense": "none",
        "seed": "42",
        "run_role": "",
        "authority": "authoritative",
        "source_phase": "phase4",
        "dataset_scope": "full",
        "authoritative_metric": "mAP50",
        "pipeline_profile": "yolo11n_lab_v1",
        "total_detections": "100",
        "avg_confidence": "0.8",
        "validation_status": "complete",
        "mAP50": "0.55",
    }
    defaults.update({k: str(v) for k, v in overrides.items()})
    return defaults


def _write_report(report_root: Path, rows: list[dict[str, str]]) -> None:
    report_root.mkdir(parents=True, exist_ok=True)
    csv_path = report_root / "framework_run_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class TeamSummaryPayloadTest(unittest.TestCase):
    def test_payload_selects_phase4_over_phase1_for_same_attack(self) -> None:
        rows = [
            _row(run_name="baseline"),
            _row(
                run_name="attack_blur_phase1",
                attack="blur",
                run_role="attack_only",
                source_phase="phase1",
                total_detections="80",
                mAP50="",
                validation_status="missing",
            ),
            _row(
                run_name="attack_blur_phase4",
                attack="blur",
                run_role="attack_only",
                source_phase="phase4",
                total_detections="60",
                mAP50="0.42",
                validation_status="complete",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            payload = build_team_summary_payload(report_root)

        self.assertEqual(payload["total_attack_runs"], 1)
        blur = payload["attacks_ranked"][0]
        self.assertEqual(blur["run_name"], "attack_blur_phase4")
        self.assertEqual(blur["source_phase"], "phase4")
        self.assertAlmostEqual(blur["map50"] or 0.0, 0.42)

    def test_payload_ranks_ranked_result_when_all_rows_authoritative(self) -> None:
        rows = [
            _row(run_name="baseline"),
            _row(
                run_name="attack_fgsm",
                attack="fgsm",
                run_role="attack_only",
                total_detections="70",
                mAP50="0.50",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            payload = build_team_summary_payload(report_root)

        self.assertEqual(payload["local_context"]["semantic_status"], "ranked_result")
        self.assertIsNotNone(payload["strongest_attack_by_detection_drop"])

    def test_payload_marks_diagnostic_when_only_proxy_evidence(self) -> None:
        rows = [
            _row(run_name="baseline", validation_status="missing", mAP50=""),
            _row(
                run_name="attack_fgsm",
                attack="fgsm",
                run_role="attack_only",
                total_detections="70",
                authority="diagnostic",
                source_phase="phase1",
                validation_status="missing",
                mAP50="",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            payload = build_team_summary_payload(report_root)

        self.assertEqual(payload["local_context"]["semantic_status"], "diagnostic")

    def test_markdown_includes_ranking_table_and_status_note_when_diagnostic(self) -> None:
        rows = [
            _row(run_name="baseline"),
            _row(
                run_name="attack_blur",
                attack="blur",
                run_role="attack_only",
                authority="diagnostic",
                source_phase="phase1",
                validation_status="missing",
                mAP50="",
                total_detections="80",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            payload = build_team_summary_payload(report_root)
            md = render_team_summary_markdown(payload)

        self.assertIn("# Team Summary", md)
        self.assertIn("## Local Attack Ranking", md)
        self.assertIn("`attack_blur`", md)
        self.assertIn("`blur`", md)
        self.assertIn("Status note:", md)

    def test_write_team_summary_emits_both_artifacts_atomically(self) -> None:
        rows = [
            _row(run_name="baseline"),
            _row(
                run_name="attack_pgd",
                attack="pgd",
                run_role="attack_only",
                total_detections="50",
                mAP50="0.30",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            json_path, md_path = write_team_summary(report_root)

            self.assertTrue(json_path.is_file())
            self.assertTrue(md_path.is_file())
            self.assertFalse(json_path.with_suffix(".json.tmp").exists())
            self.assertFalse(md_path.with_suffix(".md.tmp").exists())

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["total_attack_runs"], 1)
            self.assertEqual(payload["attacks_ranked"][0]["attack"], "pgd")

    def test_payload_raises_when_no_baseline(self) -> None:
        rows = [
            _row(
                run_name="attack_only",
                attack="blur",
                run_role="attack_only",
                defense="none",
            ),
        ]
        # Strip baseline by overriding attack to non-none; no none/none row exists.
        rows[0]["attack"] = "blur"
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            _write_report(report_root, rows)
            with self.assertRaises(ValueError):
                build_team_summary_payload(report_root)


if __name__ == "__main__":
    unittest.main()
