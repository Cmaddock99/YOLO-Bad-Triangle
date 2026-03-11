from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.attacks.blur import GaussianBlurAttack
from lab.models import YOLOModel


def main() -> None:
    source_dir = ROOT / "coco" / "val2017_subset500" / "images"
    temp_root = ROOT / "outputs" / "_kernel_sweep"
    if temp_root.exists():
        shutil.rmtree(temp_root)

    model = YOLOModel("yolo11n.pt")
    for kernel in [3, 7, 11, 15, 21, 31]:
        attack = GaussianBlurAttack(kernel_size=kernel)
        attacked = attack.apply(source_dir, temp_root / f"blur_k{kernel}")
        image_candidates = sorted(attacked.glob("*.jpg"))
        if not image_candidates:
            continue

        print(f"\n=== Kernel Size: {kernel} ===")
        results = model.predict(source=str(image_candidates[0]))
        for result in results:
            for box in result.boxes:
                print(f"Class: {int(box.cls)} | Confidence: {float(box.conf):.4f}")


if __name__ == "__main__":
    main()