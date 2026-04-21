from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ci import check_tracked_outputs


class TrackedOutputPolicyTest(unittest.TestCase):
    def test_allows_historical_report_artifacts(self) -> None:
        paths = [
            Path("outputs/cycle_history/cycle_001.json"),
            Path("outputs/framework_reports/sweep_001/framework_run_report.md"),
            Path("outputs/framework_reports/sweep_001/summary_blur.txt"),
            Path("outputs/framework_reports/sweep_001/dashboard.html"),
            Path("outputs/cycle_report.csv"),
            Path("outputs/dashboard.html"),
        ]
        self.assertEqual(check_tracked_outputs.find_disallowed_tracked_outputs(paths), [])

    def test_allows_grandfathered_top_level_logs_and_text(self) -> None:
        paths = [
            Path("outputs/delegated_phase4.log"),
            Path("outputs/training_log_round2.txt"),
        ]
        self.assertEqual(check_tracked_outputs.find_disallowed_tracked_outputs(paths), [])

    def test_rejects_raw_run_artifacts(self) -> None:
        disallowed = check_tracked_outputs.find_disallowed_tracked_outputs(
            [Path("outputs/framework_runs/demo_run/metrics.json")]
        )
        self.assertEqual(disallowed, [Path("outputs/framework_runs/demo_run/metrics.json")])

    def test_rejects_lock_and_state_files(self) -> None:
        disallowed = check_tracked_outputs.find_disallowed_tracked_outputs(
            [
                Path("outputs/.cycle.lock"),
                Path("outputs/cycle_state.json"),
            ]
        )
        self.assertEqual(
            disallowed,
            [Path("outputs/.cycle.lock"), Path("outputs/cycle_state.json")],
        )

    def test_rejects_transfer_files(self) -> None:
        disallowed = check_tracked_outputs.find_disallowed_tracked_outputs(
            [
                Path("outputs/review_bundle.zip"),
                Path("outputs/report.pdf"),
                Path("outputs/training_exports/cycle_001_training_data.zip"),
            ]
        )
        self.assertEqual(
            disallowed,
            [
                Path("outputs/review_bundle.zip"),
                Path("outputs/report.pdf"),
                Path("outputs/training_exports/cycle_001_training_data.zip"),
            ],
        )

    def test_rejects_new_top_level_log_and_text_artifacts(self) -> None:
        disallowed = check_tracked_outputs.find_disallowed_tracked_outputs(
            [
                Path("outputs/foo.log"),
                Path("outputs/foo.txt"),
            ]
        )
        self.assertEqual(
            disallowed,
            [
                Path("outputs/foo.log"),
                Path("outputs/foo.txt"),
            ],
        )

    def test_main_returns_zero_when_policy_passes(self) -> None:
        result = check_tracked_outputs.main(
            [
                Path("outputs/cycle_history/cycle_001.json"),
                Path("outputs/framework_reports/sweep_001/framework_run_report.md"),
            ]
        )
        self.assertEqual(result, 0)

    def test_main_returns_one_when_policy_fails(self) -> None:
        result = check_tracked_outputs.main(
            [Path("outputs/framework_runs/demo_run/metrics.json")]
        )
        self.assertEqual(result, 1)


class WS6FrameworkReportsBinaryTest(unittest.TestCase):
    """WS6: binary artifacts inside outputs/framework_reports/ must be blocked."""

    def test_rejects_pt_inside_framework_reports(self) -> None:
        from scripts.ci import check_tracked_outputs
        result = check_tracked_outputs.find_disallowed_tracked_outputs([
            Path("outputs/framework_reports/sweep_001/model.pt"),
        ])
        self.assertEqual(len(result), 1)

    def test_rejects_zip_inside_framework_reports(self) -> None:
        from scripts.ci import check_tracked_outputs
        result = check_tracked_outputs.find_disallowed_tracked_outputs([
            Path("outputs/framework_reports/sweep_001/bundle.zip"),
        ])
        self.assertEqual(len(result), 1)

    def test_allows_csv_inside_framework_reports(self) -> None:
        from scripts.ci import check_tracked_outputs
        result = check_tracked_outputs.find_disallowed_tracked_outputs([
            Path("outputs/framework_reports/sweep_001/headline_metrics.csv"),
        ])
        self.assertEqual(result, [])

    def test_allows_json_inside_framework_reports(self) -> None:
        from scripts.ci import check_tracked_outputs
        result = check_tracked_outputs.find_disallowed_tracked_outputs([
            Path("outputs/framework_reports/sweep_001/summary.json"),
        ])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
