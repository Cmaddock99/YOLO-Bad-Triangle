from __future__ import annotations

import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.ci import run_vulture

_REAL_NAMED_TEMPORARY_FILE = tempfile.NamedTemporaryFile


class RunVultureTest(unittest.TestCase):
    def _completed(
        self, command: list[str], returncode: int
    ) -> subprocess.CompletedProcess[None]:
        return subprocess.CompletedProcess(command, returncode)

    def _run_main(
        self,
        tmpdir: str,
        side_effect: object,
    ) -> tuple[int, str]:
        def named_temp_file(*args: object, **kwargs: object):
            kwargs.setdefault("dir", tmpdir)
            return _REAL_NAMED_TEMPORARY_FILE(*args, **kwargs)

        output = io.StringIO()
        with (
            patch.object(run_vulture, "REPO_ROOT", Path("/repo")),
            patch(
                "scripts.ci.run_vulture.tempfile.NamedTemporaryFile",
                side_effect=named_temp_file,
            ),
            patch("scripts.ci.run_vulture.subprocess.run", side_effect=side_effect),
            redirect_stdout(output),
        ):
            result = run_vulture.main()

        return result, output.getvalue()

    def test_main_returns_zero_when_vulture_reports_no_dead_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observed_whitelist_paths: list[Path] = []

            def run_side_effect(
                command: list[str],
                cwd: Path,
                capture_output: bool,
            ) -> subprocess.CompletedProcess[None]:
                self.assertEqual(cwd, Path("/repo"))
                self.assertFalse(capture_output)
                whitelist_path = Path(command[5])
                observed_whitelist_paths.append(whitelist_path)
                self.assertTrue(whitelist_path.is_file())
                whitelist_text = whitelist_path.read_text(encoding="utf-8")
                self.assertIn("FGSMAttackAdapter", whitelist_text)
                return self._completed(command, returncode=0)

            result, output = self._run_main(tmp, run_side_effect)

        self.assertEqual(result, 0)
        self.assertIn("vulture: no dead code found.", output)
        self.assertFalse(observed_whitelist_paths[0].exists())

    def test_main_returns_zero_when_vulture_reports_dead_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:

            def run_side_effect(
                command: list[str],
                cwd: Path,
                capture_output: bool,
            ) -> subprocess.CompletedProcess[None]:
                self.assertEqual(cwd, Path("/repo"))
                self.assertFalse(capture_output)
                return self._completed(command, returncode=3)

            result, output = self._run_main(tmp, run_side_effect)

        self.assertEqual(result, 0)
        self.assertIn("potential dead code found", output)

    def test_main_returns_nonzero_when_vulture_exits_with_execution_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observed_whitelist_paths: list[Path] = []

            def run_side_effect(
                command: list[str],
                cwd: Path,
                capture_output: bool,
            ) -> subprocess.CompletedProcess[None]:
                self.assertEqual(cwd, Path("/repo"))
                self.assertFalse(capture_output)
                whitelist_path = Path(command[5])
                observed_whitelist_paths.append(whitelist_path)
                self.assertTrue(whitelist_path.exists())
                return self._completed(command, returncode=1)

            result, output = self._run_main(tmp, run_side_effect)

        self.assertEqual(result, 1)
        self.assertIn("execution/setup error", output)
        self.assertFalse(observed_whitelist_paths[0].exists())

    def test_main_removes_whitelist_file_when_subprocess_launch_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:

            def run_side_effect(
                command: list[str],
                cwd: Path,
                capture_output: bool,
            ) -> subprocess.CompletedProcess[None]:
                self.assertEqual(cwd, Path("/repo"))
                self.assertFalse(capture_output)
                whitelist_path = Path(command[5])
                self.assertTrue(whitelist_path.exists())
                raise OSError("No such file or directory")

            result, output = self._run_main(tmp, run_side_effect)

            remaining_files = list(Path(tmp).iterdir())

        self.assertEqual(result, 1)
        self.assertIn("failed to launch vulture", output)
        self.assertEqual(remaining_files, [])


if __name__ == "__main__":
    unittest.main()
