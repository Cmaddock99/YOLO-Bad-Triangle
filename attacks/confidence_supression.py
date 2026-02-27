import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

img = cv2.imread("bus.jpg")

for kernel in [3, 7, 11, 15, 21, 31]:
    blurred = cv2.GaussianBlur(img, (kernel, kernel), 0)

    print(f"\n=== Kernel Size: {kernel} ===")

    results = model(blurred)

    for r in results:
        for box in r.boxes:
            print(f"Class: {int(box.cls)} | Confidence: {float(box.conf):.4f}")