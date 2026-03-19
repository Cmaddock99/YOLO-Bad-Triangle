from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class FrameworkDuplicationAstEnforcementTest(unittest.TestCase):
    def test_ast_enforcement_passes_current_repository(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, str(repo_root / "scripts/ci/check_framework_duplication_ast.py")],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)


if __name__ == "__main__":
    unittest.main()
