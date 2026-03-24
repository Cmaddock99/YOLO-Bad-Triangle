"""End-to-end pipeline integration test.

Exercises the full run_experiment → attack → defense → metrics path
with a real COCO image and the real YOLO model (yolo26n.pt).  Covers
behavioral properties that mocked unit tests cannot verify:

  - Adversarial images differ pixel-by-pixel from clean originals
  - Defense preprocessing changes image content
  - Derived metrics (detection_drop, defense_recovery) are computable
    from real run outputs without errors

All three pipeline stages (baseline, fgsm, fgsm+median_preprocess) run once
in setUpClass and results are shared across test methods to keep execution
time reasonable (~5–15 s total on CPU).

Skip conditions:
  - yolo26n.pt not found on disk (model not downloaded)
  - Real COCO images not found on disk (dataset not present)
"""
from __future__ import annotations

import json
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cv2
import numpy as np

from lab.runners.run_experiment import UnifiedExperimentRunner
from lab.eval.derived_metrics import compute_detection_drop, compute_defense_recovery

_YOLO_MODEL = "yolo26n.pt"
_COCO_DATASET = str(ROOT / "configs/coco_subset500.yaml")
_IMAGES_DIR = ROOT / "coco/val2017_subset500/images"


def _build_config(
    run_name: str,
    output_root: str,
    source_dir: str,
    *,
    attack: str = "none",
    attack_params: dict[str, Any] | None = None,
    defense: str = "none",
    defense_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "model": {"name": "yolo", "params": {"model": _YOLO_MODEL}},
        "data": {"source_dir": source_dir},
        "attack": {"name": attack, "params": attack_params or {}},
        "defense": {"name": defense, "params": defense_params or {}},
        "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
        "validation": {"enabled": False, "dataset": _COCO_DATASET, "params": {}},
        "runner": {
            "seed": 42,
            "max_images": 1,
            "output_root": output_root,
            "run_name": run_name,
        },
    }


class EndToEndPipelineTests(unittest.TestCase):
    """Integration tests: real YOLO model, real COCO images, real attacks/defenses."""

    _tmpdir: tempfile.TemporaryDirectory
    _root: Path
    _source: Path
    _baseline_dir: Path
    _fgsm_dir: Path
    _defense_dir: Path
    _skip_reason: str | None = None

    @classmethod
    def setUpClass(cls) -> None:
        # Check prerequisites before doing anything expensive.
        if not (_IMAGES_DIR / "000000030828.jpg").exists():
            cls._skip_reason = f"COCO images not found at {_IMAGES_DIR}"
            return
        if not Path(_YOLO_MODEL).exists() and not Path(ROOT / _YOLO_MODEL).exists():
            cls._skip_reason = f"YOLO model not found: {_YOLO_MODEL}"
            return

        cls._tmpdir = tempfile.TemporaryDirectory()
        cls._root = Path(cls._tmpdir.name)
        cls._source = cls._root / "images"
        cls._source.mkdir()

        # Copy one real COCO image into the temp source dir.
        real_img = _IMAGES_DIR / "000000030828.jpg"
        shutil.copy(str(real_img), str(cls._source / real_img.name))

        outputs = str(cls._root / "outputs")

        def _run(run_name: str, **kwargs: Any) -> Path:
            config = _build_config(
                run_name, outputs, str(cls._source), **kwargs
            )
            summary = UnifiedExperimentRunner(config=config).run()
            return Path(summary["run_dir"])

        cls._baseline_dir = _run("e2e_baseline")
        cls._fgsm_dir = _run(
            "e2e_fgsm", attack="fgsm", attack_params={"epsilon": 0.03}
        )
        cls._defense_dir = _run(
            "e2e_fgsm_median",
            attack="fgsm",
            attack_params={"epsilon": 0.03},
            defense="median_preprocess",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "_tmpdir"):
            cls._tmpdir.cleanup()

    def setUp(self) -> None:
        if self._skip_reason:
            self.skipTest(self._skip_reason)

    # ------------------------------------------------------------------
    # Output contract assertions
    # ------------------------------------------------------------------

    def test_all_stages_write_required_artifacts(self) -> None:
        """metrics.json, run_summary.json, predictions.jsonl, resolved_config.yaml."""
        for run_dir in (self._baseline_dir, self._fgsm_dir, self._defense_dir):
            with self.subTest(run=run_dir.name):
                self.assertTrue((run_dir / "metrics.json").exists())
                self.assertTrue((run_dir / "run_summary.json").exists())
                self.assertTrue((run_dir / "predictions.jsonl").exists())
                self.assertTrue((run_dir / "resolved_config.yaml").exists())

    def test_metrics_schema_version_is_correct(self) -> None:
        for run_dir in (self._baseline_dir, self._fgsm_dir, self._defense_dir):
            with self.subTest(run=run_dir.name):
                metrics = json.loads((run_dir / "metrics.json").read_text())
                self.assertEqual(metrics["schema_version"], "framework_metrics/v1")

    def test_metrics_prediction_keys_are_present(self) -> None:
        for run_dir in (self._baseline_dir, self._fgsm_dir, self._defense_dir):
            with self.subTest(run=run_dir.name):
                preds = json.loads((run_dir / "metrics.json").read_text())["predictions"]
                for key in ("image_count", "images_with_detections", "total_detections"):
                    self.assertIn(key, preds)
                self.assertEqual(preds["image_count"], 1)

    def test_run_summary_keys_are_present(self) -> None:
        for run_dir in (self._baseline_dir, self._fgsm_dir, self._defense_dir):
            with self.subTest(run=run_dir.name):
                summary = json.loads((run_dir / "run_summary.json").read_text())
                for key in ("run_dir", "processed_image_count", "prediction_record_count"):
                    self.assertIn(key, summary)

    def test_predictions_jsonl_has_at_least_one_line(self) -> None:
        for run_dir in (self._baseline_dir, self._fgsm_dir, self._defense_dir):
            with self.subTest(run=run_dir.name):
                lines = [
                    ln for ln in
                    (run_dir / "predictions.jsonl").read_text().splitlines()
                    if ln.strip()
                ]
                self.assertGreater(len(lines), 0)

    # ------------------------------------------------------------------
    # Behavioral assertions
    # ------------------------------------------------------------------

    def test_fgsm_attack_modifies_image_pixels(self) -> None:
        """Adversarial images must differ pixel-by-pixel from the clean originals."""
        orig_path = list(self._source.glob("*.jpg"))[0]
        orig = cv2.imread(str(orig_path))

        attacked_imgs = list((self._fgsm_dir / "images").glob("*.jpg"))
        self.assertGreater(len(attacked_imgs), 0, "No attacked images written to images/")

        attacked = cv2.imread(str(attacked_imgs[0]))
        self.assertIsNotNone(attacked, f"Could not read attacked image: {attacked_imgs[0]}")
        self.assertEqual(orig.shape, attacked.shape, "Shape mismatch between original and attacked")

        diff = np.abs(orig.astype(np.int32) - attacked.astype(np.int32))
        self.assertGreater(
            int(diff.sum()), 0,
            "FGSM attack produced no pixel change — attack is not being applied",
        )

    def test_median_defense_changes_image_relative_to_attack_only(self) -> None:
        """Defense preprocessing must alter the attacked image content."""
        fgsm_imgs = sorted((self._fgsm_dir / "images").glob("*.jpg"))
        def_imgs = sorted((self._defense_dir / "images").glob("*.jpg"))

        self.assertGreater(len(fgsm_imgs), 0)
        self.assertGreater(len(def_imgs), 0)

        fgsm_arr = cv2.imread(str(fgsm_imgs[0]))
        def_arr = cv2.imread(str(def_imgs[0]))

        self.assertIsNotNone(fgsm_arr)
        self.assertIsNotNone(def_arr)
        self.assertEqual(fgsm_arr.shape, def_arr.shape)

        diff = np.abs(fgsm_arr.astype(np.int32) - def_arr.astype(np.int32))
        self.assertGreater(
            int(diff.sum()), 0,
            "median_preprocess produced no pixel change — defense preprocessing not applied",
        )

    # ------------------------------------------------------------------
    # Derived metric assertions
    # ------------------------------------------------------------------

    def test_detection_drop_is_computable_and_finite(self) -> None:
        base_det = json.loads((self._baseline_dir / "metrics.json").read_text())["predictions"]["total_detections"]
        atk_det = json.loads((self._fgsm_dir / "metrics.json").read_text())["predictions"]["total_detections"]

        if base_det == 0:
            self.skipTest("Baseline produced 0 detections on this image — cannot compute drop")

        drop = compute_detection_drop(base_det, atk_det)
        self.assertIsNotNone(drop)
        self.assertGreaterEqual(drop, -1.0)
        self.assertLessEqual(drop, 1.0)
        self.assertEqual(drop, (base_det - atk_det) / base_det)

    def test_defense_recovery_is_computable_when_attack_has_effect(self) -> None:
        base_det = json.loads((self._baseline_dir / "metrics.json").read_text())["predictions"]["total_detections"]
        atk_det = json.loads((self._fgsm_dir / "metrics.json").read_text())["predictions"]["total_detections"]
        def_det = json.loads((self._defense_dir / "metrics.json").read_text())["predictions"]["total_detections"]

        if base_det == atk_det:
            self.skipTest("Attack had no effect on detections — recovery is undefined")

        recovery = compute_defense_recovery(base_det, atk_det, def_det)
        # recovery can be None only if denominator is 0 (already handled above)
        self.assertIsNotNone(recovery)
        self.assertIsInstance(recovery, float)


if __name__ == "__main__":
    unittest.main()
