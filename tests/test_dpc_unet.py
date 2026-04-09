from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    image_bgr_to_model_tensor,
    model_tensor_to_image_bgr,
    run_wrapper_multipass_on_bgr_image,
    run_wrapper_on_bgr_image,
    sinusoidal_timestep_embedding,
)
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins


class DPCUNetModelTests(unittest.TestCase):
    def test_sinusoidal_embedding_shape(self) -> None:
        t = torch.tensor([0.0, 10.0, 100.0])
        emb = sinusoidal_timestep_embedding(t, dim=64)
        self.assertEqual(tuple(emb.shape), (3, 64))

    def test_forward_accepts_scalar_and_tensor_timestep(self) -> None:
        model = DPCUNet().eval()
        x = torch.zeros((2, 3, 64, 64), dtype=torch.float32)
        y_scalar = model(x, timestep=100)
        y_tensor = model(x, timestep=torch.tensor([10.0, 20.0]))
        self.assertEqual(tuple(y_scalar.shape), (2, 3, 64, 64))
        self.assertEqual(tuple(y_tensor.shape), (2, 3, 64, 64))
        self.assertTrue(torch.isfinite(y_scalar).all().item())
        self.assertTrue(torch.isfinite(y_tensor).all().item())


class DPCUNetIOTests(unittest.TestCase):
    def test_roundtrip_conversion_preserves_shape(self) -> None:
        image = np.random.randint(0, 256, size=(48, 64, 3), dtype=np.uint8)
        cfg = WrapperInputConfig(color_order="rgb", scaling="zero_one", normalize=False)
        tensor = image_bgr_to_model_tensor(image, cfg=cfg)
        rebuilt = model_tensor_to_image_bgr(tensor, cfg=cfg)
        self.assertEqual(rebuilt.shape, image.shape)
        self.assertEqual(rebuilt.dtype, np.uint8)

    def test_minus_one_one_with_normalize_roundtrip(self) -> None:
        image = np.random.randint(0, 256, size=(32, 40, 3), dtype=np.uint8)
        cfg = WrapperInputConfig(color_order="bgr", scaling="minus_one_one", normalize=True)
        tensor = image_bgr_to_model_tensor(image, cfg=cfg)
        rebuilt = model_tensor_to_image_bgr(tensor, cfg=cfg)
        self.assertEqual(rebuilt.shape, image.shape)
        self.assertEqual(rebuilt.dtype, np.uint8)

    def test_wrapper_run_returns_image_and_finite_stats(self) -> None:
        image = np.full((32, 32, 3), 127, dtype=np.uint8)
        model = DPCUNet()
        cfg = WrapperInputConfig(color_order="rgb", scaling="zero_one", normalize=False)
        output, stats = run_wrapper_on_bgr_image(image, model, timestep=100, cfg=cfg, device="cpu")
        self.assertEqual(output.shape, image.shape)
        self.assertIsInstance(stats["finite"], bool)
        self.assertIn("tensor_mean", stats)

    def test_wrapper_run_is_deterministic_for_same_input(self) -> None:
        image = np.full((40, 48, 3), 96, dtype=np.uint8)
        model = DPCUNet()
        cfg = WrapperInputConfig(color_order="bgr", scaling="zero_one", normalize=True)
        out1, _ = run_wrapper_on_bgr_image(image, model, timestep=50, cfg=cfg, device="cpu")
        out2, _ = run_wrapper_on_bgr_image(image, model, timestep=50, cfg=cfg, device="cpu")
        self.assertTrue(np.array_equal(out1, out2))


class DPCUNetAdapterTests(unittest.TestCase):
    def _write_checkpoint(self, path: Path) -> None:
        model = DPCUNet()
        torch.save(model.state_dict(), path)

    def test_plugin_registered(self) -> None:
        names = list_available_defense_plugins()
        self.assertIn("preprocess_dpc_unet", names)
        self.assertIn("c_dog", names)

    def test_preprocess_runs_with_valid_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin(
                "c_dog",
                checkpoint_path=str(ckpt),
                timestep=50,
                color_order="bgr",
                scaling="zero_one",
                normalize=True,
            )
            image = np.full((40, 60, 3), 120, dtype=np.uint8)
            output, meta = defense.preprocess(image)
            self.assertEqual(output.shape, image.shape)
            self.assertEqual(meta["defense"], "preprocess_dpc_unet")
            self.assertTrue(meta["finite"])

    def test_cdog_checkpoint_provenance_reports_resolved_path_and_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin("c_dog", checkpoint_path=str(ckpt))
            result = defense.checkpoint_provenance()
            self.assertEqual(len(result), 1)
            self.assertTrue(Path(result[0]["path"]).is_absolute())
            self.assertEqual(result[0]["path"], str(ckpt.resolve()))
            # Verify sha256 matches independently computed digest
            digest = hashlib.sha256()
            with ckpt.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    digest.update(chunk)
            self.assertEqual(result[0]["sha256"], digest.hexdigest())

    def test_cdog_checkpoint_provenance_empty_when_checkpoint_path_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=False) as env:
            env.pop("DPC_UNET_CHECKPOINT_PATH", None)
            defense = build_defense_plugin("c_dog", checkpoint_path="")
            self.assertEqual(defense.checkpoint_provenance(), [])

    def test_preprocess_rejects_non_finite_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            self._write_checkpoint(ckpt)
            defense = build_defense_plugin("preprocess_dpc_unet", checkpoint_path=str(ckpt))
            image = np.zeros((32, 32, 3), dtype=np.uint8)
            with patch(
                "lab.defenses.preprocess_dpc_unet_adapter.run_wrapper_on_bgr_image",
                return_value=(image.copy(), {"finite": False, "tensor_min": 0.0, "tensor_max": 0.0, "tensor_mean": 0.0, "tensor_std": 0.0}),
            ):
                with self.assertRaises(RuntimeError):
                    defense.preprocess(image)


class WS5MultipassTest(unittest.TestCase):
    """WS5 tests: multipass call count, NaN guard, multipass metadata."""

    def setUp(self) -> None:
        self.model = DPCUNet().eval()
        self.image = np.full((32, 32, 3), 127, dtype=np.uint8)
        self.cfg = WrapperInputConfig(color_order="bgr", scaling="zero_one", normalize=False)

    def test_multipass_call_count_equals_schedule_length(self) -> None:
        """Model must be called exactly len(schedule) times — no extra post-loop pass."""
        schedule = [75.0, 50.0, 25.0]
        call_count = [0]
        original_forward = self.model.forward

        def counting_forward(x, timestep=None):
            call_count[0] += 1
            return original_forward(x, timestep=timestep)

        with patch.object(self.model, "forward", side_effect=counting_forward):
            run_wrapper_multipass_on_bgr_image(
                self.image, self.model, timestep_schedule=schedule, cfg=self.cfg, device="cpu"
            )
        self.assertEqual(call_count[0], len(schedule))

    def test_multipass_nan_raises_runtime_error(self) -> None:
        """A model that returns NaN must cause RuntimeError before the round-trip clamp."""
        import torch

        def nan_forward(x, timestep=None):
            return torch.full_like(x, float("nan"))

        with patch.object(self.model, "forward", side_effect=nan_forward):
            with self.assertRaises(RuntimeError):
                run_wrapper_multipass_on_bgr_image(
                    self.image, self.model, timestep_schedule=[50.0], cfg=self.cfg, device="cpu"
                )

    def test_multipass_passes_stat_equals_schedule_length(self) -> None:
        """stats['passes'] must equal len(timestep_schedule)."""
        schedule = [75.0, 25.0]
        _, stats = run_wrapper_multipass_on_bgr_image(
            self.image, self.model, timestep_schedule=schedule, cfg=self.cfg, device="cpu"
        )
        self.assertEqual(stats["passes"], len(schedule))


class WS5CheckpointProvenanceTest(unittest.TestCase):
    """WS5: hash is cached at load time; on-disk replacement does not change provenance output."""

    def test_hash_cached_at_load_time(self) -> None:
        from lab.defenses.framework_registry import build_defense_plugin
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "dpc.pt"
            model = DPCUNet()
            torch.save(model.state_dict(), ckpt)
            defense = build_defense_plugin(
                "c_dog", checkpoint_path=str(ckpt), timestep=50,
                color_order="bgr", scaling="zero_one", normalize=False,
            )
            image = np.full((32, 32, 3), 127, dtype=np.uint8)
            defense.preprocess(image)  # triggers _ensure_loaded

            prov_before = defense.checkpoint_provenance()
            sha_before = prov_before[0]["sha256"]

            # Overwrite file on disk with a different model
            model2 = DPCUNet()
            torch.save(model2.state_dict(), ckpt)

            prov_after = defense.checkpoint_provenance()
            sha_after = prov_after[0]["sha256"]

            # Provenance must reflect the file as-it-was-at-load, not the new file
            self.assertEqual(sha_before, sha_after)


if __name__ == "__main__":
    unittest.main()
