from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import sweep_and_report


class SweepAndReportScriptTest(unittest.TestCase):
    def test_parse_attacks_from_csv(self) -> None:
        attacks = sweep_and_report._parse_attacks("fgsm, blur ,pgd")
        self.assertEqual(attacks, ["fgsm", "blur", "pgd"])

    def test_parse_attacks_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            sweep_and_report._parse_attacks(" , , ")

    def test_default_max_images_for_presets(self) -> None:
        self.assertEqual(sweep_and_report._default_max_images("smoke"), 8)
        self.assertEqual(sweep_and_report._default_max_images("full"), 0)

    def test_experiment_command_contains_required_overrides(self) -> None:
        command = sweep_and_report._experiment_command(
            python_bin="./.venv/bin/python",
            config=Path("configs/lab_framework_phase5.yaml"),
            output_root=Path("outputs/framework_runs/sweep_x"),
            run_name="attack_fgsm",
            attack_name="fgsm",
            defense_name="none",
            seed=42,
            max_images=8,
            validation_enabled=False,
        )
        rendered = " ".join(command)
        self.assertIn("src/lab/runners/run_experiment.py", rendered)
        self.assertIn("runner.run_name=attack_fgsm", rendered)
        self.assertIn("attack.name=fgsm", rendered)
        self.assertIn("summary.enabled=false", rendered)

    def test_metrics_exists_helper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            self.assertFalse(sweep_and_report._metrics_exists(run_dir))
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            self.assertTrue(sweep_and_report._metrics_exists(run_dir))

    def test_generate_legacy_compat_command(self) -> None:
        command = sweep_and_report._generate_legacy_compat_command(
            python_bin="./.venv/bin/python",
            runs_root=Path("outputs/framework_runs/sweep_x"),
            output_root=Path("outputs/week1_test"),
        )
        rendered = " ".join(command)
        self.assertIn("scripts/generate_legacy_compat_artifacts.py", rendered)
        self.assertIn("outputs/framework_runs/sweep_x", rendered)
        self.assertIn("outputs/week1_test", rendered)


if __name__ == "__main__":
    unittest.main()
