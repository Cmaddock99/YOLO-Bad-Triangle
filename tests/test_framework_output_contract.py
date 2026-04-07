from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import cv2
import numpy as np
import yaml

from lab.runners.run_experiment import UnifiedExperimentRunner, _assert_metrics_payload_contract


class _DummyFrameworkModel:
    def __init__(self, *, raise_on_validate: bool = False) -> None:
        self._raise_on_validate = raise_on_validate

    def load(self) -> None:
        return

    def predict(self, images: list[Path], **kwargs: Any) -> list[dict[str, Any]]:
        del kwargs
        rows: list[dict[str, Any]] = []
        for image in images:
            rows.append(
                {
                    "image_id": image.name,
                    "boxes": [[0.1, 0.1, 0.5, 0.5]],
                    "scores": [0.9],
                    "class_ids": [0],
                    "metadata": {},
                }
            )
        return rows

    def validate(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        del dataset, kwargs
        if self._raise_on_validate:
            raise RuntimeError("validation intentionally failed in test")
        return {"precision": 0.7, "recall": 0.6, "mAP50": 0.5, "mAP50-95": 0.4}


class _DummyEmptyPredictionModel(_DummyFrameworkModel):
    def predict(self, images: list[Path], **kwargs: Any) -> list[dict[str, Any]]:
        del images, kwargs
        return []


class _DummyUnsupportedValidationModel(_DummyFrameworkModel):
    def validate(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        del dataset, kwargs
        return {
            "mAP50": None,
            "mAP50-95": None,
            "precision": None,
            "recall": None,
            "_status": "not_supported",
        }


class _RecordingAttack:
    def __init__(self) -> None:
        self.input_means: list[int] = []
        self.seeds: list[int] = []

    def apply(self, image: np.ndarray, *, model: Any, seed: int) -> tuple[np.ndarray, dict[str, Any]]:
        del model
        self.input_means.append(int(image.mean()))
        self.seeds.append(seed)
        transformed = np.clip(image.astype(np.int16) + 5, 0, 255).astype(np.uint8)
        return transformed, {"objective_mode": "untargeted_conf_suppression"}


class _RecordingDefense:
    def __init__(self) -> None:
        self.preprocess_inputs: list[tuple[int, str | None]] = []

    def preprocess(
        self,
        image: np.ndarray,
        *,
        attack_hint: str | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        self.preprocess_inputs.append((int(image.mean()), attack_hint))
        defended = np.clip(image.astype(np.int16) + 10, 0, 255).astype(np.uint8)
        return defended, {}

    def postprocess(self, records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return list(records), {}


@dataclass
class _ResolvedAttackWithOptionalParam:
    epsilon: float = 0.016
    steps: int = 20
    optional_scale: float | None = None
    objective_mode: str = "untargeted_conf_suppression"
    target_class: int | None = None
    preserve_weight: float = 0.25
    attack_roi: str | None = None

    def apply(self, image: np.ndarray, *, model: Any, seed: int) -> tuple[np.ndarray, dict[str, Any]]:
        del model, seed
        return image, {
            "objective_mode": self.objective_mode,
            "target_class": self.target_class,
            "preserve_weight": self.preserve_weight,
            "attack_roi": self.attack_roi,
        }


class _PassthroughDefense:
    def preprocess(
        self,
        image: np.ndarray,
        *,
        attack_hint: str | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del attack_hint
        return image, {}

    def postprocess(self, records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return list(records), {}


class FrameworkOutputContractTests(unittest.TestCase):
    def _write_image(self, path: Path, *, pixel_value: int = 127) -> None:
        image = np.full((40, 60, 3), pixel_value, dtype=np.uint8)
        ok = cv2.imwrite(str(path), image)
        self.assertTrue(ok)

    def _write_legacy_metrics_csv(self, path: Path, *, row: dict[str, Any]) -> None:
        headers = [
            "run_name",
            "images_with_detections",
            "total_detections",
            "avg_conf",
            "median_conf",
            "precision",
            "recall",
            "mAP50",
            "mAP50-95",
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerow({name: row.get(name, "") for name in headers})

    def _write_framework_run_artifacts(
        self,
        run_dir: Path,
        *,
        model_name: str,
        attack_name: str,
        defense_name: str,
        seed: int,
        total_detections: int,
        confidence_mean: float,
    ) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "model": {"name": model_name, "params": {}},
                    "attack": {"name": attack_name, "params": {}},
                    "defense": {"name": defense_name, "params": {}},
                    "seed": seed,
                    "prediction_record_count": 1,
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "metrics.json").write_text(
            json.dumps(
                {
                    "predictions": {
                        "image_count": 1,
                        "images_with_detections": 1 if total_detections > 0 else 0,
                        "total_detections": total_detections,
                        "confidence": {"mean": confidence_mean},
                    },
                    "validation": {"status": "missing", "enabled": False, "error": None},
                }
            ),
            encoding="utf-8",
        )

    def test_framework_run_writes_required_artifacts_and_schema_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")
            self._write_image(source / "b.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 42, "output_root": str(root / "outputs"), "run_name": "contract_ok"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()):
                summary = UnifiedExperimentRunner(config=config).run()

            run_dir = Path(summary["run_dir"])
            predictions_path = run_dir / "predictions.jsonl"
            metrics_path = run_dir / "metrics.json"
            run_summary_path = run_dir / "run_summary.json"
            resolved_config_path = run_dir / "resolved_config.yaml"

            self.assertTrue(predictions_path.exists())
            self.assertTrue(metrics_path.exists())
            self.assertTrue(run_summary_path.exists())
            self.assertTrue(resolved_config_path.exists())

            lines = [line for line in predictions_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertGreater(len(lines), 0)

            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertIn("predictions", metrics)
            self.assertIn("validation", metrics)
            self.assertIn("status", metrics["validation"])
            self.assertIn(metrics["validation"]["status"], {"missing", "partial", "complete", "error"})
            for key in ("image_count", "images_with_detections", "total_detections"):
                self.assertIn(key, metrics["predictions"])
            confidence_mean = metrics["predictions"]["confidence"]["mean"]
            self.assertTrue(confidence_mean is None or math.isfinite(float(confidence_mean)))

            run_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
            for key in ("run_dir", "metrics_path", "processed_image_count", "prediction_record_count"):
                self.assertIn(key, run_summary)
            self.assertNotIn("reporting_context", run_summary)
            self.assertIn("pipeline", run_summary)
            self.assertEqual(
                run_summary["pipeline"]["transform_order"],
                ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
            )
            self.assertEqual(run_summary["pipeline"]["semantic_order"], "attack_then_defense")
            self.assertIn("signature", run_summary["attack"])
            self.assertIn("signature", run_summary["defense"])
            self.assertIn("provenance", metrics)
            self.assertEqual(
                metrics["provenance"]["transform_order"],
                ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
            )
            self.assertEqual(metrics["provenance"]["semantic_order"], "attack_then_defense")

            resolved = yaml.safe_load(resolved_config_path.read_text(encoding="utf-8"))
            self.assertEqual(resolved["attack"]["name"], "none")
            self.assertEqual(resolved["defense"]["name"], "none")

    def test_runner_persists_reporting_context_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            reporting_context = {
                "run_role": "baseline",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": True, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "reporting_context": reporting_context,
                "runner": {"seed": 42, "output_root": str(root / "outputs"), "run_name": "contract_reporting_ctx"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()):
                summary = UnifiedExperimentRunner(config=config).run()

            run_summary = json.loads(Path(summary["run_dir"]).joinpath("run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(run_summary["reporting_context"], reporting_context)

    def test_validation_exception_sets_error_status_without_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": True, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 7, "output_root": str(root / "outputs"), "run_name": "contract_val_error"},
            }

            with patch(
                "lab.runners.run_experiment.build_model",
                return_value=_DummyFrameworkModel(raise_on_validate=True),
            ):
                summary = UnifiedExperimentRunner(config=config).run()

            metrics_path = Path(summary["metrics_path"])
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(metrics["validation"]["status"], "error")
            self.assertIsNotNone(metrics["validation"]["error"])

    def test_validation_not_supported_is_persisted_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "faster_rcnn", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": True, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 7, "output_root": str(root / "outputs"), "run_name": "contract_val_unsupported"},
            }

            with patch(
                "lab.runners.run_experiment.build_model",
                return_value=_DummyUnsupportedValidationModel(),
            ):
                summary = UnifiedExperimentRunner(config=config).run()

            metrics_path = Path(summary["metrics_path"])
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(metrics["validation"]["status"], "missing")
            self.assertEqual(metrics["validation"]["capability_supported"], False)
            self.assertEqual(
                metrics["validation"]["capability_reason"],
                "model_adapter_reports_not_supported",
            )

    def test_runner_fails_fast_on_empty_prediction_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 11, "output_root": str(root / "outputs"), "run_name": "contract_empty_pred"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyEmptyPredictionModel()):
                with self.assertRaises(RuntimeError):
                    UnifiedExperimentRunner(config=config).run()

    def test_runner_rejects_malformed_prediction_schema(self) -> None:
        class _DummyMalformedModel(_DummyFrameworkModel):
            def predict(self, images: list[Path], **kwargs: Any) -> list[dict[str, Any]]:
                del images, kwargs
                # Missing required class_ids key.
                return [
                    {
                        "image_id": "bad.jpg",
                        "boxes": [[0.1, 0.1, 0.5, 0.5]],
                        "scores": [0.8],
                        "metadata": {},
                    }
                ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 99, "output_root": str(root / "outputs"), "run_name": "contract_bad_schema"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyMalformedModel()):
                with self.assertRaises(ValueError):
                    UnifiedExperimentRunner(config=config).run()

    def test_runner_applies_attack_before_defense_and_persists_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.png", pixel_value=100)

            attack = _RecordingAttack()
            defense = _RecordingDefense()
            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "fgsm", "params": {}},
                "defense": {"name": "median_preprocess", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 123, "output_root": str(root / "outputs"), "run_name": "attack_then_defense"},
            }

            with (
                patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()),
                patch("lab.runners.run_experiment.build_attack_plugin", return_value=attack),
                patch("lab.runners.run_experiment.build_defense_plugin", return_value=defense),
            ):
                summary = UnifiedExperimentRunner(config=config).run()

            run_dir = Path(summary["run_dir"])
            prepared = cv2.imread(str(run_dir / "images" / "a.png"))
            self.assertIsNotNone(prepared)
            self.assertEqual(attack.input_means, [100])
            self.assertEqual(defense.preprocess_inputs, [(105, "fgsm")])
            self.assertEqual(int(prepared[0, 0, 0]), 115)

            metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
            run_summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metrics["provenance"]["transform_order"],
                ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
            )
            self.assertEqual(metrics["provenance"]["semantic_order"], "attack_then_defense")
            self.assertEqual(
                run_summary["pipeline"]["transform_order"],
                ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
            )
            self.assertEqual(run_summary["pipeline"]["semantic_order"], "attack_then_defense")

    def test_runner_filters_none_params_before_plugin_build_and_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            attack_build_kwargs: dict[str, Any] = {}
            defense_build_kwargs: dict[str, Any] = {}

            def _build_attack(name: str, **kwargs: Any) -> _ResolvedAttackWithOptionalParam:
                self.assertEqual(name, "pgd")
                attack_build_kwargs.update(kwargs)
                self.assertNotIn("epsilon", kwargs)
                return _ResolvedAttackWithOptionalParam(
                    epsilon=0.016,
                    steps=int(kwargs.get("steps", 20)),
                    optional_scale=None,
                )

            def _build_defense(name: str, **kwargs: Any) -> _PassthroughDefense:
                self.assertEqual(name, "median_preprocess")
                defense_build_kwargs.update(kwargs)
                self.assertEqual(kwargs, {})
                return _PassthroughDefense()

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "pgd", "params": {"epsilon": None, "steps": 4}},
                "defense": {"name": "median_preprocess", "params": {"kernel_size": None}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 21, "output_root": str(root / "outputs"), "run_name": "contract_null_params"},
            }

            with (
                patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()),
                patch("lab.runners.run_experiment.build_attack_plugin", side_effect=_build_attack),
                patch("lab.runners.run_experiment.build_defense_plugin", side_effect=_build_defense),
            ):
                summary = UnifiedExperimentRunner(config=config).run()

            self.assertEqual(attack_build_kwargs, {"steps": 4})
            self.assertEqual(defense_build_kwargs, {})

            run_summary = json.loads(
                Path(summary["run_dir"]).joinpath("run_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(run_summary["attack"]["params"], {"epsilon": 0.016, "steps": 4})
            self.assertNotIn("optional_scale", run_summary["attack"]["params"])
            self.assertEqual(run_summary["defense"]["params"], {})

    def test_metrics_payload_contract_accepts_valid_payload(self) -> None:
        payload = {
            "schema_version": "framework_metrics/v1",
            "predictions": {
                "image_count": 1,
                "images_with_detections": 1,
                "total_detections": 1,
            },
            "validation": {"status": "missing", "enabled": False, "error": None},
        }
        _assert_metrics_payload_contract(payload)

    def test_metrics_payload_contract_rejects_invalid_validation_status(self) -> None:
        payload = {
            "schema_version": "framework_metrics/v1",
            "predictions": {
                "image_count": 1,
                "images_with_detections": 1,
                "total_detections": 1,
            },
            "validation": {"status": "bogus", "enabled": False, "error": None},
        }
        with self.assertRaises(ValueError):
            _assert_metrics_payload_contract(payload)

    def test_metrics_payload_contract_rejects_missing_prediction_keys(self) -> None:
        payload = {
            "schema_version": "framework_metrics/v1",
            "predictions": {"image_count": 1},
            "validation": {"status": "missing", "enabled": False, "error": None},
        }
        with self.assertRaises(ValueError):
            _assert_metrics_payload_contract(payload)

    def test_parity_disabled_does_not_write_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "runner": {"seed": 1, "output_root": str(root / "outputs"), "run_name": "parity_disabled"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()):
                summary = UnifiedExperimentRunner(config=config).run()

            run_dir = Path(summary["run_dir"])
            self.assertFalse((run_dir / "parity_report.json").exists())

    def test_summary_enabled_with_only_baseline_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "summary": {"enabled": True},
                "runner": {"seed": 13, "output_root": str(root / "outputs"), "run_name": "summary_baseline"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()):
                summary = UnifiedExperimentRunner(config=config).run()
            run_dir = Path(summary["run_dir"])
            self.assertFalse((run_dir / "experiment_summary.json").exists())

    def test_summary_enabled_with_baseline_and_attack_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs = root / "outputs"
            source = root / "images"
            source.mkdir(parents=True, exist_ok=True)
            self._write_image(source / "a.jpg")

            self._write_framework_run_artifacts(
                outputs / "baseline_existing",
                model_name="yolo",
                attack_name="none",
                defense_name="none",
                seed=17,
                total_detections=10,
                confidence_mean=0.9,
            )
            self._write_framework_run_artifacts(
                outputs / "attack_existing",
                model_name="yolo",
                attack_name="fgsm",
                defense_name="none",
                seed=17,
                total_detections=7,
                confidence_mean=0.8,
            )

            config = {
                "model": {"name": "yolo", "params": {"model": "dummy.pt"}},
                "data": {"source_dir": str(source)},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "predict": {"conf": 0.5, "iou": 0.7, "imgsz": 640},
                "validation": {"enabled": False, "dataset": "configs/coco_subset500.yaml", "params": {}},
                "summary": {"enabled": True},
                "runner": {"seed": 17, "output_root": str(outputs), "run_name": "summary_observer"},
            }

            with patch("lab.runners.run_experiment.build_model", return_value=_DummyFrameworkModel()):
                summary = UnifiedExperimentRunner(config=config).run()
            report_path = Path(summary["run_dir"]) / "experiment_summary.json"
            self.assertTrue(report_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertIn("attack_effectiveness", report)
            self.assertIn("defense_recovery", report)
            self.assertIn("confidence_drop", report)
            self.assertIn("interpretation", report)


if __name__ == "__main__":
    unittest.main()
