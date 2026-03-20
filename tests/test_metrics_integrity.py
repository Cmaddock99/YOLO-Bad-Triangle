from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MetricsIntegrityProfilesTest(unittest.TestCase):
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
            },
            {
                "run_name": "fgsm_only",
                "MODEL": "yolo",
                "attack": "fgsm",
                "conf": "0.25",
                "seed": "42",
                "precision": "0.49",
                "recall": "0.39",
                "mAP50": "0.29",
                "mAP50-95": "0.19",
                "config_fingerprint": "fp",
                "attack_params_json": '{"epsilon":0.01}',
            },
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_strict_profile_fails_sparse_attack_sweep(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metrics_summary.csv"
            self._write_fixture_csv(csv_path)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/check_metrics_integrity.py"),
                    "--csv",
                    str(csv_path),
                    "--attack",
                    "fgsm",
                    "--profile",
                    "strict",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONPATH": "src"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

    def test_demo_profile_passes_sparse_attack_sweep(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metrics_summary.csv"
            self._write_fixture_csv(csv_path)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/check_metrics_integrity.py"),
                    "--csv",
                    str(csv_path),
                    "--attack",
                    "fgsm",
                    "--profile",
                    "demo",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONPATH": "src"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            self.assertIn('"status": "ok"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
