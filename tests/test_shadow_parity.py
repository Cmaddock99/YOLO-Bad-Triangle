from __future__ import annotations

import unittest

from lab.migration.shadow_parity import (
    ValidationGateConfig,
    compare_shadow_runs,
    enforce_validation_gate,
    normalize_run_metadata,
)


class ShadowParityTest(unittest.TestCase):
    def test_normalize_run_metadata_none_like(self) -> None:
        normalized = normalize_run_metadata(
            {
                "run_name": " My Run ",
                "model": "YOLOv8n.pt",
                "attack": "identity",
                "defense": "",
                "seed": "42",
            }
        )
        self.assertEqual(normalized["run_name"], "my-run")
        self.assertEqual(normalized["model"], "yolo8n")
        self.assertEqual(normalized["attack"], "none")
        self.assertEqual(normalized["defense"], "none")
        self.assertEqual(normalized["seed"], 42)

    def test_compare_shadow_runs_pass(self) -> None:
        legacy = {
            "metadata": {"run_name": "shadow_x", "model": "yolo26n", "attack": "fgsm", "defense": "none", "seed": 42},
            "predictions": {
                "images_with_detections": 10,
                "total_detections": 25,
                "avg_conf": 0.5,
                "median_conf": 0.51,
                "p25_conf": 0.45,
                "p75_conf": 0.58,
            },
            "validation": {"precision": 0.6, "recall": 0.5, "mAP50": 0.4, "mAP50-95": 0.3},
        }
        framework = {
            "metadata": {"run_name": "shadow_x", "model": "yolo26n", "attack": "fgsm", "defense": "none", "seed": 42},
            "predictions": {
                "images_with_detections": 10,
                "total_detections": 25,
                "avg_conf": 0.5001,
                "median_conf": 0.509,
                "p25_conf": 0.451,
                "p75_conf": 0.579,
            },
            "validation": {"precision": 0.6, "recall": 0.5, "mAP50": 0.4, "mAP50-95": 0.3},
        }
        result = compare_shadow_runs(
            legacy,
            framework,
            max_detection_relative_delta_pct=5.0,
            max_conf_relative_delta_pct=5.0,
        )
        self.assertTrue(result["parity_pass"])
        self.assertGreaterEqual(float(result["parity_score"]), 90.0)

    def test_validation_gate_fails_when_missing_metrics(self) -> None:
        errors = enforce_validation_gate(
            attack_name="fgsm",
            legacy_row={"precision": "", "recall": "", "mAP50": "", "mAP50-95": ""},
            framework_metrics={"validation": {"enabled": False, "status": "missing"}},
            gate_config=ValidationGateConfig(required_attacks={"fgsm", "pgd"}),
        )
        self.assertTrue(errors)
        self.assertTrue(any("legacy missing required validation metric" in item for item in errors))
        self.assertTrue(any("framework validation.enabled=false" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
