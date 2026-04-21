from __future__ import annotations

import os
import subprocess
import unittest
from unittest.mock import call, patch

from scripts.ci import run_repo_standards_audit


class RepoStandardsAuditTest(unittest.TestCase):
    def _completed(self, command: list[str], returncode: int = 0) -> subprocess.CompletedProcess[None]:
        return subprocess.CompletedProcess(command, returncode)

    def test_compat_lane_runs_structure_compat_suite(self) -> None:
        expected_command = [
            "python-custom",
            "-m",
            "pytest",
            "-q",
            "tests/test_repo_structure_compat.py",
            "tests/test_plugin_loader_routing.py",
            "tests/test_training_script_compat.py",
            "tests/test_reporting_and_demo_script_compat.py",
            "tests/test_automation_script_compat.py",
            "tests/test_framework_output_contract.py",
        ]

        with patch.dict(os.environ, {}, clear=True):
            with patch("scripts.ci.run_repo_standards_audit.subprocess.run") as run_mock:
                run_mock.return_value = self._completed(expected_command)

                result = run_repo_standards_audit.main(
                    ["--lane", "compat", "--python-bin", "python-custom"]
                )

        self.assertEqual(result, 0)
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    expected_command,
                    cwd=run_repo_standards_audit.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
            ],
        )

    def test_full_lane_runs_quality_gate_then_structure_compat_suite(self) -> None:
        quality_gate = [
            "python-custom",
            "scripts/ci/run_repo_quality_gate.py",
            "--lane",
            "fast",
        ]
        compat_suite = [
            "python-custom",
            "-m",
            "pytest",
            "-q",
            "tests/test_repo_structure_compat.py",
            "tests/test_plugin_loader_routing.py",
            "tests/test_training_script_compat.py",
            "tests/test_reporting_and_demo_script_compat.py",
            "tests/test_automation_script_compat.py",
            "tests/test_framework_output_contract.py",
        ]

        with patch.dict(os.environ, {}, clear=True):
            with patch("scripts.ci.run_repo_standards_audit.subprocess.run") as run_mock:
                run_mock.side_effect = [
                    self._completed(quality_gate),
                    self._completed(compat_suite),
                ]

                result = run_repo_standards_audit.main(
                    ["--lane", "full", "--python-bin", "python-custom"]
                )

        self.assertEqual(result, 0)
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    quality_gate,
                    cwd=run_repo_standards_audit.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                ),
                call(
                    compat_suite,
                    cwd=run_repo_standards_audit.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                ),
            ],
        )

    def test_stops_on_first_failure(self) -> None:
        quality_gate = [
            "python-custom",
            "scripts/ci/run_repo_quality_gate.py",
            "--lane",
            "fast",
        ]

        with patch.dict(os.environ, {}, clear=True):
            with patch("scripts.ci.run_repo_standards_audit.subprocess.run") as run_mock:
                run_mock.return_value = self._completed(quality_gate, returncode=5)

                result = run_repo_standards_audit.main(
                    ["--lane", "full", "--python-bin", "python-custom"]
                )

        self.assertEqual(result, 5)
        self.assertEqual(
            run_mock.call_args_list,
            [
                call(
                    quality_gate,
                    cwd=run_repo_standards_audit.REPO_ROOT,
                    env={"PYTHONPATH": "src"},
                    check=False,
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
