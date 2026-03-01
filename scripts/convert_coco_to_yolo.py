#!/usr/bin/env python3
import os
import json

DATASET_DIR = "coco/val2017_subset500"
JSON_PATH = os.path.join(DATASET_DIR, "instances_val2017_subset500.json")
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
LABELS_DIR = os.path.join(DATASET_DIR, "labels")

os.makedirs(LABELS_DIR, exist_ok=True)

with open(JSON_PATH) as f:
    coco = json.load(f)

images = {img["id"]: img for img in coco["images"]}

categories = coco["categories"]
cat_id_map = {cat["id"]: i for i, cat in enumerate(categories)}

for ann in coco["annotations"]:
    image_id = ann["image_id"]
    bbox = ann["bbox"]
    category_id = ann["category_id"]

    image_info = images[image_id]
    img_width = image_info["width"]
    img_height = image_info["height"]

    x_min, y_min, width, height = bbox

    x_center = (x_min + width / 2) / img_width
    y_center = (y_min + height / 2) / img_height
    width /= img_width
    height /= img_height

    yolo_class = cat_id_map[category_id]

    label_path = os.path.join(
        LABELS_DIR,
        os.path.splitext(image_info["file_name"])[0] + ".txt"
    )

    with open(label_path, "a") as f:
        f.write(f"{yolo_class} {x_center} {y_center} {width} {height}\n")

print("Conversion complete.")