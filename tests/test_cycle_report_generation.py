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


if __name__ == "__main__":
    unittest.main()
