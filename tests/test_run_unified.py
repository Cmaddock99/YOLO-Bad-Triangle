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
    def _captured_command(self, argv: list[str]) -> list[str]:
        captured: list[list[str]] = []

        def _fake_run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
            del component, env
            captured.append(command)
            return 0

        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        return captured[0]

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

    def test_build_run_experiment_command_accepts_profile(self) -> None:
        command = cli_utils.build_run_experiment_command(
            Path("/repo"),
            None,
            ["attack.name=fgsm"],
            profile="yolo11n_lab_v1",
            python_bin="python",
        )

        self.assertEqual(
            command,
            [
                "python",
                "/repo/src/lab/runners/run_experiment.py",
                "--profile",
                "yolo11n_lab_v1",
                "--set",
                "attack.name=fgsm",
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

    def test_sweep_forwards_dry_run_and_list_plugins(self) -> None:
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
            "--dry-run",
            "--list-plugins",
        ]
        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        rendered = " ".join(captured[0])
        self.assertIn("--dry-run", rendered)
        self.assertIn("--list-plugins", rendered)

    def test_sweep_forwards_repeatable_set_overrides(self) -> None:
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
            "pretrained_patch",
            "--set",
            "attack.params.artifact_path=/tmp/patch.png",
            "--set",
            "attack.params.clean_detect_conf=0.6",
        ]
        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        rendered = " ".join(captured[0])
        self.assertIn("--set attack.params.artifact_path=/tmp/patch.png", rendered)
        self.assertIn("--set attack.params.clean_detect_conf=0.6", rendered)

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

    def test_run_one_profile_forwards_profile_flag(self) -> None:
        captured: list[list[str]] = []

        def _fake_run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
            del component, env
            captured.append(command)
            return 0

        argv = [
            "run_unified.py",
            "run-one",
            "--profile",
            "yolo11n_lab_v1",
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
        rendered = " ".join(captured[0])
        self.assertIn("--profile yolo11n_lab_v1", rendered)
        self.assertIn("runner.seed=11", rendered)

    def test_sweep_profile_forwards_profile_flag(self) -> None:
        captured: list[list[str]] = []

        def _fake_run(command: list[str], *, component: str, env: dict[str, str] | None = None) -> int:
            del component, env
            captured.append(command)
            return 0

        argv = [
            "run_unified.py",
            "sweep",
            "--profile",
            "yolo11n_lab_v1",
            "--attacks",
            "fgsm,pgd",
        ]
        with patch("sys.argv", argv):
            with patch("scripts.run_unified.resolve_python_bin", return_value="python"):
                with patch("scripts.run_unified.with_src_pythonpath", return_value={}):
                    with patch("scripts.run_unified._run", side_effect=_fake_run):
                        with self.assertRaises(SystemExit) as exit_ctx:
                            run_unified.main()
                        self.assertEqual(int(exit_ctx.exception.code), 0)

        self.assertEqual(len(captured), 1)
        self.assertIn("--profile yolo11n_lab_v1", " ".join(captured[0]))

    def test_run_one_rejects_profile_and_config_together(self) -> None:
        argv = [
            "run_unified.py",
            "run-one",
            "--config",
            "configs/default.yaml",
            "--profile",
            "yolo11n_lab_v1",
        ]
        with patch("sys.argv", argv):
            with self.assertRaises(SystemExit) as exit_ctx:
                run_unified.main()
        self.assertEqual(int(exit_ctx.exception.code), 2)

    def test_sweep_rejects_profile_and_config_together(self) -> None:
        argv = [
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
            "--profile",
            "yolo11n_lab_v1",
        ]
        with patch("sys.argv", argv):
            with self.assertRaises(SystemExit) as exit_ctx:
                run_unified.main()
        self.assertEqual(int(exit_ctx.exception.code), 2)

    def test_sweep_forwards_no_failure_gallery(self) -> None:
        command = self._captured_command([
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
            "--no-failure-gallery",
        ])

        self.assertIn("--no-failure-gallery", " ".join(command))

    def test_sweep_forwards_no_compat_dashboard(self) -> None:
        command = self._captured_command([
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
            "--no-compat-dashboard",
        ])

        self.assertIn("--no-compat-dashboard", " ".join(command))

    def test_sweep_omits_optional_report_extra_flags_when_unspecified(self) -> None:
        command = self._captured_command([
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
        ])

        rendered = " ".join(command)
        self.assertNotIn("--failure-gallery", rendered)
        self.assertNotIn("--no-failure-gallery", rendered)
        self.assertNotIn("--compat-dashboard", rendered)
        self.assertNotIn("--no-compat-dashboard", rendered)

    def test_sweep_forwards_reporting_metadata_flags(self) -> None:
        command = self._captured_command([
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
            "--reporting-dataset-scope",
            "smoke",
            "--reporting-authority",
            "diagnostic",
            "--reporting-source-phase",
            "phase1",
        ])

        rendered = " ".join(command)
        self.assertIn("--reporting-dataset-scope smoke", rendered)
        self.assertIn("--reporting-authority diagnostic", rendered)
        self.assertIn("--reporting-source-phase phase1", rendered)

    def test_sweep_omits_reporting_metadata_flags_when_unspecified(self) -> None:
        command = self._captured_command([
            "run_unified.py",
            "sweep",
            "--config",
            "configs/default.yaml",
        ])

        rendered = " ".join(command)
        self.assertNotIn("--reporting-dataset-scope", rendered)
        self.assertNotIn("--reporting-authority", rendered)
        self.assertNotIn("--reporting-source-phase", rendered)


if __name__ == "__main__":
    unittest.main()
