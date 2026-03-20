from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_experiment import _legacy_to_framework_args


class LegacyToFrameworkArgsTest(unittest.TestCase):
    def test_maps_attack_key(self) -> None:
        result = _legacy_to_framework_args(["attack=fgsm"])
        self.assertIn("--set", result)
        idx = result.index("--set")
        self.assertEqual(result[idx + 1], "attack.name=fgsm")

    def test_maps_defense_key(self) -> None:
        result = _legacy_to_framework_args(["defense=median"])
        self.assertIn("--set", result)
        self.assertIn("defense.name=median", result)

    def test_maps_model_key(self) -> None:
        result = _legacy_to_framework_args(["model=yolov8n.pt"])
        self.assertIn("model.params.model=yolov8n.pt", result)

    def test_maps_conf_key(self) -> None:
        result = _legacy_to_framework_args(["conf=0.25"])
        self.assertIn("predict.conf=0.25", result)

    def test_passes_through_set_overrides(self) -> None:
        result = _legacy_to_framework_args(["--set", "runner.seed=7"])
        self.assertIn("--set", result)
        self.assertIn("runner.seed=7", result)

    def test_appends_default_config_when_not_provided(self) -> None:
        result = _legacy_to_framework_args(["attack=blur"])
        self.assertIn("--config", result)
        idx = result.index("--config")
        self.assertEqual(result[idx + 1], "configs/lab_framework_phase5.yaml")

    def test_does_not_append_default_config_when_provided(self) -> None:
        result = _legacy_to_framework_args(["config=configs/my_config.yaml"])
        self.assertIn("--config", result)
        idx = result.index("--config")
        self.assertEqual(result[idx + 1], "configs/my_config.yaml")
        # Should only appear once
        self.assertEqual(result.count("--config"), 1)

    def test_unrecognized_keys_are_not_dropped(self) -> None:
        result = _legacy_to_framework_args(["unknown_key=value"])
        # Unrecognized keys pass through as --set overrides
        self.assertIn("--set", result)
        self.assertIn("unknown_key=value", result)

    def test_dry_run_true_adds_flag(self) -> None:
        result = _legacy_to_framework_args(["dry_run=true"])
        self.assertIn("--dry-run", result)

    def test_dry_run_false_does_not_add_flag(self) -> None:
        result = _legacy_to_framework_args(["dry_run=false"])
        self.assertNotIn("--dry-run", result)


if __name__ == "__main__":
    unittest.main()
