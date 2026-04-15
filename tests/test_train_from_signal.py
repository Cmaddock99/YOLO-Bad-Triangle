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

    def _subprocess_side_effect_with_delta(
        self,
        *,
        train_returncode: int = 0,
        clean_delta: float = 0.02,
        clean_returncode: int = 0,
        attack_delta: float = 0.01,
        attack_returncode: int = 0,
    ):
        """Like _subprocess_side_effect but allows controlling delta values independently."""
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
                is_clean = attack == "none"
                delta = clean_delta if is_clean else attack_delta
                rc = clean_returncode if is_clean else attack_returncode
                output_json.write_text(
                    json.dumps({"attack": attack, "delta_mAP50": delta}),
                    encoding="utf-8",
                )
                return self._completed(command, rc)
            raise AssertionError(f"Unexpected subprocess command: {command}")

        return _handler

    def test_clean_gate_fails_when_delta_below_threshold_despite_exit_zero(self) -> None:
        """delta_mAP50 = -0.01 must fail the clean gate even if evaluate_checkpoint exits 0.

        evaluate_checkpoint.py exits 0 when B >= A; our spec requires delta >= -0.005.
        A candidate with delta = -0.01 is outside the noise-floor tolerance and must
        not receive a promotion recommendation regardless of exit code.
        """
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect_with_delta(
                clean_delta=-0.01,
                clean_returncode=0,  # exit 0 — gate must still fail on delta alone
            ),
        )

        self.assertEqual(exit_code, 1)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "failed_clean")
        self.assertEqual(manifest["clean_gate"]["verdict"], "failed")
        self.assertAlmostEqual(manifest["clean_gate"]["delta_mAP50"], -0.01)
        self.assertNotIn("PROMOTION READY", stdout)

    def test_clean_gate_passes_when_delta_within_tolerance(self) -> None:
        """delta_mAP50 = -0.003 is within the -0.005 tolerance band and must pass."""
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect_with_delta(
                clean_delta=-0.003,
                clean_returncode=0,
                attack_delta=0.005,
                attack_returncode=0,
            ),
        )

        self.assertEqual(exit_code, 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["clean_gate"]["verdict"], "passed")
        self.assertEqual(manifest["final_verdict"], "passed_both_manual_promotion_required")
        self.assertIn("PROMOTION READY", stdout)

    def test_attack_gate_fails_when_delta_below_threshold_despite_exit_zero(self) -> None:
        """delta_mAP50 = -0.01 on the attack gate must block promotion even with exit 0."""
        exit_code, stdout, _, _ = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            side_effect=self._subprocess_side_effect_with_delta(
                clean_delta=0.02,
                clean_returncode=0,
                attack_delta=-0.01,
                attack_returncode=0,  # exit 0 — gate must still fail on delta
            ),
        )

        self.assertEqual(exit_code, 1)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["final_verdict"], "passed_clean_failed_attack")
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

    def test_profile_incompatible_writes_manifest_and_exits_nonzero(self) -> None:
        exit_code, _, _, run_mock = self._run_cli(
            "--signal-path",
            str(self.signal_path),
            "--checkpoint-a",
            str(self.baseline_checkpoint),
            "--profile",
            "yolo11n_lab_v1",
        )

        self.assertEqual(exit_code, 2)
        self.assertFalse(run_mock.called)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["pipeline_profile"], "yolo11n_lab_v1")
        self.assertEqual(manifest["authoritative_metric"], "mAP50")
        self.assertEqual(manifest["final_verdict"], "profile_incompatible")
        self.assertEqual(manifest["learned_defense_compatibility"]["status"], "incompatible")


class WS2GateAndManifestTest(unittest.TestCase):
    """WS2 tests: gate threshold, manifest completeness, atomic manifest writes."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_gate_threshold_is_minus_0005(self) -> None:
        """_GATE_THRESHOLD must be -0.005 so that delta=-0.003 passes the gate."""
        self.assertEqual(train_from_signal._GATE_THRESHOLD, -0.005)

    def test_gate_passed_with_delta_minus_0003(self) -> None:
        """A candidate with delta_mAP50=-0.003 should pass (within tolerance band)."""
        result = subprocess.CompletedProcess(args=[], returncode=0)
        payload = {"delta_mAP50": -0.003}
        self.assertTrue(train_from_signal._gate_passed(result, payload))

    def test_gate_fails_with_delta_minus_0006(self) -> None:
        """A candidate with delta_mAP50=-0.006 must fail (beyond tolerance band)."""
        result = subprocess.CompletedProcess(args=[], returncode=0)
        payload = {"delta_mAP50": -0.006}
        self.assertFalse(train_from_signal._gate_passed(result, payload))

    def test_gate_fails_when_subprocess_exits_nonzero(self) -> None:
        """A nonzero subprocess return code must cause the gate to fail regardless of delta."""
        result = subprocess.CompletedProcess(args=[], returncode=1)
        payload = {"delta_mAP50": 0.01}
        self.assertFalse(train_from_signal._gate_passed(result, payload))

    def test_manifest_contains_attack_params(self) -> None:
        """training_manifest.json must include attack_params in the attack_gate section."""
        manifest_dir = self.repo / "outputs" / "training_runs" / "cycle_test"
        manifest_path = manifest_dir / "training_manifest.json"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "cycle_id": "cycle_test",
            "attack_gate": {
                "attack": "deepfool",
                "attack_params": {"attack.params.epsilon": 0.1},
                "result_path": "/tmp/result.json",
                "delta_mAP50": 0.02,
                "verdict": "passed",
            },
        }
        train_from_signal._write_manifest(manifest_path, payload)
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("attack_params", loaded["attack_gate"])
        self.assertEqual(loaded["attack_gate"]["attack_params"], {"attack.params.epsilon": 0.1})

    def test_write_manifest_is_atomic(self) -> None:
        """_write_manifest must not leave a .tmp file after a successful write."""
        manifest_dir = self.repo / "manifests"
        manifest_path = manifest_dir / "training_manifest.json"
        train_from_signal._write_manifest(manifest_path, {"test": True})
        self.assertTrue(manifest_path.exists())
        tmp_files = list(manifest_dir.glob("*.tmp"))
        self.assertEqual(tmp_files, [], f"Leftover .tmp after _write_manifest: {tmp_files}")


if __name__ == "__main__":
    unittest.main()
