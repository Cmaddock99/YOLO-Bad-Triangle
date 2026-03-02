#!/usr/bin/env python3
import os
import argparse
import json
import subprocess
import shutil
import glob
from datetime import datetime
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Run YOLOv8 experiment via API")
    parser.add_argument('--run_name', required=True, help='Name of this run (used as results folder)')
    parser.add_argument('--attack', required=True, choices=['none', 'blur'], help='Attack type or "none"')
    parser.add_argument('--conf', type=float, required=True, help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=0.7, help='IoU threshold')
    parser.add_argument('--imgsz', type=int, required=True, help='Image size (pixels)')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')
    parser.add_argument('--attacks_dir', default='attacks/blur/images', help='Path to attacked images')
    args = parser.parse_args()

    # -------------------------
    # Setup
    # -------------------------

    model = YOLO("yolov8n.pt")

    run_dir = os.path.join("results", args.run_name)

    # Wipe previous run completely (reproducibility)
    if os.path.exists(run_dir):
        shutil.rmtree(run_dir)

    val_dir = os.path.join(run_dir, "val")
    predict_dir = os.path.join(run_dir, "predict")

    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(predict_dir, exist_ok=True)

    # -------------------------
    # 1) Validation (baseline only)
    # -------------------------

    if args.attack == "none":
        print(f"\nRunning validation for {args.run_name} (conf={args.conf})...\n")

        metrics = model.val(
            data="configs/coco_subset500.yaml",
            imgsz=args.imgsz,
            conf=args.conf,
            iou=args.iou,
            seed=args.seed
        )

        metrics_dict = {
            "map50": float(metrics.box.map50),
            "map50_95": float(metrics.box.map),
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
        }

        with open(os.path.join(val_dir, "metrics.json"), "w") as f:
            json.dump(metrics_dict, f, indent=2)

    # -------------------------
    # 2) Prediction (inference)
    # -------------------------

    if args.attack == "none":
        source = "coco/val2017_subset500/images"
    else:
        source = args.attacks_dir

    print(f"\nRunning inference for {args.run_name} on source: {source}\n")

    model.predict(
        source=source,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        seed=args.seed,
        save=True,
        save_txt=True,
        exist_ok=True
    )

    # Move prediction outputs into structured folder
    predict_path = "runs/detect/predict"

    if os.path.exists(predict_path):
        for file in glob.glob(os.path.join(predict_path, "*")):
            dst = os.path.join(predict_dir, os.path.basename(file))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(file, dst)

        shutil.rmtree(predict_path, ignore_errors=True)

    # -------------------------
    # 3) Metadata + CSV logging
    # -------------------------

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        ).decode().strip()

        branch = subprocess.check_output(
            ["git", "branch", "--show-current"]
        ).decode().strip()

    except Exception:
        commit = "unknown"
        branch = "unknown"

    date = datetime.utcnow().isoformat()

    cmd = (
        f"run_experiment_api.py "
        f"--run_name {args.run_name} "
        f"--attack {args.attack} "
        f"--conf {args.conf} "
        f"--iou {args.iou} "
        f"--imgsz {args.imgsz} "
        f"--seed {args.seed}"
    )

    if args.attack != "none":
        cmd += f" --attacks_dir {args.attacks_dir}"

    subprocess.run([
        "python3", "collect_metrics_api.py",
        "--run_name", args.run_name,
        "--attack", args.attack,
        "--conf", str(args.conf),
        "--iou", str(args.iou),
        "--imgsz", str(args.imgsz),
        "--seed", str(args.seed),
        "--date", date,
        "--commit", commit,
        "--branch", branch,
        "--cmd", cmd
    ])

    print(f"\nExperiment {args.run_name} completed successfully.")
    print(f"Outputs saved to: {run_dir}\n")


if __name__ == "__main__":
    try:
        import ultralytics
    except ImportError:
        print("Error: Ultralytics YOLO not installed. Run: pip install ultralytics")
        exit(1)

    main()