from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.experiment_runner import ExperimentRunner


class _DummyTorchDetector(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stride = torch.tensor([32.0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        score = x.mean(dim=(1, 2, 3), keepdim=False).unsqueeze(-1)
        return score.unsqueeze(-1).repeat(1, 10, 6)


class _DummyUltralyticsModel:
    def __init__(self) -> None:
        self.model = _DummyTorchDetector().eval()

    def predict(self, **kwargs: object) -> object:
        source = Path(str(kwargs["source"]))
        project = Path(str(kwargs["project"]))
        run_name = str(kwargs["name"])
        run_dir = project / run_name
        labels_dir = run_dir / "labels"
        labels_dir.mkdir(parents=True, exist_ok=True)
        for image_file in source.rglob("*.jpg"):
            stem = image_file.stem
            (labels_dir / f"{stem}.txt").write_text("0 0.5 0.5 0.2 0.2 0.8\n")
        return []

    def val(self, **kwargs: object) -> object:
        class _Box:
            map50 = 0.5
            map = 0.4
            mp = 0.3
            mr = 0.2

        class _Val:
            box = _Box()

        return _Val()


class _DummyYOLOModel:
    def __init__(self, model: str | None = None) -> None:
        self.model = model
        self._model = _DummyUltralyticsModel()

    def predict(self, **kwargs: object) -> object:
        return self._model.predict(**kwargs)

    def validate(self, **kwargs: object) -> object:
        return self._model.val(**kwargs)


class RunnerPGDEOTSmokeMatrixTests(unittest.TestCase):
    def test_tiny_smoke_config_exists(self) -> None:
        config_path = ROOT / "configs" / "pgd_eot_tiny_smoke_matrix.yaml"
        self.assertTrue(config_path.exists())
        loaded = yaml.safe_load(config_path.read_text())
        experiments = loaded.get("experiments", [])
        names = [exp.get("name") for exp in experiments]
        self.assertIn("baseline_tiny_smoke", names)
        self.assertIn("pgd_tiny_smoke", names)
        self.assertIn("eot_pgd_tiny_smoke", names)

    def test_runner_smoke_matrix_writes_artifacts_and_metrics_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_dir = root / "dataset" / "images"
            labels_dir = root / "dataset" / "labels"
            image_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)
            sample = np.random.randint(0, 255, size=(64, 80, 3), dtype=np.uint8)
            cv2.imwrite(str(image_dir / "sample.jpg"), sample)
            (labels_dir / "sample.txt").write_text("0 0.5 0.5 0.2 0.2\n")
            data_yaml = root / "data.yaml"
            data_yaml.write_text(yaml.safe_dump({"names": {0: "person"}}))

            config = {
                "model": {"path": "dummy.pt", "label": "dummy"},
                "data": {"data_yaml": str(data_yaml), "image_dir": str(image_dir)},
                "runner": {
                    "confs": [0.25],
                    "iou": 0.7,
                    "imgsz": 640,
                    "seed": 42,
                    "output_root": str(root / "outputs"),
                    "metrics_csv": "metrics_summary.csv",
                    "run_validation": False,
                },
                "experiments": [
                    {
                        "name": "baseline_tiny_smoke",
                        "attack": "none",
                        "defense": "none",
                        "run_name_template": "baseline-tiny-smoke-conf{conf_token}",
                        "run_validation": False,
                    },
                    {
                        "name": "pgd_tiny_smoke",
                        "attack": "pgd",
                        "attack_params": {
                            "epsilon": 0.008,
                            "alpha": 0.002,
                            "steps": 2,
                            "random_start": False,
                            "restarts": 1,
                        },
                        "defense": "none",
                        "run_name_template": "pgd-tiny-smoke-conf{conf_token}",
                        "run_validation": False,
                    },
                    {
                        "name": "eot_pgd_tiny_smoke",
                        "attack": "eot_pgd",
                        "attack_params": {
                            "epsilon": 0.008,
                            "alpha": 0.002,
                            "steps": 2,
                            "random_start": False,
                            "restarts": 1,
                            "eot_samples": 1,
                            "scale_jitter": 0.0,
                            "translate_frac": 0.0,
                            "brightness_jitter": 0.0,
                            "contrast_jitter": 0.0,
                            "blur_prob": 0.0,
                        },
                        "defense": "none",
                        "run_name_template": "eot-pgd-tiny-smoke-conf{conf_token}",
                        "run_validation": False,
                    },
                ],
            }

            with patch("lab.models.YOLOModel", _DummyYOLOModel):
                runner = ExperimentRunner.from_dict(config)
                rows = runner.run()

            self.assertEqual(len(rows), 3)
            run_names = [row["run_name"] for row in rows]
            attack_by_run = {row["run_name"]: row["attack"] for row in rows}
            output_root = root / "outputs"
            csv_path = output_root / "metrics_summary.csv"
            self.assertTrue(csv_path.exists())

            with csv_path.open(newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                csv_rows = list(reader)
            self.assertEqual(len(csv_rows), 3)
            fieldnames = list(reader.fieldnames or [])
            self.assertIn("row_status", fieldnames)
            self.assertIn("missing_metric_fields", fieldnames)
            self.assertIn("error_reason", fieldnames)

            for run_name in run_names:
                run_dir = output_root / run_name
                self.assertTrue(run_dir.exists())
                self.assertTrue((run_dir / "labels").exists())
                attacked_dir = output_root / "_intermediates" / run_name / "attacked"
                defended_dir = output_root / "_intermediates" / run_name / "defended"
                if attack_by_run[run_name] == "none":
                    self.assertFalse(attacked_dir.exists())
                else:
                    self.assertTrue(attacked_dir.exists())
                # Defense is "none" in this smoke matrix, so defense artifacts are not materialized.
                self.assertFalse(defended_dir.exists())
            self.assertTrue(all(row["row_status"] in {"ok", "partial"} for row in csv_rows))


if __name__ == "__main__":
    unittest.main()
