# 0) repo root
cd ~/path/to/YOLO-Bad-Triangle

# 1) Download model weights (puts .pt files in repo root)
./.venv/bin/python - <<'PY'
from ultralytics import YOLO
for w in ("yolov8n.pt", "yolo11n.pt", "yolo11s.pt"):
    YOLO(w)  # triggers download if missing
    print("ready:", w)
PY

# 2) Download COCO val2017 images + annotations
mkdir -p coco/_downloads
cd coco/_downloads
curl -L -o val2017.zip http://images.cocodataset.org/zips/val2017.zip
curl -L -o annotations_trainval2017.zip http://images.cocodataset.org/annotations/annotations_trainval2017.zip
unzip -q -n val2017.zip
unzip -q -n annotations_trainval2017.zip
cd ../..

# 3) Build expected subset folder: coco/val2017_subset500
#    (deterministic first 500 images by filename + filtered annotations json)
./.venv/bin/python - <<'PY'
import json, shutil
from pathlib import Path

root = Path(".")
src_images = root / "coco" / "_downloads" / "val2017"
src_ann = root / "coco" / "_downloads" / "annotations" / "instances_val2017.json"

dst = root / "coco" / "val2017_subset500"
(dst / "images").mkdir(parents=True, exist_ok=True)

data = json.loads(src_ann.read_text())
images = sorted(data["images"], key=lambda x: x["file_name"])[:500]
image_ids = {img["id"] for img in images}
annotations = [a for a in data["annotations"] if a["image_id"] in image_ids]

subset = {
    "info": data.get("info", {}),
    "licenses": data.get("licenses", []),
    "images": images,
    "annotations": annotations,
    "categories": data["categories"],
}
(dst / "instances_val2017_subset500.json").write_text(json.dumps(subset))

for img in images:
    shutil.copy2(src_images / img["file_name"], dst / "images" / img["file_name"])

print(f"subset ready: {len(images)} images, {len(annotations)} annotations")
PY

# 4) Generate YOLO label txt files expected by this repo
./.venv/bin/python scripts/convert_coco_to_yolo.py

# 5) Final verification
./.venv/bin/python scripts/check_environment.py

