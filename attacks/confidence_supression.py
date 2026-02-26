import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

img = cv2.imread("bus.jpg")

for kernel in [3, 7, 11, 15, 21, 31]:
    blurred = cv2.GaussianBlur(img, (kernel, kernel), 0)
    temp_path = f"blur_{kernel}.jpg"
    cv2.imwrite(temp_path, blurred)

    print(f"\n=== Kernel Size: {kernel} ===")

    results = model(temp_path)

    for r in results:
        for box in r.boxes:
            print(f"Class: {int(box.cls)} | Confidence: {float(box.conf):.4f}")