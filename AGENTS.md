# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Python ML research project benchmarking adversarial attacks (Gaussian blur) against YOLOv8 object detection on a 500-image COCO val2017 subset. No web server, no database, no Docker — all CLI-based scripts outputting JSON/CSV results.

### Virtual environment

The project uses a Python venv at `.venv/`. Activate it before running any command:

```
source .venv/bin/activate
```

### Dataset setup (one-time)

The COCO images and YOLO labels are gitignored. If the `coco/val2017_subset500/images/` directory is empty or missing, download images from URLs in the annotation JSON and convert labels:

```python
# Download images (uses coco_url field from instances_val2017_subset500.json)
python3 -c "
import json, os, urllib.request, concurrent.futures
with open('coco/val2017_subset500/instances_val2017_subset500.json') as f:
    data = json.load(f)
os.makedirs('coco/val2017_subset500/images', exist_ok=True)
def dl(img):
    p = f'coco/val2017_subset500/images/{img[\"file_name\"]}'
    if not os.path.exists(p): urllib.request.urlretrieve(img['coco_url'], p)
with concurrent.futures.ThreadPoolExecutor(20) as ex:
    list(ex.map(dl, data['images']))
print('Done')
"

# Convert annotations to YOLO format
python3 scripts/convert_coco_to_yolo.py
```

### Running experiments

Primary experiment runner (runs YOLOv8 val + predict, then collects metrics):

```
python3 run_experiment_api.py --run_name baseline_conf025 --attack none --conf 0.25 --imgsz 640 --seed 0
```

Results go to `results/<run_name>/` (JSON metrics + CSV summary).

### Key caveats

- No linter, formatter, or test framework is configured. Code quality checks are limited to `python3 -m py_compile <file>`.
- The YOLOv8n model weights (`yolov8n.pt`) are auto-downloaded by Ultralytics on first use; no manual download needed.
- All inference runs on **CPU** in this environment (no GPU). A full 500-image experiment takes ~40 seconds.
- The `scripts/blur_experiment.sh` shell script has a syntax error on line 6 (`DATA_YAML="DATA_YAML=...`); use `run_experiment_api.py` or `scripts/run_experiment.py` instead.
- System dependency `libgl1` is needed for `opencv-python` on headless Linux (installed via `apt`).
