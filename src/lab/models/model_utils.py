from __future__ import annotations

from pathlib import Path


DEFAULT_YOLO_MODEL = "yolo26n.pt"


def normalize_model_path(model: str | None) -> str:
    value = str(model).strip() if model is not None else ""
    if not value:
        return DEFAULT_YOLO_MODEL
    if value.lower().endswith(".pt"):
        return value
    return f"{value}.pt"


def model_label_from_path(model_path: str) -> str:
    stem = Path(model_path).stem.lower()
    if stem.startswith("yolov8"):
        return "yolo8"
    if stem.startswith("yolo11"):
        return "yolo11"
    return stem
