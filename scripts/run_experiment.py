#!/usr/bin/env python3
import subprocess
import os

MODEL = "yolov8n.pt"
DATA_YAML = "configs/coco_subset500.yaml"
IMAGE_DIR = "coco/val2017_subset500/images"

CONFS = [0.25, 0.50, 0.75]
IOU = 0.7
IMG_SIZE = 640
SEED = 42
BLUR_KERNEL = 9  # adjust if needed

def run_command(cmd):
    print("\nRunning:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def run_baseline(conf):
    run_name = f"baseline_conf{str(conf).replace('.', '')}"

    run_command([
        "yolo", "val",
        f"model={MODEL}",
        f"data={DATA_YAML}",
        f"imgsz={IMG_SIZE}",
        f"conf={conf}",
        f"iou={IOU}",
        "save_json=True",
        f"project=results",
        f"name={run_name}",
        "exist_ok=True"
    ])

    collect_metrics(run_name, "none", conf)

def run_blur_attack(conf):
    run_name = f"blur_k{BLUR_KERNEL}_conf{str(conf).replace('.', '')}"

    # Apply blur attack first (assumes you already have blur_attack.py)
    run_command([
        "python",
        "attacks/blur/blur_attack.py",
        f"--kernel={BLUR_KERNEL}"
    ])

    run_command([
        "yolo", "val",
        f"model={MODEL}",
        f"data={DATA_YAML}",
        f"imgsz={IMG_SIZE}",
        f"conf={conf}",
        f"iou={IOU}",
        "save_json=True",
        f"project=results",
        f"name={run_name}",
        "exist_ok=True"
    ])

    collect_metrics(run_name, f"blur_k{BLUR_KERNEL}", conf)

def collect_metrics(run_name, attack_name, conf):
    run_command([
        "python",
        "scripts/collect_metrics.py",
        f"--run_name={run_name}",
        f"--attack={attack_name}",
        f"--conf={conf}",
        f"--iou={IOU}",
        f"--imgsz={IMG_SIZE}",
        f"--seed={SEED}"
    ])

if __name__ == "__main__":
    for conf in CONFS:
        run_baseline(conf)
        run_blur_attack(conf)

    print("\nAll experiments completed successfully.")