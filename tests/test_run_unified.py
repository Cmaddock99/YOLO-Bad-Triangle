from __future__ import annotations

import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from scripts import run_unified
from lab.runners import cli_utils


class RunUnifiedTest(unittest.TestCase):
    def test_build_run_experiment_command_appends_set_overrides(self) -> None:
        command = cli_utils.build_run_experiment_command(
            Path("/repo"),
            "configs/default.yaml",
            ["attack.name=fgsm", "runner.seed=7"],
            python_bin="python",
        )

        self.assertEqual(
            command,
            [
                "python",
                "/repo/src/lab/runners/run_experiment.py",
                "--config",
                "configs/default.yaml",
                "--set",
                "attack.name=fgsm",
                "--set",
                "runner.seed=7",
            ],
        )

    def test_build_repo_python_command_targets_requested_script(self) -> None:
        command = cli_utils.build_repo_python_command(
            Path("/repo"),
            "scripts/sweep_and_report.py",
            ["--config", "configs/default.yaml"],
            python_bin="python3",
        )

        self.assertEqual(
            command,
            [
                "python3",
                "/repo/scripts/sweep_and_report.py",
                "--config",
                "configs/default.yaml",
            ],
        )

    def test_sweep_forwards_extended_flags(self) -> None:
        captured: list[list[str]] = []

        def _fake_run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
            del component, env
            captured.append(command)
            return 0

        argv = [
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
            "--attacks",
            "fgsm,pgd",
            "--defenses",
            "c_dog",
            "--workers",
            "2",
            "--phases",
            "2,3,4",
            "--seed",
            "123",
            "--resume",
            "--skip-errors",
        ]
        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        command = captured[0]
        rendered = " ".join(command)
        self.assertIn("--defenses c_dog", rendered)
        self.assertIn("--workers 2", rendered)
        self.assertIn("--phases 2,3,4", rendered)
        self.assertIn("--seed 123", rendered)
        self.assertIn("--resume", rendered)
        self.assertIn("--skip-errors", rendered)

    def test_run_one_adds_seed_override(self) -> None:
        captured: list[list[str]] = []

        def _fake_run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
            del component, env
            captured.append(command)
            return 0

        argv = [
            "run_unified.py",
            "run-one",
            "--config",
            "configs/default.yaml",
            "--seed",
            "11",
        ]
        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        self.assertIn("runner.seed=11", " ".join(captured[0]))


if __name__ == "__main__":
    unittest.main()
