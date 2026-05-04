from __future__ import annotations

import unittest
from pathlib import Path

from lab.health_checks.regression import load_csv_rows, run_metrics_integrity_checks


class RegressionSweepFixtureTest(unittest.TestCase):
    def test_minimal_sweep_passes_integrity_checks(self) -> None:
        csv_path = Path("tests/fixtures/reports/regression_sweep_minimal.csv").resolve()
        rows = load_csv_rows(csv_path=csv_path, require_columns=True)
        run_metrics_integrity_checks(rows=rows, attack_name="fgsm", allow_sparse_fgsm=False)


if __name__ == "__main__":
    unittest.main()
