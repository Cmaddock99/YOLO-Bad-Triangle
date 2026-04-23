from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from unittest.mock import call, patch

import cv2

from scripts.ci import run_repo_quality_gate


class RepoQualityGateTest(unittest.TestCase):
    def _completed(self, command: list[str], returncode: int = 0) -> subprocess.CompletedProcess[None]:
        return subprocess.CompletedProcess(command, returncode)

    def test_ensure_ci_demo_input_writes_expected_fixture_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = run_repo_quality_gate.Path(tmp)

            first = run_repo_quality_gate._ensure_ci_demo_input(repo_root)
            second = run_repo_quality_gate._ensure_ci_demo_input(repo_root)

            self.assertEqual(first, repo_root / "outputs" / "ci_demo" / "images" / "ci.jpg")
            self.assertEqual(second, first)
            self.assertTrue(first.is_file())
            image = cv2.imread(str(first))
            self.assertIsNotNone(image)
            assert image is not None
            self.assertEqual(image.shape, (128, 128, 3))
            self.assertTrue((image == 127).all())

    def test_default_without_flag_prefers_repo_venv_python_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = run_repo_quality_gate.Path(tmp)
            repo_python = repo_root / ".venv" / "bin" / "python"
            repo_python.parent.mkdir(parents=True, exist_ok=True)
            repo_python.write_text("", encoding="utf-8")
            expected_commands = [
                [str(repo_python), "-m", "ruff", "check", "src", "tests", "scripts"],
                [str(repo_python), "-m", "mypy"],
                [str(repo_python), "-m", "pytest", "-q"],
            ]

            with patch.object(run_repo_quality_gate, "REPO_ROOT", repo_root):
                with patch.dict(os.environ, {}, clear=True):
                    with (
                        patch.object(run_repo_quality_gate.sys, "executable", "python-sys"),
                        patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                        patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
                    ):
                        run_mock.side_effect = [self._completed(command) for command in expected_commands]

                        result = run_repo_quality_gate.main(["--lane", "fast"])

        self.assertEqual(result, 0)
        ensure_demo_mock.assert_not_called()
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command,
                    cwd=repo_root,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
                for command in expected_commands
            ],
        )

    def test_default_without_flag_falls_back_to_sys_executable_when_repo_venv_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = run_repo_quality_gate.Path(tmp)
            expected_commands = [
                ["python-sys", "-m", "ruff", "check", "src", "tests", "scripts"],
                ["python-sys", "-m", "mypy"],
                ["python-sys", "-m", "pytest", "-q"],
            ]

            with patch.object(run_repo_quality_gate, "REPO_ROOT", repo_root):
                with patch.dict(os.environ, {}, clear=True):
                    with (
                        patch.object(run_repo_quality_gate.sys, "executable", "python-sys"),
                        patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                        patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
                    ):
                        run_mock.side_effect = [self._completed(command) for command in expected_commands]

                        result = run_repo_quality_gate.main(["--lane", "fast"])

        self.assertEqual(result, 0)
        ensure_demo_mock.assert_not_called()
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command,
                    cwd=repo_root,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
                for command in expected_commands
            ],
        )

    def test_explicit_python_bin_wins_over_repo_venv_auto_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = run_repo_quality_gate.Path(tmp)
            repo_python = repo_root / ".venv" / "bin" / "python"
            repo_python.parent.mkdir(parents=True, exist_ok=True)
            repo_python.write_text("", encoding="utf-8")
            expected_commands = [
                ["python-custom", "-m", "ruff", "check", "src", "tests", "scripts"],
                ["python-custom", "-m", "mypy"],
                ["python-custom", "-m", "pytest", "-q"],
            ]

            with patch.object(run_repo_quality_gate, "REPO_ROOT", repo_root):
                with patch.dict(os.environ, {}, clear=True):
                    with (
                        patch.object(run_repo_quality_gate.sys, "executable", "python-sys"),
                        patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                        patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
                    ):
                        run_mock.side_effect = [self._completed(command) for command in expected_commands]

                        result = run_repo_quality_gate.main(["--lane", "fast", "--python-bin", "python-custom"])

        self.assertEqual(result, 0)
        ensure_demo_mock.assert_not_called()
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command,
                    cwd=repo_root,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
                for command in expected_commands
            ],
        )

    def test_fast_lane_runs_expected_commands_with_src_pythonpath(self) -> None:
        self.assertNotIn("cv2", run_repo_quality_gate.__dict__)
        self.assertNotIn("np", run_repo_quality_gate.__dict__)

        expected_commands = [
            ["python-fast", "-m", "ruff", "check", "src", "tests", "scripts"],
            ["python-fast", "-m", "mypy"],
            ["python-fast", "-m", "pytest", "-q"],
        ]

        with patch.dict(os.environ, {}, clear=True):
            with (
                patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
            ):
                run_mock.side_effect = [self._completed(command) for command in expected_commands]

                result = run_repo_quality_gate.main(["--lane", "fast", "--python-bin", "python-fast"])

        self.assertEqual(result, 0)
        ensure_demo_mock.assert_not_called()
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command,
                    cwd=run_repo_quality_gate.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
                for command in expected_commands
            ],
        )
        for command in expected_commands:
            self.assertNotIn("scripts/check_environment.py", " ".join(command))

    def test_ci_lane_runs_fast_lane_plus_repo_quality_commands(self) -> None:
        expected_commands = [
            ["python-custom", "-m", "ruff", "check", "src", "tests", "scripts"],
            ["python-custom", "-m", "mypy"],
            ["python-custom", "-m", "pytest", "-q"],
            [
                "python-custom",
                "scripts/run_unified.py",
                "run-one",
                "--config",
                "configs/ci_demo.yaml",
                "--set",
                "runner.output_root=outputs/framework_runs/ci",
                "--set",
                "runner.run_name=ci_demo",
            ],
            [
                "python-custom",
                "scripts/ci/validate_outputs.py",
                "--output-root",
                "outputs/framework_runs/ci/ci_demo",
                "--contract-name",
                "framework_run",
                "--framework-run-dir",
                "outputs/framework_runs/ci/ci_demo",
                "--legacy-compat-csv",
                "tests/fixtures/schema/valid/legacy_compat.csv",
                "--require-schema",
            ],
            [
                "python-custom",
                "scripts/generate_framework_report.py",
                "--runs-root",
                "outputs/framework_runs/ci",
                "--output-dir",
                "outputs/framework_reports/ci",
            ],
            ["python-custom", "scripts/ci/check_tracked_outputs.py"],
        ]

        with patch.dict(os.environ, {}, clear=True):
            with (
                patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
            ):
                run_mock.side_effect = [self._completed(command) for command in expected_commands]

                result = run_repo_quality_gate.main(["--lane", "ci", "--python-bin", "python-custom"])

        self.assertEqual(result, 0)
        ensure_demo_mock.assert_called_once_with(run_repo_quality_gate.REPO_ROOT)
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command,
                    cwd=run_repo_quality_gate.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
                for command in expected_commands
            ],
        )
        for command in expected_commands:
            self.assertNotIn("scripts/check_environment.py", " ".join(command))

    def test_stops_on_first_failure_and_returns_that_exit_code(self) -> None:
        command_one = ["python-fast", "-m", "ruff", "check", "src", "tests", "scripts"]
        command_two = ["python-fast", "-m", "mypy"]

        with patch.dict(os.environ, {}, clear=True):
            with (
                patch("scripts.ci.run_repo_quality_gate._ensure_ci_demo_input") as ensure_demo_mock,
                patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock,
            ):
                run_mock.side_effect = [
                    self._completed(command_one, returncode=0),
                    self._completed(command_two, returncode=7),
                ]

                result = run_repo_quality_gate.main(["--lane", "fast", "--python-bin", "python-fast"])

        self.assertEqual(result, 7)
        ensure_demo_mock.assert_not_called()
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    command_one,
                    cwd=run_repo_quality_gate.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                ),
                call(
                    command_two,
                    cwd=run_repo_quality_gate.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
