from __future__ import annotations

import hashlib
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks import build_attack
from lab.attacks.eot_pgd import EOTPGDAttack
from lab.attacks.pgd import PGDAttack
from lab.attacks.registry import list_available_attacks


class DummyDetectionModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stride = torch.tensor([32.0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        score = x.mean(dim=(1, 2, 3), keepdim=False).unsqueeze(-1)
        return score.unsqueeze(-1).repeat(1, 10, 6)


class PGDEOTAttackTests(unittest.TestCase):
    def _build_pgd(self, **overrides: object) -> PGDAttack:
        params = {
            "epsilon": 0.016,
            "alpha": 0.002,
            "steps": 4,
            "random_start": False,
            "restarts": 1,
            **overrides,
        }
        attack = build_attack("pgd", params)
        self.assertIsInstance(attack, PGDAttack)
        return attack

    def _build_eot(self, **overrides: object) -> EOTPGDAttack:
        params = {
            "epsilon": 0.016,
            "alpha": 0.002,
            "steps": 4,
            "random_start": False,
            "restarts": 1,
            "eot_samples": 2,
            "scale_jitter": 0.0,
            "translate_frac": 0.0,
            "brightness_jitter": 0.0,
            "contrast_jitter": 0.0,
            "blur_prob": 0.0,
            **overrides,
        }
        attack = build_attack("eot_pgd", params)
        self.assertIsInstance(attack, EOTPGDAttack)
        return attack

    def test_registry_aliases_resolve_expected_classes(self) -> None:
        available = set(list_available_attacks())
        self.assertIn("pgd", available)
        self.assertIn("ifgsm", available)
        self.assertIn("bim", available)
        self.assertIn("eot_pgd", available)
        self.assertIn("pgd_eot", available)

        self.assertIsInstance(build_attack("pgd"), PGDAttack)
        self.assertIsInstance(build_attack("ifgsm"), PGDAttack)
        self.assertIsInstance(build_attack("bim"), PGDAttack)
        self.assertIsInstance(build_attack("eot_pgd"), EOTPGDAttack)
        self.assertIsInstance(build_attack("pgd_eot"), EOTPGDAttack)

    def test_unsupported_attack_alias_lists_supported_names(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported attack 'not_a_real_attack'"):
            build_attack("not_a_real_attack")

    def test_param_validation_rejects_invalid_values(self) -> None:
        invalid_pgd = [
            {"epsilon": 0.0},
            {"epsilon": -0.1},
            {"epsilon": math.inf},
            {"alpha": 0.0},
            {"alpha": math.nan},
            {"steps": 0},
            {"steps": 1.5},
            {"restarts": 0},
        ]
        for params in invalid_pgd:
            with self.assertRaises(ValueError):
                self._build_pgd(**params)

        invalid_eot = [
            {"eot_samples": 0},
            {"eot_samples": 1.5},
            {"scale_jitter": -0.1},
            {"scale_jitter": 1.0},
            {"translate_frac": -0.1},
            {"translate_frac": 0.5},
            {"brightness_jitter": -0.1},
            {"contrast_jitter": 1.0},
            {"blur_prob": -0.1},
            {"blur_prob": 2.0},
        ]
        for params in invalid_eot:
            with self.assertRaises(ValueError):
                self._build_eot(**params)

    def test_tensor_mode_contract_shape_dtype_device_bounds_no_inplace(self) -> None:
        model = DummyDetectionModel().eval()
        image = torch.rand(1, 3, 65, 79, dtype=torch.float32, device="cpu")
        image_before = image.clone()
        pgd = self._build_pgd(steps=3)
        eot = self._build_eot(steps=3, eot_samples=3)

        adv_pgd = pgd.apply(image, model)
        adv_eot = eot.apply(image, model, seed=42)

        for attack, adv in ((pgd, adv_pgd), (eot, adv_eot)):
            self.assertIsInstance(adv, torch.Tensor)
            self.assertEqual(tuple(adv.shape), tuple(image.shape))
            self.assertEqual(adv.dtype, image.dtype)
            self.assertEqual(adv.device, image.device)
            self.assertGreaterEqual(float(adv.min().item()), 0.0)
            self.assertLessEqual(float(adv.max().item()), 1.0)
            linf = float((adv - image).abs().amax().item())
            self.assertLessEqual(linf, float(attack.epsilon) + 1e-6)

        self.assertTrue(torch.allclose(image, image_before), "Input tensor modified in-place")

    def test_deterministic_with_fixed_seed(self) -> None:
        model = DummyDetectionModel().eval()
        image = torch.rand(1, 3, 64, 80)
        pgd = self._build_pgd(random_start=True)
        eot = self._build_eot(random_start=True, eot_samples=2, scale_jitter=0.05, translate_frac=0.02)

        adv_a = pgd.apply(image, model, seed=123)
        adv_b = pgd.apply(image, model, seed=123)
        self.assertTrue(torch.allclose(adv_a, adv_b))

        adv_c = eot.apply(image, model, seed=456)
        adv_d = eot.apply(image, model, seed=456)
        self.assertTrue(torch.allclose(adv_c, adv_d))

    def test_different_seeds_change_randomized_outputs(self) -> None:
        model = DummyDetectionModel().eval()
        image = torch.rand(1, 3, 64, 80)
        pgd = self._build_pgd(random_start=True, steps=3)
        eot = self._build_eot(
            random_start=True,
            steps=3,
            eot_samples=2,
            scale_jitter=0.05,
            translate_frac=0.02,
            brightness_jitter=0.03,
            contrast_jitter=0.03,
        )
        adv_seed_1 = pgd.apply(image, model, seed=11)
        adv_seed_2 = pgd.apply(image, model, seed=22)
        self.assertFalse(torch.allclose(adv_seed_1, adv_seed_2))

        eot_seed_1 = eot.apply(image, model, seed=33)
        eot_seed_2 = eot.apply(image, model, seed=44)
        self.assertFalse(torch.allclose(eot_seed_1, eot_seed_2))

    def test_eot_random_transform_preserves_dimensions(self) -> None:
        eot = self._build_eot(
            scale_jitter=0.2,
            translate_frac=0.1,
            brightness_jitter=0.1,
            contrast_jitter=0.1,
            blur_prob=0.5,
        )
        x = torch.rand(1, 3, 71, 83)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(42)
        y = eot._random_transform(x, generator=generator)
        self.assertEqual(tuple(y.shape), tuple(x.shape))

    def test_eot_transforms_preserve_gradient_flow(self) -> None:
        eot = self._build_eot(
            scale_jitter=0.2,
            translate_frac=0.05,
            brightness_jitter=0.1,
            contrast_jitter=0.1,
            blur_prob=0.3,
        )
        x = torch.rand(1, 3, 64, 80, requires_grad=True)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(123)
        y = eot._random_transform(x, generator=generator)
        loss = y.mean()
        loss.backward()
        self.assertIsNotNone(x.grad)
        assert x.grad is not None
        self.assertTrue(torch.isfinite(x.grad).all())

    def test_eot_samples_count_is_respected(self) -> None:
        model = DummyDetectionModel().eval()
        image = torch.rand(1, 3, 64, 80)
        eot = self._build_eot(steps=2, eot_samples=3)

        with patch.object(
            eot, "_random_transform", wraps=eot._random_transform
        ) as mocked_transform:
            _ = eot.apply(image, model, seed=101)
            self.assertEqual(mocked_transform.call_count, eot.steps * eot.eot_samples)

    def test_noop_eot_matches_pgd_under_same_budget(self) -> None:
        model = DummyDetectionModel().eval()
        image = torch.rand(1, 3, 64, 80)
        pgd = self._build_pgd(steps=3, random_start=False, restarts=1)
        eot = self._build_eot(
            steps=3,
            random_start=False,
            restarts=1,
            eot_samples=1,
            scale_jitter=0.0,
            translate_frac=0.0,
            brightness_jitter=0.0,
            contrast_jitter=0.0,
            blur_prob=0.0,
        )
        adv_pgd = pgd.apply(image, model, seed=7)
        adv_eot = eot.apply(image, model, seed=7)
        self.assertTrue(torch.allclose(adv_pgd, adv_eot, atol=1e-6, rtol=1e-5))

    def test_directory_mode_writes_outputs(self) -> None:
        model = DummyDetectionModel().eval()
        pgd = self._build_pgd(steps=2)
        eot = self._build_eot(steps=2)

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir(parents=True, exist_ok=True)
            img_path = source / "img.jpg"
            image = np.random.randint(0, 255, size=(64, 80, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), image)

            out_pgd = Path(tmp) / "pgd"
            out_eot = Path(tmp) / "eot"
            pgd.apply(source, out_pgd, model=model, seed=4)
            eot.apply(source, out_eot, model=model, seed=7)

            self.assertTrue((out_pgd / "img.jpg").exists())
            self.assertTrue((out_eot / "img.jpg").exists())

    def test_seed_reproducibility_in_directory_mode(self) -> None:
        model = DummyDetectionModel().eval()
        pgd = self._build_pgd(steps=3, random_start=True)
        eot = self._build_eot(
            alpha=0.0015,
            steps=3,
            random_start=True,
            eot_samples=2,
            scale_jitter=0.05,
            translate_frac=0.02,
            brightness_jitter=0.02,
            contrast_jitter=0.02,
            blur_prob=0.0,
        )
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir(parents=True, exist_ok=True)
            image = np.random.randint(0, 255, size=(64, 80, 3), dtype=np.uint8)
            cv2.imwrite(str(source / "img.jpg"), image)
            pgd_a = Path(tmp) / "pgd_a"
            pgd_b = Path(tmp) / "pgd_b"
            out_a = Path(tmp) / "out_a"
            out_b = Path(tmp) / "out_b"
            pgd.apply(source, pgd_a, model=model, seed=99)
            pgd.apply(source, pgd_b, model=model, seed=99)
            eot.apply(source, out_a, model=model, seed=123)
            eot.apply(source, out_b, model=model, seed=123)
            pgd_hash_a = hashlib.sha256((pgd_a / "img.jpg").read_bytes()).hexdigest()
            pgd_hash_b = hashlib.sha256((pgd_b / "img.jpg").read_bytes()).hexdigest()
            hash_a = hashlib.sha256((out_a / "img.jpg").read_bytes()).hexdigest()
            hash_b = hashlib.sha256((out_b / "img.jpg").read_bytes()).hexdigest()
            self.assertEqual(pgd_hash_a, pgd_hash_b)
            self.assertEqual(hash_a, hash_b)

    def test_dry_run_resolves_pgd_and_eot(self) -> None:
        script = ROOT / "run_experiment.py"
        for attack_name in ("pgd", "eot_pgd"):
            proc = subprocess.run(
                [sys.executable, str(script), f"attack={attack_name}", "dry_run=true"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertIn('"attack":', proc.stdout)
            self.assertIn(f'"{attack_name}"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
