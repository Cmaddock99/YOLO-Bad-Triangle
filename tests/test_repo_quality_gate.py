from __future__ import annotations

import os
import subprocess
import unittest
from unittest.mock import call, patch

from scripts.ci import run_repo_quality_gate


class RepoQualityGateTest(unittest.TestCase):
    def _completed(self, command: list[str], returncode: int = 0) -> subprocess.CompletedProcess[None]:
        return subprocess.CompletedProcess(command, returncode)

    def test_fast_lane_runs_expected_commands_with_src_pythonpath(self) -> None:
        expected_commands = [
            ["python-fast", "-m", "ruff", "check", "src", "tests", "scripts"],
            ["python-fast", "-m", "mypy"],
            ["python-fast", "-m", "pytest", "-q"],
        ]

        with patch.dict(os.environ, {}, clear=True):
            with patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock:
                run_mock.side_effect = [self._completed(command) for command in expected_commands]

                result = run_repo_quality_gate.main(["--lane", "fast", "--python-bin", "python-fast"])

        self.assertEqual(result, 0)
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
            with patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock:
                run_mock.side_effect = [self._completed(command) for command in expected_commands]

                result = run_repo_quality_gate.main(["--lane", "ci", "--python-bin", "python-custom"])

        self.assertEqual(result, 0)
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
            with patch("scripts.ci.run_repo_quality_gate.subprocess.run") as run_mock:
                run_mock.side_effect = [
                    self._completed(command_one, returncode=0),
                    self._completed(command_two, returncode=7),
                ]

                result = run_repo_quality_gate.main(["--lane", "fast", "--python-bin", "python-fast"])

        self.assertEqual(result, 7)
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
