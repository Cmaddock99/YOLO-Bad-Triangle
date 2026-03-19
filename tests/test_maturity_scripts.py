from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MaturityScriptsTest(unittest.TestCase):
    def test_weekly_dashboard_includes_four_week_trends(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            nightly = tmp_root / "nightly.jsonl"
            ci = tmp_root / "ci.jsonl"
            health = tmp_root / "health.jsonl"
            out = tmp_root / "stability_dashboard.md"
            for i in range(10):
                nightly.write_text(
                    (nightly.read_text(encoding="utf-8") if nightly.exists() else "")
                    + json.dumps({"status": "PASS" if i % 2 == 0 else "FAIL"})
                    + "\n",
                    encoding="utf-8",
                )
                ci.write_text(
                    (ci.read_text(encoding="utf-8") if ci.exists() else "")
                    + json.dumps({"status": "PASS"})
                    + "\n",
                    encoding="utf-8",
                )
                health.write_text(
                    (health.read_text(encoding="utf-8") if health.exists() else "")
                    + json.dumps({"status": "PASS", "regression_detected": bool(i == 3)})
                    + "\n",
                    encoding="utf-8",
                )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/ops/generate_stability_dashboard.py"),
                    "--nightly-log",
                    str(nightly),
                    "--ci-log",
                    str(ci),
                    "--health-log",
                    str(health),
                    "--output",
                    str(out),
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Four-Week Trends", text)
            self.assertIn("Regression incidents", text)

    def test_nightly_log_contains_category_and_flaky_marker(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script_text = (repo_root / "scripts/ops/run_nightly_shadow_job.py").read_text(encoding="utf-8")
        self.assertIn('"failure_category"', script_text)
        self.assertIn('"flaky_marker"', script_text)


if __name__ == "__main__":
    unittest.main()
