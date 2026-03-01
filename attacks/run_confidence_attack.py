from ultralytics import YOLO
import cv2
import os
import json
import numpy as np

model = YOLO("yolov8n.pt")

input_dir = "coco/val2017_subset500/images"
perturbed_dir = "attack_results/iteration1/perturbed_images"

os.makedirs(perturbed_dir, exist_ok=True)

# Apply simple blur degradation attack
for img_name in os.listdir(input_dir):
    img_path = os.path.join(input_dir, img_name)
    img = cv2.imread(img_path)

    if img is None:
        continue

    perturbed = cv2.GaussianBlur(img, (9, 9), 0)
    cv2.imwrite(os.path.join(perturbed_dir, img_name), perturbed)

# Run inference on perturbed images
results = model.predict(
    source=perturbed_dir,
    conf=0.25,
    iou=0.7,
    save=True,
    save_txt=True,
    save_conf=True,
    project="runs",
    name="attack_iteration1",
    exist_ok=True
)

# Collect metrics
total_detections = 0
for r in results:
    total_detections += len(r.boxes)

metrics = {
    "attack": "GaussianBlur",
    "total_images": len(results),
    "total_detections": total_detections
}

output_dir = "runs/detect/attack_iteration1"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=4)

print("Attack complete.")
print(metrics)