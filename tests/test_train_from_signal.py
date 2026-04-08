from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from scripts import train_from_signal


class TrainFromSignalTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmpdir.name)
        self.signal_path = self.repo / "outputs" / "cycle_training_signal.json"
        self.signal_path.parent.mkdir(parents=True, exist_ok=True)
        self.signal_path.write_text(
            json.dumps(
                {
                    "cycle_id": "cycle_test",
                    "worst_attack": "deepfool",
                    "worst_attack_params": {"attack.params.epsilon": 0.1},
                }
            ),
            encoding="utf-8",
        )
        self.baseline_checkpoint = self.repo / "baseline.pt"
        self.baseline_checkpoint.write_bytes(b"baseline")
        self.training_zip = self.repo / "outputs" / "training_exports" / "cycle_test_training_data.zip"
        self.candidate_checkpoint = self.repo / "outputs" / "checkpoints" / "cycle_test_signal_candidate.pt"
        self.manifest_path = self.repo / "outputs" / "training_runs" / "cycle_test" / "training_manifest.json"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _completed(self, command: list[str], returncode: int = 0) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(command, returncode)

    def _subprocess_side_effect(
        self,
        *,
        train_returncode: int = 0,
        clean_returncode: int = 0,
        attack_returncode: int = 0,
    ):
        def _handler(command: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            script_name = Path(command[1]).name
            if script_name == "export_training_data.py":
                self.training_zip.parent.mkdir(parents=True, exist_ok=True)
                self.training_zip.write_bytes(b"zip")
                return self._completed(command, 0)
            if script_name == "train_dpc_unet_local.py":
                if train_returncode == 0:
                    self.candidate_checkpoint.parent.mkdir(parents=True, exist_ok=True)
                    self.candidate_checkpoint.write_bytes(b"candidate")
                return self._completed(command, train_returncode)
            if script_name == "evaluate_checkpoint.py":
                output_json = Path(command[command.index("--output-json") + 1])
                attack = command[command.index("--attack") + 1]
                output_json.parent.mkdir(parents=True, exist_ok=True)
                output_json.write_text(
                    json.dumps(
                        {
                            "attack": attack,
                            "delta_mAP50": 0.02 if attack == "none" else 0.01,
                        }
                    ),
                    encoding="utf-8",
                )
                returncode = clean_returncode if attack == "none" else attack_returncode
                return self._completed(command, returncode)
            raise AssertionError(f"Unexpected subprocess command: {command}")

        return _handler

    def _run_cli(self, *args: str, side_effect=None) -> tuple[int, str, str, mock.Mock]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = ["train_from_signal.py", *args]
        with mock.patch.object(train_from_signal, "REPO", self.repo):
            with mock.patch.object(sys, "argv", argv):
                with mock.patch("scripts.train_from_signal.subprocess.run", side_effect=side_effect) as run_mock:
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        try:
                            train_from_signal.run_cli()
                            exit_code = 0
                        except SystemExit as exc:
                            exit_code = int(exc.code)
        return exit_code, stdout.getvalue(), stderr.getvalue(), run_mock

    def test_happy_path_writes_complete_manifest_and_promotion_command(self) -> None:
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect(),
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.manifest_path.is_file())
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "passed_both_manual_promotion_required")
        self.assertEqual(manifest["clean_gate"]["verdict"], "passed")
        self.assertEqual(manifest["attack_gate"]["verdict"], "passed")
        self.assertIsNotNone(manifest["candidate_checkpoint"]["sha256"])
        self.assertIn("=== PROMOTION READY ===", stdout)
        self.assertIn("cp ", stdout)
        self.assertIn("mv ", stdout)

    def test_missing_signal_file_exits_nonzero(self) -> None:
        missing_signal = self.repo / "outputs" / "missing_signal.json"
        exit_code, _, stderr, _ = self._run_cli(
            "--signal-path",
            str(missing_signal),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Training signal not found", stderr)

    def test_missing_baseline_checkpoint_exits_nonzero(self) -> None:
        missing_checkpoint = self.repo / "missing.pt"
        exit_code, _, stderr, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(missing_checkpoint),
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Baseline checkpoint not found", stderr)

    def test_failed_training_writes_run_failed_manifest(self) -> None:
        exit_code, _, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect(train_returncode=1),
        )

        self.assertEqual(exit_code, 2)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "run_failed")
        self.assertIsNone(manifest["candidate_checkpoint"]["sha256"])

    def test_failed_clean_gate_blocks_promotion(self) -> None:
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect(clean_returncode=1),
        )

        self.assertEqual(exit_code, 1)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "failed_clean")
        self.assertEqual(manifest["clean_gate"]["verdict"], "failed")
        self.assertNotIn("PROMOTION READY", stdout)

    def test_failed_attack_gate_blocks_promotion(self) -> None:
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect(attack_returncode=1),
        )

        self.assertEqual(exit_code, 1)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "passed_clean_failed_attack")
        self.assertEqual(manifest["clean_gate"]["verdict"], "passed")
        self.assertEqual(manifest["attack_gate"]["verdict"], "failed")
        self.assertNotIn("PROMOTION READY", stdout)

    def test_dry_run_prints_commands_without_executing(self) -> None:
        exit_code, stdout, _, run_mock = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            "--dry-run",
        )

        self.assertEqual(exit_code, 0)
        run_mock.assert_not_called()
        self.assertIn("export_training_data.py", stdout)
        self.assertIn("train_dpc_unet_local.py", stdout)
        self.assertIn("evaluate_checkpoint.py", stdout)
        self.assertFalse(self.manifest_path.exists())


if __name__ == "__main__":
    unittest.main()
