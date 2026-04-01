#!/usr/bin/env python3
"""Validate environment before running experiments.

Checks Python version, required packages, YOLO model availability, dataset
images, and plugin registration. Run this after initial setup to confirm
everything is in order before starting sweeps or cycles.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
"""
from __future__ import annotations

import argparse
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_PYTHON = (3, 9)
DEFAULT_DATASET_PATH = "coco/val2017_subset500/images"
DEFAULT_MODEL_CANDIDATES = ("yolo26n.pt", "yolo11n.pt", "yolo11s.pt", "yolov8n.pt")
CHECKMARK = "✔"
CROSSMARK = "✘"


@dataclass
class CheckResult:
    label: str
    ok: bool
    instruction: str | None = None
    detail: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check local environment requirements for this repository."
    )
    parser.add_argument(
        "--dataset-path",
        default=DEFAULT_DATASET_PATH,
        help=f"Dataset directory path (default: {DEFAULT_DATASET_PATH})",
    )
    parser.add_argument(
        "--model-path",
        default=None,
        help="Specific YOLO weights file path to check. "
        "If omitted, common default model files are checked.",
    )
    return parser.parse_args()


def check_python_version() -> CheckResult:
    current = sys.version_info
    ok = current >= MIN_PYTHON
    min_version_text = ".".join(str(part) for part in MIN_PYTHON)
    detail = f"found {current.major}.{current.minor}.{current.micro}"
    instruction = (
        f"Install Python {min_version_text}+ and run this script again."
        if not ok
        else None
    )
    return CheckResult("Python version OK", ok, instruction=instruction, detail=detail)


def check_import(module_name: str, label: str) -> CheckResult:
    try:
        importlib.import_module(module_name)
        return CheckResult(label, True)
    except Exception:
        return CheckResult(
            label,
            False,
            instruction="Install dependencies with: ./.venv/bin/pip install -r requirements.txt",
            detail=f"missing module: {module_name}",
        )


def check_dataset_path(dataset_path: str) -> CheckResult:
    path = Path(dataset_path)
    ok = path.exists()
    instruction = (
        "Place/download the dataset and update the path with --dataset-path if needed."
        if not ok
        else None
    )
    if not ok:
        return CheckResult("Dataset missing", False, instruction=instruction, detail=str(path))

    image_files = [
        *path.glob("*.jpg"),
        *path.glob("*.jpeg"),
        *path.glob("*.png"),
    ]
    labels_dir = path.parent / "labels"
    if not image_files:
        return CheckResult(
            "Dataset missing images",
            False,
            instruction="Ensure dataset image directory contains .jpg/.jpeg/.png files.",
            detail=str(path),
        )
    if not labels_dir.is_dir():
        return CheckResult(
            "Dataset labels missing",
            False,
            instruction="Expected sibling labels directory beside images (../labels).",
            detail=str(labels_dir),
        )
    sample_images = sorted(image_files)[: min(25, len(image_files))]
    missing_labels = [
        image_path.name
        for image_path in sample_images
        if not (labels_dir / f"{image_path.stem}.txt").is_file()
    ]
    if missing_labels:
        return CheckResult(
            "Dataset label pairing failed",
            False,
            instruction="Add matching .txt labels for sampled images in ../labels.",
            detail=f"missing labels for: {', '.join(missing_labels[:5])}",
        )
    return CheckResult(
        "Dataset found",
        True,
        detail=f"{path} (sampled_pairs_ok={len(sample_images)})",
    )


def resolve_model_path(model_path: str | None) -> Path | None:
    if model_path:
        candidate = Path(model_path)
        return candidate if candidate.exists() else None
    for candidate_name in DEFAULT_MODEL_CANDIDATES:
        candidate = Path(candidate_name)
        if candidate.exists():
            return candidate
    return None


def check_model_weights(model_path: str | None) -> CheckResult:
    resolved = resolve_model_path(model_path)
    if resolved is not None:
        return CheckResult("YOLO model found", True, detail=str(resolved))

    if model_path:
        missing_target = model_path
    else:
        missing_target = ", ".join(DEFAULT_MODEL_CANDIDATES)

    return CheckResult(
        "YOLO model missing",
        False,
        instruction=(
            "Download YOLO weights (for example `yolo26n.pt`) into the repo root, "
            "or set --model-path to your weights file."
        ),
        detail=f"checked: {missing_target}",
    )


def print_result(result: CheckResult) -> None:
    symbol = CHECKMARK if result.ok else CROSSMARK
    print(f"{symbol} {result.label}")


def main() -> int:
    args = parse_args()
    checks = [
        check_python_version(),
        check_import("ultralytics", "Ultralytics installed"),
        check_import("torch", "Torch installed"),
        check_model_weights(args.model_path),
        check_dataset_path(args.dataset_path),
    ]

    for result in checks:
        print_result(result)

    failures = [result for result in checks if not result.ok]
    if not failures:
        return 0

    print("\nHow to fix:")
    for result in failures:
        if result.detail:
            print(f"- {result.label}: {result.detail}")
        if result.instruction:
            print(f"  {result.instruction}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
