from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from lab.migration.diagnostics import diagnose_failure


class MigrationDiagnosticsTest(unittest.TestCase):
    def test_diagnose_failure_reports_missing_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "metrics_summary.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["run_name"])
                writer.writeheader()
                writer.writerow({"run_name": "x"})
            diagnosis = diagnose_failure(
                {
                    "failure_type": "artifact_validation",
                    "component": "metrics_summary.csv",
                    "stage": "artifact_validation",
                    "artifact_path": str(csv_path),
                    "required_columns": ["run_name", "precision"],
                }
            )
            self.assertEqual(diagnosis["severity"], "CRITICAL")
            self.assertTrue(diagnosis["issues"])
            self.assertTrue(any("adapter" in str(item.get("likely_cause", "")) for item in diagnosis["issues"]))


if __name__ == "__main__":
    unittest.main()
