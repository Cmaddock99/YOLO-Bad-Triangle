#!/usr/bin/env python3
"""Validate the supported local environment before running experiments.

Checks the local Python runtime, pinned package versions, Torch runtime health,
YOLO model availability, dataset images, and label pairing. Run this after
setup to confirm the machine matches the supported local configuration before
starting sweeps or closed-loop cycles.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

SUPPORTED_LOCAL_PYTHON = (3, 11)
EXPECTED_ULTRALYTICS_VERSION = "8.4.23"
EXPECTED_TORCH_VERSION = "2.5.1"
EXPECTED_TORCHVISION_VERSION = "0.20.1"
TORCH_RUNTIME_TIMEOUT_SECONDS = 30
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


def _supported_runtime_instruction() -> str:
    return (
        "Use Python 3.11.x with ultralytics==8.4.23, torch==2.5.1, and "
        "torchvision==0.20.1. Rebuild `.venv` with `python3.11 -m venv .venv`, "
        "then reinstall requirements."
    )


def _coerce_version_info(version_info: Any) -> tuple[int, int, int]:
    return (int(version_info[0]), int(version_info[1]), int(version_info[2]))


def check_python_version(version_info: Any | None = None) -> CheckResult:
    current = _coerce_version_info(version_info or sys.version_info)
    ok = current[:2] == SUPPORTED_LOCAL_PYTHON
    detail = (
        f"found {current[0]}.{current[1]}.{current[2]}; supported local runtime is "
        f"{SUPPORTED_LOCAL_PYTHON[0]}.{SUPPORTED_LOCAL_PYTHON[1]}.x"
    )
    return CheckResult(
        "Python 3.11.x supported",
        ok,
        instruction=None if ok else _supported_runtime_instruction(),
        detail=detail,
    )


def _installed_distribution_version(distribution_name: str) -> str | None:
    try:
        return importlib_metadata.version(distribution_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def check_pinned_distribution_version(
    distribution_name: str,
    expected_version: str,
    label: str,
) -> CheckResult:
    installed_version = _installed_distribution_version(distribution_name)
    if installed_version is None:
        return CheckResult(
            label,
            False,
            instruction="Install dependencies with: ./.venv/bin/pip install -r requirements.txt",
            detail=f"package not installed: {distribution_name}",
        )
    if installed_version != expected_version:
        return CheckResult(
            label,
            False,
            instruction=_supported_runtime_instruction(),
            detail=f"found {distribution_name}=={installed_version}; expected {expected_version}",
        )
    return CheckResult(label, True, detail=f"{distribution_name}=={installed_version}")


def run_torch_runtime_probe(
    *,
    executable: str | None = None,
    runner: Any = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    probe_executable = executable or sys.executable
    return runner(
        [
            probe_executable,
            "-c",
            (
                "import torch, torchvision; "
                "print(torch.__version__); "
                "print(torchvision.__version__)"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=TORCH_RUNTIME_TIMEOUT_SECONDS,
        check=False,
    )


def _probe_failure_detail(result: subprocess.CompletedProcess[str]) -> str:
    stderr_lines = [line.strip() for line in (result.stderr or "").splitlines() if line.strip()]
    stdout_lines = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]
    tail = stderr_lines[-1] if stderr_lines else (stdout_lines[-1] if stdout_lines else "no output")
    if result.returncode < 0:
        return f"probe crashed with signal {abs(result.returncode)}: {tail}"
    return f"probe exited {result.returncode}: {tail}"


def check_torch_runtime_health(
    *,
    executable: str | None = None,
    runner: Any = subprocess.run,
) -> CheckResult:
    try:
        result = run_torch_runtime_probe(executable=executable, runner=runner)
    except subprocess.TimeoutExpired:
        return CheckResult(
            "Torch runtime healthy",
            False,
            instruction=_supported_runtime_instruction(),
            detail=(
                "probe timed out while importing torch/torchvision; rebuild `.venv` on "
                "Python 3.11 and reinstall the pinned ML stack."
            ),
        )
    except OSError as exc:
        return CheckResult(
            "Torch runtime healthy",
            False,
            instruction=_supported_runtime_instruction(),
            detail=f"failed to launch runtime probe: {exc}",
        )

    if result.returncode != 0:
        return CheckResult(
            "Torch runtime healthy",
            False,
            instruction=_supported_runtime_instruction(),
            detail=_probe_failure_detail(result),
        )

    versions = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]
    detail = None
    if len(versions) >= 2:
        detail = f"torch={versions[0]}, torchvision={versions[1]}"
    return CheckResult("Torch runtime healthy", True, detail=detail)


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
        check_pinned_distribution_version(
            "ultralytics",
            EXPECTED_ULTRALYTICS_VERSION,
            "Ultralytics version pinned",
        ),
        check_pinned_distribution_version(
            "torch",
            EXPECTED_TORCH_VERSION,
            "Torch package version pinned",
        ),
        check_pinned_distribution_version(
            "torchvision",
            EXPECTED_TORCHVISION_VERSION,
            "TorchVision version pinned",
        ),
        check_torch_runtime_health(),
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
