from __future__ import annotations

import importlib
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutomationScriptCompatTest(unittest.TestCase):
    def test_old_and_new_auto_cycle_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.auto_cycle")
        new_mod = importlib.import_module("scripts.automation.auto_cycle")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_watch_cycle_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.watch_cycle")
        new_mod = importlib.import_module("scripts.automation.watch_cycle")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_cleanup_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("scripts.cleanup_stale_runs")
        new_mod = importlib.import_module("scripts.automation.cleanup_stale_runs")
        self.assertIs(old_mod, new_mod)

    def test_old_paths_still_expose_expected_symbols(self) -> None:
        from scripts.auto_cycle import _REQUIRED_RUN_ARTIFACTS
        from scripts.cleanup_stale_runs import find_stale_dirs
        from scripts.watch_cycle import _expected_validate_runs

        self.assertEqual(
            _REQUIRED_RUN_ARTIFACTS,
            ("metrics.json", "run_summary.json", "predictions.jsonl"),
        )
        self.assertEqual(_expected_validate_runs.__name__, "_expected_validate_runs")
        self.assertEqual(find_stale_dirs.__name__, "find_stale_dirs")

    def test_cleanup_stale_runs_root_entrypoint_help_smoke(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/cleanup_stale_runs.py", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Remove framework_runs directories", result.stdout)
        self.assertIn("--dry-run", result.stdout)


if __name__ == "__main__":
    unittest.main()
