from __future__ import annotations

import unittest

from scripts import generate_cycle_report


class CycleReportComparabilityTest(unittest.TestCase):
    def test_build_markdown_includes_comparability_notes(self) -> None:
        cycles = [
            {
                "cycle_id": "cycle_legacy",
                "started_at": "2026-03-23T00:00:00",
                "finished_at": "2026-03-23T01:00:00",
                "pipeline_semantics": "defense_then_attack",
                "top_attacks": ["pgd"],
                "top_defenses": ["confidence_filter"],
                "validation_results": {
                    "validate_baseline": {"attack": None, "defense": None, "detections": 1000, "mAP50": 0.6},
                    "validate_atk_pgd": {"attack": "pgd", "defense": "none", "detections": 700, "mAP50": 0.45},
                },
            },
            {
                "cycle_id": "cycle_current",
                "started_at": "2026-03-26T00:00:00",
                "finished_at": "2026-03-26T01:00:00",
                "pipeline_semantics": "attack_then_defense",
                "top_attacks": ["deepfool", "eot_pgd", "blur"],
                "top_defenses": ["bit_depth", "jpeg_preprocess"],
                "validation_results": {
                    "validate_baseline": {"attack": None, "defense": None, "detections": 1400, "mAP50": 0.6002},
                    "validate_atk_deepfool": {"attack": "deepfool", "defense": "none", "detections": 600, "mAP50": 0.22},
                    "validate_deepfool_bit_depth": {
                        "attack": "deepfool",
                        "defense": "bit_depth",
                        "detections": 650,
                        "mAP50": 0.24,
                    },
                },
            },
        ]

        markdown = generate_cycle_report.build_markdown(cycles)
        self.assertIn("Comparability Notes", markdown)
        self.assertIn("Current Catalogue Trends", markdown)
        self.assertIn("Legacy Catalogue Trends", markdown)
        self.assertIn("attack_then_defense", markdown)


class WS3CycleReportTest(unittest.TestCase):
    """WS3 tests: Phase 4 dedup precedence and numeric zero-guard."""

    def _cycle(self, validation_results: dict) -> dict:
        return {
            "cycle_id": "test_cycle",
            "started_at": "2026-04-08T00:00:00",
            "finished_at": "2026-04-08T01:00:00",
            "pipeline_semantics": "attack_then_defense",
            "top_attacks": ["fgsm"],
            "top_defenses": ["c_dog"],
            "validation_results": validation_results,
        }

    def test_phase4_validate_row_wins_over_smoke_row_for_same_key(self) -> None:
        """When both a smoke row and a validate_ row exist for the same (attack, defense),
        the validate_ row must appear in the CSV output (Phase 4 beats Phase 1).
        """
        cycle = self._cycle({
            # Smoke run (Phase 1): lower mAP50
            "fgsm__c_dog__smoke": {
                "attack": "fgsm",
                "defense": "c_dog",
                "detections": 300,
                "mAP50": 0.1,
            },
            # Phase 4 validate run: higher mAP50 — should win
            "validate_atk_fgsm__c_dog": {
                "attack": "fgsm",
                "defense": "c_dog",
                "detections": 800,
                "mAP50": 0.55,
            },
        })
        rows = generate_cycle_report._build_csv_rows([cycle])
        defended_rows = [r for r in rows if r["defense"] == "c_dog"]
        self.assertEqual(len(defended_rows), 1)
        self.assertAlmostEqual(float(defended_rows[0]["defended_mAP50"]), 0.55)

    def test_smoke_row_used_when_no_validate_row_exists(self) -> None:
        """When only a smoke row exists, it must appear in the output unchanged."""
        cycle = self._cycle({
            "fgsm__c_dog__smoke": {
                "attack": "fgsm",
                "defense": "c_dog",
                "detections": 300,
                "mAP50": 0.1,
            },
        })
        rows = generate_cycle_report._build_csv_rows([cycle])
        defended_rows = [r for r in rows if r["defense"] == "c_dog"]
        self.assertEqual(len(defended_rows), 1)
        self.assertAlmostEqual(float(defended_rows[0]["defended_mAP50"]), 0.1)

    def test_zero_baseline_detections_does_not_raise(self) -> None:
        """baseline_dets=0 must not cause a ZeroDivisionError; drop_pct should be empty."""
        cycle = self._cycle({
            "validate_baseline": {"attack": None, "defense": None, "detections": 0, "mAP50": 0.0},
            "validate_atk_fgsm": {"attack": "fgsm", "defense": "none", "detections": 0, "mAP50": 0.0},
        })
        rows = generate_cycle_report._build_csv_rows([cycle])
        attack_rows = [r for r in rows if r["defense"] == "none"]
        self.assertEqual(len(attack_rows), 1)
        # detection_drop_pct must be empty (no division performed)
        self.assertEqual(attack_rows[0]["detection_drop_pct"], "")


if __name__ == "__main__":
    unittest.main()
