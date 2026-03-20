from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FgsmSanityProfilesTest(unittest.TestCase):
    def _write_fixture_csv(self, path: Path) -> None:
        fields = [
            "run_name",
            "MODEL",
            "attack",
            "conf",
            "seed",
            "precision",
            "recall",
            "mAP50",
            "mAP50-95",
            "config_fingerprint",
            "attack_params_json",
            "run_session_id",
            "run_started_at_utc",
        ]
        rows = [
            {
                "run_name": "baseline",
                "MODEL": "yolo",
                "attack": "none",
                "conf": "0.25",
                "seed": "42",
                "precision": "0.50",
                "recall": "0.40",
                "mAP50": "0.30",
                "mAP50-95": "0.20",
                "config_fingerprint": "fp",
                "attack_params_json": "{}",
                "run_session_id": "sess",
                "run_started_at_utc": "2026-03-19T00:00:00Z",
            },
            {
                "run_name": "fgsm_only",
                "MODEL": "yolo",
                "attack": "fgsm",
                "conf": "0.25",
                "seed": "42",
                "precision": "0.50",
                "recall": "0.40",
                "mAP50": "0.30",
                "mAP50-95": "0.20",
                "config_fingerprint": "fp",
                "attack_params_json": '{"epsilon":0.01}',
                "run_session_id": "sess",
                "run_started_at_utc": "2026-03-19T00:00:00Z",
            },
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_strict_profile_fails_incomplete_fgsm_sweep(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metrics_summary.csv"
            self._write_fixture_csv(csv_path)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/check_fgsm_sanity.py"),
                    "--csv",
                    str(csv_path),
                    "--profile",
                    "strict",
                    "--attack",
                    "fgsm",
                    "--use-latest-session",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONPATH": "src"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

    def test_demo_profile_warns_and_passes_incomplete_fgsm_sweep(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metrics_summary.csv"
            self._write_fixture_csv(csv_path)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/check_fgsm_sanity.py"),
                    "--csv",
                    str(csv_path),
                    "--profile",
                    "demo",
                    "--attack",
                    "fgsm",
                    "--use-latest-session",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONPATH": "src"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            combined = proc.stdout + proc.stderr
            self.assertIn("Incomplete fgsm sweep accepted", combined)
            self.assertIn("Baseline-vs-fgsm equivalence accepted", combined)


if __name__ == "__main__":
    unittest.main()
