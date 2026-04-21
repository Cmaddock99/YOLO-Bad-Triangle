from __future__ import annotations

import importlib
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TrainingScriptCompatTest(unittest.TestCase):
    def test_old_and_new_run_training_ritual_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.run_training_ritual")
        new_mod = importlib.import_module("scripts.training.run_training_ritual")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_train_from_signal_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.train_from_signal")
        new_mod = importlib.import_module("scripts.training.train_from_signal")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_export_training_data_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.export_training_data")
        new_mod = importlib.import_module("scripts.training.export_training_data")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_evaluate_checkpoint_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.evaluate_checkpoint")
        new_mod = importlib.import_module("scripts.training.evaluate_checkpoint")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_train_dpc_unet_local_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.train_dpc_unet_local")
        new_mod = importlib.import_module("scripts.training.train_dpc_unet_local")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_train_dpc_unet_feature_loss_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.train_dpc_unet_feature_loss")
        new_mod = importlib.import_module("scripts.training.train_dpc_unet_feature_loss")
        self.assertIs(old_mod, new_mod)

    def test_old_paths_still_expose_expected_symbols(self) -> None:
        from scripts.export_training_data import _resolve_runs_root
        from scripts.run_training_ritual import _check_signal
        from scripts.train_from_signal import _gate_passed

        self.assertEqual(_resolve_runs_root.__name__, "_resolve_runs_root")
        self.assertEqual(_check_signal.__name__, "_check_signal")
        self.assertEqual(_gate_passed.__name__, "_gate_passed")

    def test_root_training_entrypoint_help_smoke(self) -> None:
        cases = (
            ("scripts/run_training_ritual.py", "--max-age-hours"),
            ("scripts/train_from_signal.py", "--checkpoint-a"),
            ("scripts/export_training_data.py", "--from-signal"),
            ("scripts/evaluate_checkpoint.py", "--checkpoint-b"),
            ("scripts/train_dpc_unet_local.py", "--training-zip"),
            ("scripts/train_dpc_unet_feature_loss.py", "--feature-weight"),
        )

        env = os.environ.copy()
        env["PYTHONPATH"] = "src"

        for script_path, expected_substring in cases:
            with self.subTest(script_path=script_path):
                result = subprocess.run(
                    [sys.executable, script_path, "--help"],
                    cwd=REPO_ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, msg=result.stderr)
                self.assertIn(expected_substring, result.stdout)


if __name__ == "__main__":
    unittest.main()
