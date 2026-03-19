from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.experiment_runner import ExperimentRunner


class RunnerValidationDatasetTests(unittest.TestCase):
    def test_validation_data_yaml_is_created_with_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_dir = root / "dataset" / "images"
            labels_dir = root / "dataset" / "labels"
            image_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)
            (labels_dir / "sample.txt").write_text("0 0.5 0.5 0.2 0.2")

            data_yaml = root / "data.yaml"
            data_yaml.write_text(yaml.safe_dump({"names": {0: "person"}}))

            output_root = root / "outputs"
            transformed = output_root / "_intermediates" / "run1" / "attacked"
            transformed.mkdir(parents=True, exist_ok=True)
            (transformed / "sample.jpg").write_bytes(b"fake")

            runner = ExperimentRunner(
                model_path="yolov8n.pt",
                model_label="yolo8",
                data_yaml=str(data_yaml),
                image_dir=image_dir,
                confs=[0.25],
                iou=0.7,
                imgsz=640,
                seed=42,
                output_root=output_root,
                metrics_csv="metrics_summary.csv",
                default_run_validation=True,
                clean_existing_runs=True,
                experiments=[],
            )

            generated = runner._validation_data_yaml_for_run(
                run_name="run1",
                source_dir=transformed,
            )
            generated_path = Path(generated)
            self.assertTrue(generated_path.is_file())

            loaded = yaml.safe_load(generated_path.read_text())
            self.assertEqual(loaded["train"], "images")
            self.assertEqual(loaded["val"], "images")
            self.assertEqual(loaded["names"], {0: "person"})

            dataset_root = generated_path.parent
            self.assertTrue((dataset_root / "images").exists())
            self.assertTrue((dataset_root / "labels").exists())
            # "images" must be a real directory so dataset loaders resolve
            # sibling labels under the same dataset root.
            self.assertTrue((dataset_root / "images").is_dir())
            self.assertFalse((dataset_root / "images").is_symlink())
            self.assertTrue((dataset_root / "images" / "sample.jpg").exists())

    def test_validation_data_yaml_requires_labels_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_dir = root / "dataset" / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            data_yaml = root / "data.yaml"
            data_yaml.write_text(yaml.safe_dump({"names": {0: "person"}}))

            runner = ExperimentRunner(
                model_path="yolov8n.pt",
                model_label="yolo8",
                data_yaml=str(data_yaml),
                image_dir=image_dir,
                confs=[0.25],
                iou=0.7,
                imgsz=640,
                seed=42,
                output_root=root / "outputs",
                metrics_csv="metrics_summary.csv",
                default_run_validation=True,
                clean_existing_runs=True,
                experiments=[],
            )

            source_dir = root / "attacked"
            source_dir.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(FileNotFoundError):
                runner._validation_data_yaml_for_run(run_name="run_missing_labels", source_dir=source_dir)

    def test_from_dict_uses_runner_validation_default(self) -> None:
        config = {
            "model": {"path": "yolov8n.pt", "label": "yolo8"},
            "data": {
                "data_yaml": "configs/coco_subset500.yaml",
                "image_dir": "coco/val2017_subset500/images",
            },
            "runner": {
                "run_validation": False,
                "confs": [0.25],
                "iou": 0.7,
                "imgsz": 640,
                "seed": 42,
                "output_root": "outputs",
                "metrics_csv": "metrics_summary.csv",
            },
            "experiments": [
                {
                    "name": "baseline",
                    "attack": "none",
                    "defense": "none",
                    "run_name_template": "baseline_conf{conf_token}",
                }
            ],
        }
        runner = ExperimentRunner.from_dict(config)
        self.assertFalse(runner.default_run_validation)
        self.assertTrue(runner.clean_existing_runs)

    def test_run_name_safety_blocks_traversal_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = ExperimentRunner(
                model_path="yolov8n.pt",
                model_label="yolo8",
                data_yaml=str(root / "data.yaml"),
                image_dir=root / "images",
                confs=[0.25],
                iou=0.7,
                imgsz=640,
                seed=42,
                output_root=root / "outputs",
                metrics_csv="metrics_summary.csv",
                default_run_validation=True,
                clean_existing_runs=True,
                experiments=[],
            )
            with self.assertRaises(ValueError):
                runner._assert_run_name_safe("../escape")
            with self.assertRaises(ValueError):
                runner._assert_run_name_safe("nested/run")

    def test_metrics_csv_path_must_resolve_under_output_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = ExperimentRunner(
                model_path="yolov8n.pt",
                model_label="yolo8",
                data_yaml=str(root / "data.yaml"),
                image_dir=root / "images",
                confs=[0.25],
                iou=0.7,
                imgsz=640,
                seed=42,
                output_root=root / "outputs",
                metrics_csv="../outside.csv",
                default_run_validation=True,
                clean_existing_runs=True,
                experiments=[],
            )
            with self.assertRaises(ValueError):
                runner._metrics_csv_path()

    def test_reset_dir_blocks_overwrite_when_clean_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = ExperimentRunner(
                model_path="yolov8n.pt",
                model_label="yolo8",
                data_yaml=str(root / "data.yaml"),
                image_dir=root / "images",
                confs=[0.25],
                iou=0.7,
                imgsz=640,
                seed=42,
                output_root=root / "outputs",
                metrics_csv="metrics_summary.csv",
                default_run_validation=True,
                clean_existing_runs=False,
                experiments=[],
            )
            target = root / "outputs" / "existing"
            target.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(FileExistsError):
                runner._reset_dir(target, context="existing test dir")

    def test_from_dict_respects_clean_existing_runs_flag(self) -> None:
        config = {
            "model": {"path": "yolov8n.pt", "label": "yolo8"},
            "data": {
                "data_yaml": "configs/coco_subset500.yaml",
                "image_dir": "coco/val2017_subset500/images",
            },
            "runner": {
                "run_validation": False,
                "clean_existing_runs": False,
            },
            "experiments": [
                {
                    "name": "baseline",
                    "attack": "none",
                    "defense": "none",
                    "run_name_template": "baseline_conf{conf_token}",
                }
            ],
        }
        runner = ExperimentRunner.from_dict(config)
        self.assertFalse(runner.clean_existing_runs)


if __name__ == "__main__":
    unittest.main()
