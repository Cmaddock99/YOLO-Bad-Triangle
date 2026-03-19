from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CiEnforcementScriptsTest(unittest.TestCase):
    def test_legacy_policy_guard_blocks_protected_branch_enablement(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "migration_runtime.yaml"
            config.write_text(
                "migration:\n  use_legacy_runtime: true\n  required_consecutive_passes: 2\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/ci/check_legacy_policy_branch_guard.py"),
                    "--config",
                    str(config),
                    "--branch",
                    "main",
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=dict(os.environ),
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)

    def test_legacy_usage_enforcement_passes_repository(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, str(repo_root / "scripts/ci/check_legacy_usage_enforcement.py")],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=dict(os.environ),
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)


if __name__ == "__main__":
    unittest.main()
