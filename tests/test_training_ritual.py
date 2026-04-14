from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import run_training_ritual


REPO = Path(__file__).resolve().parents[1]


class TrainingRitualTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.signal_path = self.tmp / "cycle_training_signal.json"
        self.outputs = self.tmp / "outputs"
        self.outputs.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_signal(self, cycle_id: str = "cycle_001", age_hours: float = 0.5) -> None:
        payload = {
            "cycle_id": cycle_id,
            "worst_attack": "pgd",
            "worst_attack_params": {},
        }
        self.signal_path.write_text(json.dumps(payload), encoding="utf-8")
        ts = (datetime.now(tz=timezone.utc) - timedelta(hours=age_hours)).timestamp()
        os.utime(self.signal_path, (ts, ts))

    def _patch_signal_path(self) -> mock._patch:
        return mock.patch.object(run_training_ritual, "SIGNAL_PATH", self.signal_path)

    def test_fails_fast_if_signal_absent(self) -> None:
        """Exit code 2 when cycle_training_signal.json does not exist."""
        with self._patch_signal_path():
            rc = run_training_ritual.main([])
        self.assertEqual(rc, 2)

    def test_fails_fast_if_signal_stale(self) -> None:
        """Exit code 2 when the signal file is older than --max-age-hours."""
        self._write_signal(age_hours=50)  # older than default 24h
        with self._patch_signal_path():
            rc = run_training_ritual.main(["--max-age-hours", "24"])
        self.assertEqual(rc, 2)

    def test_accepts_fresh_signal_within_age_limit(self) -> None:
        """A signal file younger than the limit is accepted (no exit-2 from check_signal)."""
        self._write_signal(age_hours=1)
        captured: list[list[str]] = []

        def fake_run_step(label: str, cmd: list[str], *, dry_run: bool) -> None:
            captured.append(cmd)
            if label == "export_training_data":
                return  # success
            # train step — raise to stop further processing cleanly
            raise SystemExit(0)

        with self._patch_signal_path():
            with mock.patch.object(run_training_ritual, "_run_step", side_effect=fake_run_step):
                with mock.patch.object(run_training_ritual, "_print_verdict"):
                    run_training_ritual.main([])

        # Should have reached export step without failing at signal check
        self.assertTrue(any("export_training_data" in " ".join(c) for c in captured))

    def test_dry_run_prints_steps_without_executing(self) -> None:
        """--dry-run calls _run_step with dry_run=True for all steps."""
        self._write_signal(age_hours=1)
        dry_run_flags: list[bool] = []



        def recording_run_step(label: str, cmd: list[str], *, dry_run: bool) -> None:
            dry_run_flags.append(dry_run)
            # Don't actually run anything; simulate success

        with self._patch_signal_path():
            with mock.patch.object(run_training_ritual, "_run_step", side_effect=recording_run_step):
                with mock.patch.object(run_training_ritual, "_print_verdict"):
                    rc = run_training_ritual.main(["--dry-run"])

        self.assertEqual(rc, 0)
        self.assertTrue(all(dry_run_flags), "Expected all steps to be dry-run")

    def test_reads_verdict_from_manifest(self) -> None:
        """_print_verdict reads final_verdict from training_manifest.json."""
        self._write_signal(cycle_id="cycle_xyz", age_hours=1)
        manifest_dir = self.tmp / "outputs" / "training_runs" / "cycle_xyz"
        manifest_dir.mkdir(parents=True)
        manifest = {
            "cycle_id": "cycle_xyz",
            "final_verdict": "passed_both_manual_promotion_required",
            "clean_gate": {"delta_mAP50": 0.003},
            "attack_gate": {"delta_mAP50": -0.001},
        }
        (manifest_dir / "training_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        signal = {"cycle_id": "cycle_xyz"}
        outputs_patch = mock.patch.object(run_training_ritual, "OUTPUTS", self.tmp / "outputs")
        with outputs_patch:
            # Capture printed output
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                run_training_ritual._print_verdict(signal)

        output = buf.getvalue()
        self.assertIn("passed_both_manual_promotion_required", output)
        self.assertIn("+0.0030", output)  # clean delta
        self.assertIn("PROMOTION READY", output)

    def test_export_exit_2_returns_nonzero(self) -> None:
        """When export_training_data exits 2, main returns non-zero."""
        self._write_signal(age_hours=1)

        def failing_export(label: str, cmd: list[str], *, dry_run: bool) -> None:
            if "export_training_data" in label:
                raise SystemExit(2)

        with self._patch_signal_path():
            with mock.patch.object(run_training_ritual, "_run_step", side_effect=failing_export):
                rc = run_training_ritual.main([])

        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
