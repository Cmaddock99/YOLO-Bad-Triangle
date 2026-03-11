from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.models import YOLOModel


def main() -> None:
    model = YOLOModel("yolo11n.pt")
    results = model.predict(source="bus.jpg")
    for result in results:
        for box in result.boxes:
            print(f"Class: {int(box.cls)} | Confidence: {float(box.conf):.4f}")


if __name__ == "__main__":
    main()
    