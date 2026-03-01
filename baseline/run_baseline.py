from ultralytics import YOLO
import json
import os

# Load model
model = YOLO("yolov8n.pt")

# Run baseline inference
results = model.predict(
    source="coco/val2017_subset500/images",
    conf=0.25,
    iou=0.7,
    save=True,
    save_txt=True,
    save_conf=True,
    project="baseline_results",
    name="iteration1",
    exist_ok=True
)

# Collect metrics
total_detections = 0
for r in results:
    total_detections += len(r.boxes)

metrics = {
    "model": "yolov8n.pt",
    "conf_threshold": 0.25,
    "iou_threshold": 0.7,
    "total_images": len(results),
    "total_detections": total_detections
}

os.makedirs("baseline_results/iteration1", exist_ok=True)

with open("baseline_results/iteration1/metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("Baseline complete.")
print(metrics)