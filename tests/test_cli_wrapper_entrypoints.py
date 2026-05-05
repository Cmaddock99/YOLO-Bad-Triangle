from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliWrapperEntrypointTest(unittest.TestCase):
    def test_root_wrapper_help_entrypoints_smoke(self) -> None:
        cases = (
            ("scripts/auto_cycle.py", "--loop"),
            ("scripts/watch_cycle.py", "Live watcher"),
            ("scripts/cleanup_stale_runs.py", "--dry-run"),
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
