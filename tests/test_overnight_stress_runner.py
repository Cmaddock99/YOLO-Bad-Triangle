from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import run_overnight_stress


class OvernightStressRunnerTest(unittest.TestCase):
    def test_collect_progress_counts_completed_and_prepared_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            baseline = runs_root / "baseline_none"
            attack = runs_root / "attack_fgsm"
            (baseline / "prepared_images").mkdir(parents=True, exist_ok=True)
            (attack / "prepared_images").mkdir(parents=True, exist_ok=True)
            for idx in range(3):
                (baseline / "prepared_images" / f"{idx}.jpg").write_text("x", encoding="utf-8")
            for idx in range(2):
                (attack / "prepared_images" / f"{idx}.jpg").write_text("x", encoding="utf-8")
            (baseline / "metrics.json").write_text("{}", encoding="utf-8")

            progress = run_overnight_stress._collect_progress(runs_root)
            self.assertEqual(progress["run_dirs_discovered"], 2)
            self.assertEqual(progress["completed_runs"], 1)
            self.assertEqual(progress["prepared_images_total"], 5)
            self.assertEqual(progress["active_run"], "baseline_none")

    def test_classify_final_status_prefers_timeout_resumable(self) -> None:
        status = run_overnight_stress._classify_final_status(
            timed_out=True,
            exit_code=None,
            artifact_result={"all_present": False, "parse_ok": False},
            smoke_result={"all_ok": True},
        )
        self.assertEqual(status, "timed_out_resumable")

    def test_classify_final_status_completed_clean(self) -> None:
        status = run_overnight_stress._classify_final_status(
            timed_out=False,
            exit_code=0,
            artifact_result={"all_present": True, "parse_ok": True},
            smoke_result={"all_ok": True},
        )
        self.assertEqual(status, "completed_clean")

    def test_classify_final_status_completed_with_caveats(self) -> None:
        status = run_overnight_stress._classify_final_status(
            timed_out=False,
            exit_code=0,
            artifact_result={"all_present": False, "parse_ok": True},
            smoke_result={"all_ok": True},
        )
        self.assertEqual(status, "completed_with_caveats")

    def test_classify_final_status_failed(self) -> None:
        status = run_overnight_stress._classify_final_status(
            timed_out=False,
            exit_code=1,
            artifact_result={"all_present": True, "parse_ok": True},
            smoke_result={"all_ok": False},
        )
        self.assertEqual(status, "failed_needs_attention")


if __name__ == "__main__":
    unittest.main()
