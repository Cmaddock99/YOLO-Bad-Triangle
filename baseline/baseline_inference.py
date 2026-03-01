from ultralytics import YOLO

model = YOLO("./yolov8n.pt")

results = model("bus.jpg")

for r in results:
    for box in r.boxes:
        print(f"Class: {int(box.cls)} | Confidence: {float(box.conf):.4f}")
    