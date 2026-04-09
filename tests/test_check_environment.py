from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import check_environment


class CheckEnvironmentTest(unittest.TestCase):
    def test_supported_python_version_passes(self) -> None:
        result = check_environment.check_python_version((3, 11, 9))
        self.assertTrue(result.ok)

    def test_unsupported_python_version_fails(self) -> None:
        result = check_environment.check_python_version((3, 12, 1))
        self.assertFalse(result.ok)
        self.assertIn("Python 3.11.x", result.instruction or "")

    def test_torch_runtime_health_passes_when_probe_succeeds(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            del args, kwargs
            return subprocess.CompletedProcess(
                args=["python", "-c", "probe"],
                returncode=0,
                stdout="2.5.1\n0.20.1\n",
                stderr="",
            )

        result = check_environment.check_torch_runtime_health(
            executable="/tmp/python",
            runner=runner,
        )
        self.assertTrue(result.ok)
        self.assertIn("torch=2.5.1", result.detail or "")

    def test_torch_runtime_health_fails_when_probe_exits_nonzero(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            del args, kwargs
            return subprocess.CompletedProcess(
                args=["python", "-c", "probe"],
                returncode=1,
                stdout="",
                stderr="ImportError: broken torch",
            )

        result = check_environment.check_torch_runtime_health(
            executable="/tmp/python",
            runner=runner,
        )
        self.assertFalse(result.ok)
        self.assertIn("exited 1", result.detail or "")

    def test_torch_runtime_health_reports_native_crash(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            del args, kwargs
            return subprocess.CompletedProcess(
                args=["python", "-c", "probe"],
                returncode=-6,
                stdout="",
                stderr="Abort trap",
            )

        result = check_environment.check_torch_runtime_health(
            executable="/tmp/python",
            runner=runner,
        )
        self.assertFalse(result.ok)
        self.assertIn("signal 6", result.detail or "")

    def test_dataset_pairing_requires_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images_dir = Path(tmp) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            (images_dir / "a.jpg").write_bytes(b"stub")
            result = check_environment.check_dataset_path(str(images_dir))
            self.assertFalse(result.ok)
            self.assertIn("labels", (result.label or "").lower())

    def test_dataset_pairing_passes_when_labels_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images_dir = root / "images"
            labels_dir = root / "labels"
            images_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)
            (images_dir / "a.jpg").write_bytes(b"stub")
            (labels_dir / "a.txt").write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
            result = check_environment.check_dataset_path(str(images_dir))
            self.assertTrue(result.ok)

    def test_dpc_checkpoint_optional_passes_when_not_required(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch.object(
            check_environment,
            "DEFAULT_DPC_CHECKPOINT_CANDIDATES",
            ("missing_checkpoint_a.pt", "missing_checkpoint_b.pt"),
        ):
            result = check_environment.check_dpc_checkpoint(None, require=False)
        self.assertTrue(result.ok)
        self.assertIn("optional", result.label.lower())

    def test_dpc_checkpoint_required_fails_when_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch.object(
            check_environment,
            "DEFAULT_DPC_CHECKPOINT_CANDIDATES",
            ("missing_checkpoint_a.pt", "missing_checkpoint_b.pt"),
        ):
            result = check_environment.check_dpc_checkpoint(None, require=True)
        self.assertFalse(result.ok)
        self.assertIn("checkpoint", result.label.lower())

    def test_dpc_checkpoint_passes_when_env_points_to_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "dpc_unet_adversarial_finetuned.pt"
            checkpoint.write_bytes(b"stub")
            with patch.dict("os.environ", {"DPC_UNET_CHECKPOINT_PATH": str(checkpoint)}, clear=True):
                result = check_environment.check_dpc_checkpoint(None, require=True)
        self.assertTrue(result.ok)
        self.assertIn(str(checkpoint), result.detail or "")


if __name__ == "__main__":
    unittest.main()
