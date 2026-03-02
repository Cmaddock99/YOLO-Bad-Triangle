#!/usr/bin/env python3
import os, glob, csv, json, argparse
from statistics import mean, median

parser = argparse.ArgumentParser()
parser.add_argument('--run_name', required=True)
parser.add_argument('--attack', required=True)
parser.add_argument('--conf', required=True)
parser.add_argument('--iou', required=True)
parser.add_argument('--imgsz', required=True)
parser.add_argument('--seed', required=True)
parser.add_argument('--date', required=True)
parser.add_argument('--commit', required=True)
parser.add_argument('--branch', required=True)
parser.add_argument('--cmd', required=True)
args = parser.parse_args()

run = args.run_name
metrics_path = os.path.join("results", run, "val", "metrics.json")
images_dir = os.path.join("results", run, "predict")
confidences = []
images_with_det = 0
total_dets = 0

# Read detection label files for confidences
if os.path.isdir(images_dir):
    for txt in glob.glob(os.path.join(images_dir, "*.txt")):
        lines = [l.strip().split() for l in open(txt) if l.strip()]
        if lines:
            images_with_det += 1
            total_dets += len(lines)
            for parts in lines:
                try:
                    confidences.append(float(parts[-1]))
                except:
                    pass

# Compute confidence stats
if confidences:
    avg_conf = mean(confidences)
    med_conf = median(confidences)
    sorted_conf = sorted(confidences)
    p25_conf = sorted_conf[max(0, int(0.25*len(sorted_conf))-1)]
    p75_conf = sorted_conf[min(len(sorted_conf)-1, int(0.75*len(sorted_conf))-1)]
else:
    avg_conf = med_conf = p25_conf = p75_conf = ''

# Read validation metrics from JSON if exists
mAP50 = mAP50_95 = ''
prec = recall = ''
if os.path.isfile(metrics_path):
    data = json.load(open(metrics_path))
    mAP50 = data.get("mAP50", '')
    mAP50_95 = data.get("mAP50-95", '')
    prec = data.get("precision", '')
    recall = data.get("recall", '')

# Prepare CSV entry
csv_file = os.path.join("results", "metrics_summary.csv")
headers = ["date","commit","branch","run_name","attack","conf","iou",
           "imgsz","seed","precision","recall","images_with_detections",
           "total_detections","avg_conf","median_conf","p25_conf","p75_conf","mAP50","mAP50-95"]
row = {
    "date": args.date, 
    "commit": args.commit, 
    "branch": args.branch,
    "run_name": run,
    "attack": args.attack,
    "conf": args.conf,
    "iou": args.iou,
    "imgsz": args.imgsz,
    "seed": args.seed,
    "precision": prec,
    "recall": recall,
    "images_with_detections": images_with_det,
    "total_detections": total_dets,
    "avg_conf": avg_conf,
    "median_conf": med_conf,
    "p25_conf": p25_conf,
    "p75_conf": p75_conf,
    "mAP50": mAP50,
    "mAP50-95": mAP50_95
}

# Write/append CSV
write_header = not os.path.isfile(csv_file)
with open(csv_file, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    if write_header:
        writer.writeheader()
    writer.writerow(row)

print(f"Logged metrics for {run} (attack={args.attack})")
