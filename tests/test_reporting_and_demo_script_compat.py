from __future__ import annotations

import importlib
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReportingAndDemoScriptCompatTest(unittest.TestCase):
    def test_old_and_new_run_demo_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.run_demo")
        new_mod = importlib.import_module("scripts.demo.run_demo")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_generate_auto_summary_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.generate_auto_summary")
        new_mod = importlib.import_module("scripts.reporting.generate_auto_summary")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_generate_cycle_report_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.generate_cycle_report")
        new_mod = importlib.import_module("scripts.reporting.generate_cycle_report")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_generate_framework_report_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.generate_framework_report")
        new_mod = importlib.import_module("scripts.reporting.generate_framework_report")
        self.assertIs(old_mod, new_mod)

    def test_old_paths_still_expose_expected_symbols(self) -> None:
        from scripts.generate_auto_summary import _parse_args
        from scripts.generate_cycle_report import generate_reports
        from scripts.generate_framework_report import generate_framework_report
        from scripts.run_demo import build_expected_runs

        self.assertEqual(_parse_args.__name__, "_parse_args")
        self.assertEqual(generate_reports.__name__, "generate_reports")
        self.assertEqual(generate_framework_report.__name__, "generate_framework_report")
        self.assertEqual(build_expected_runs.__name__, "build_expected_runs")

    def test_root_reporting_and_demo_entrypoint_help_smoke(self) -> None:
        cases = (
            ("scripts/run_demo.py", "--dry-run"),
            ("scripts/generate_auto_summary.py", "--runs-root"),
            ("scripts/generate_cycle_report.py", "--history-dir"),
            ("scripts/generate_framework_report.py", "--output-dir"),
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
