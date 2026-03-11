from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners import ExperimentRunner


def main() -> None:
    runner = ExperimentRunner.from_dict(
        {
            "model": {"path": "yolov8n.pt"},
            "data": {
                "data_yaml": "configs/coco_subset500.yaml",
                "image_dir": "coco/val2017_subset500/images",
            },
            "runner": {
                "confs": [0.25],
                "iou": 0.7,
                "imgsz": 640,
                "seed": 42,
                "output_root": "attack_results",
                "metrics_csv": "metrics_summary.csv",
            },
            "experiments": [
                {
                    "name": "attack_iteration1",
                    "run_name_template": "attack_iteration1",
                    "attack": "blur",
                    "attack_params": {"kernel_size": 9},
                    "defense": "none",
                    "run_validation": False,
                }
            ],
        }
    )
    rows = runner.run()
    print("Attack complete.")
    print(rows[0] if rows else {})


if __name__ == "__main__":
    main()