#!/usr/bin/env python3
import os, glob, json, csv, argparse, subprocess
from datetime import datetime
from statistics import mean, median
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

parser = argparse.ArgumentParser()
parser.add_argument('--run_name', required=True, help='Run folder name (under results/)')
parser.add_argument('--attack', required=True, help='Attack name (or "none")')
parser.add_argument('--conf', required=True, help='Confidence threshold (as string)')
parser.add_argument('--iou', required=True, help='IOU threshold (as string)')
parser.add_argument('--imgsz', required=True)
parser.add_argument('--seed', required=True)
args = parser.parse_args()

run_name = args.run_name
attack = args.attack
conf = args.conf
iou = args.iou
imgsz = args.imgsz
seed = args.seed
results_dir = os.path.join("results", run_name)
labels_dir = os.path.join(results_dir, "labels")

# Initialize metrics
images_with_detections = 0
total_detections = 0
confidences = []

# Parse label files if they exist
if os.path.isdir(labels_dir):
    for txt_file in glob.glob(os.path.join(labels_dir, "*.txt")):
        with open(txt_file) as f:
            lines = [line.strip().split() for line in f if line.strip()]
        if lines:
            images_with_detections += 1
            total_detections += len(lines)
            for parts in lines:
                # YOLO labels: [class, x, y, w, h, conf]
                try:
                    confidences.append(float(parts[-1]))
                except:
                    pass

# Compute confidence statistics
if confidences:
    avg_conf = mean(confidences)
    med_conf = median(confidences)
    sorted_confs = sorted(confidences)
    p25_conf = sorted_confs[max(0, int(0.25*len(sorted_confs))-1)]
    p75_conf = sorted_confs[min(len(sorted_confs)-1, int(0.75*len(sorted_confs))-1)]
else:
    avg_conf = med_conf = p25_conf = p75_conf = None

# Attempt to read YOLO val metrics JSON
map50 = None
map50_95 = None
metrics_json = os.path.join(results_dir, "metrics.json")
if os.path.isfile(metrics_json):
    try:
        data = json.load(open(metrics_json))
        map50 = data.get("mAP50", None)
        map50_95 = data.get("mAP50-95", None)
    except:
        pass

# Git metadata
commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
date = datetime.utcnow().isoformat()

# CSV file path
csv_file = os.path.join("results", "metrics_summary.csv")
fieldnames = ["date","commit","branch","run_name","attack","conf","iou","imgsz","seed",
              "images_with_detections","total_detections","avg_conf",
              "median_conf","p25_conf","p75_conf","mAP50","mAP50-95"]

# Write header if needed
if not os.path.isfile(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

# Append this run's metrics
with open(csv_file, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow({
        "date": date,
        "commit": commit,
        "branch": branch,
        "run_name": run_name,
        "attack": attack,
        "conf": conf,
        "iou": args.iou,
        "imgsz": args.imgsz,
        "seed": args.seed,
        "images_with_detections": images_with_detections,
        "total_detections": total_detections,
        "avg_conf": avg_conf,
        "median_conf": med_conf,
        "p25_conf": p25_conf,
        "p75_conf": p75_conf,
        "mAP50": map50,
        "mAP50-95": map50_95
    })

print(f"Metrics for run '{run_name}' appended to {csv_file}")
