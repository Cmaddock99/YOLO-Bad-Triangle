from __future__ import annotations

import unittest

from lab.runners.run_experiment import _normalized_config_for_output


class FrameworkConfigNormalizationTest(unittest.TestCase):
    def test_null_names_normalize_to_none(self) -> None:
        cfg = {
            "model": {"name": "yolo"},
            "data": {"source_dir": "coco/val2017_subset500/images"},
            "attack": {"name": None, "params": {}},
            "defense": {"name": None, "params": {}},
        }
        normalized = _normalized_config_for_output(cfg)
        self.assertEqual(normalized["attack"]["name"], "none")
        self.assertEqual(normalized["defense"]["name"], "none")

    def test_non_empty_names_preserved(self) -> None:
        cfg = {
            "attack": {"name": "fgsm", "params": {"epsilon": 0.01}},
            "defense": {"name": "confidence_filter", "params": {"threshold": 0.6}},
            "parity": {"enabled": True, "legacy_csv_path": "outputs/metrics_summary.csv"},
            "summary": {"enabled": True},
        }
        normalized = _normalized_config_for_output(cfg)
        self.assertEqual(normalized["attack"]["name"], "fgsm")
        self.assertEqual(normalized["defense"]["name"], "confidence_filter")
        self.assertTrue(normalized["parity"]["enabled"])
        self.assertEqual(normalized["parity"]["legacy_csv_path"], "outputs/metrics_summary.csv")
        self.assertTrue(normalized["summary"]["enabled"])


if __name__ == "__main__":
    unittest.main()
