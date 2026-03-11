from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


def _git_metadata() -> tuple[str, str]:
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        )
        branch = (
            subprocess.check_output(
                ["git", "branch", "--show-current"], text=True
            ).strip()
        )
        return commit, branch
    except Exception:
        return "unknown", "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _find_label_files(run_dir: Path) -> list[Path]:
    patterns = [
        "labels/*.txt",
        "predict/labels/*.txt",
        "predict/*.txt",
        "*.txt",
    ]
    found: dict[str, Path] = {}
    for pattern in patterns:
        for file_path in run_dir.glob(pattern):
            if file_path.is_file():
                found[str(file_path)] = file_path
    return sorted(found.values())


def _parse_detection_stats(run_dir: Path) -> dict[str, Any]:
    label_files = _find_label_files(run_dir)
    images_with_detections = 0
    total_detections = 0
    confidences: list[float] = []

    for txt_file in label_files:
        lines = [line.strip().split() for line in txt_file.read_text().splitlines() if line.strip()]
        if lines:
            images_with_detections += 1
            total_detections += len(lines)
            for parts in lines:
                try:
                    confidences.append(float(parts[-1]))
                except Exception:
                    continue

    if confidences:
        sorted_confs = sorted(confidences)
        p25_idx = max(0, int(0.25 * len(sorted_confs)) - 1)
        p75_idx = min(len(sorted_confs) - 1, int(0.75 * len(sorted_confs)) - 1)
        avg_conf = mean(confidences)
        med_conf = median(confidences)
        p25_conf = sorted_confs[p25_idx]
        p75_conf = sorted_confs[p75_idx]
    else:
        avg_conf = med_conf = p25_conf = p75_conf = None

    return {
        "images_with_detections": images_with_detections,
        "total_detections": total_detections,
        "avg_conf": avg_conf,
        "median_conf": med_conf,
        "p25_conf": p25_conf,
        "p75_conf": p75_conf,
    }


def _read_val_metrics(run_dir: Path) -> dict[str, Any]:
    candidates = [
        run_dir / "metrics.json",
        run_dir / "val" / "metrics.json",
    ]
    merged: dict[str, Any] = {}
    for candidate in candidates:
        merged.update(_read_json(candidate))

    return {
        "precision": merged.get("precision", merged.get("mp")),
        "recall": merged.get("recall", merged.get("mr")),
        "mAP50": merged.get("mAP50", merged.get("map50")),
        "mAP50-95": merged.get("mAP50-95", merged.get("map50_95", merged.get("map"))),
    }


def append_run_metrics(
    *,
    run_dir: Path,
    csv_path: Path,
    run_name: str,
    model: str = "yolo8",
    attack: str,
    defense: str,
    conf: float,
    iou: float,
    imgsz: int,
    seed: int,
) -> dict[str, Any]:
    commit, branch = _git_metadata()
    detection_stats = _parse_detection_stats(run_dir)
    val_metrics = _read_val_metrics(run_dir)

    row = {
        "date": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "branch": branch,
        "run_name": run_name,
        "MODEL": model,
        "attack": attack,
        "defense": defense,
        "conf": conf,
        "iou": iou,
        "imgsz": imgsz,
        "seed": seed,
        **detection_stats,
        **val_metrics,
    }

    default_fieldnames = [
        "date",
        "commit",
        "branch",
        "run_name",
        "MODEL",
        "attack",
        "defense",
        "conf",
        "iou",
        "imgsz",
        "seed",
        "images_with_detections",
        "total_detections",
        "avg_conf",
        "median_conf",
        "p25_conf",
        "p75_conf",
        "precision",
        "recall",
        "mAP50",
        "mAP50-95",
    ]

    fieldnames = default_fieldnames
    if csv_path.is_file():
        with csv_path.open(newline="") as csv_file:
            reader = csv.reader(csv_file)
            first_row = next(reader, None)
            if first_row:
                fieldnames = first_row

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not csv_path.is_file()
    with csv_path.open("a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({name: row.get(name, "") for name in fieldnames})
    return row

