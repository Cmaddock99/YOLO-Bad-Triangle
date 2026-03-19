#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from lab.attacks.utils import iter_images
from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    load_checkpoint_state_dict,
    run_wrapper_on_bgr_image,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe timestep stability for DPC-UNet wrapper.")
    parser.add_argument("--checkpoint", default="/Users/lurch/Downloads/dpc_unet_final_golden.pt")
    parser.add_argument("--source-dir", default="coco/val2017_subset500/images")
    parser.add_argument("--output-dir", default="outputs/wrapper_verification")
    parser.add_argument("--max-images", type=int, default=16)
    parser.add_argument("--timesteps", default="0,10,50,100,250,500,750,999")
    parser.add_argument("--include-normalized", action="store_true", help="Also probe timestep/999 values.")
    parser.add_argument("--model", default="yolo26n.pt", help="Detector model for confidence behavior checks.")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.7)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--color-order", default="bgr", choices=["rgb", "bgr"])
    parser.add_argument("--scaling", default="zero_one", choices=["zero_one", "minus_one_one"])
    parser.add_argument("--normalize", action="store_true")
    return parser


def _parse_timestep_values(raw: str, include_normalized: bool) -> list[float]:
    base = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if include_normalized:
        return base + [value / 999.0 for value in base]
    return base


def _detector_confidence_stats(
    model: YOLO, image_paths: list[Path], *, conf: float, iou: float, imgsz: int
) -> dict[str, float | int]:
    results = model.predict(source=str(image_paths[0].parent), conf=conf, iou=iou, imgsz=imgsz, save=False)
    confs: list[float] = []
    total_detections = 0
    for result in results:
        boxes = getattr(result, "boxes", None)
        if boxes is None or boxes.conf is None:
            continue
        row = boxes.conf.detach().cpu().numpy().astype(float).tolist()
        confs.extend(row)
        total_detections += len(row)
    if not confs:
        return {
            "det_total_detections": 0,
            "det_mean_conf": 0.0,
            "det_median_conf": 0.0,
        }
    return {
        "det_total_detections": int(total_detections),
        "det_mean_conf": float(np.mean(confs)),
        "det_median_conf": float(np.median(confs)),
    }


def main() -> None:
    args = _build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = Path(args.source_dir).expanduser().resolve()
    checkpoint = Path(args.checkpoint).expanduser().resolve()

    image_paths = sorted(iter_images(source_dir))
    if args.max_images > 0:
        image_paths = image_paths[: args.max_images]
    if not image_paths:
        raise ValueError(f"No images found in source dir: {source_dir}")

    cfg = WrapperInputConfig(
        color_order=args.color_order,
        scaling=args.scaling,
        normalize=bool(args.normalize),
    )

    model = DPCUNet()
    model.load_state_dict(load_checkpoint_state_dict(checkpoint), strict=True)
    model.eval()

    detector = YOLO(args.model)
    rows: list[dict[str, Any]] = []
    for timestep in _parse_timestep_values(args.timesteps, include_normalized=bool(args.include_normalized)):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            finite_ok = True
            shape_ok = True
            l2_values: list[float] = []
            tensor_stds: list[float] = []
            for image_path in image_paths:
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                out, stats = run_wrapper_on_bgr_image(
                    image,
                    model,
                    timestep=timestep,
                    cfg=cfg,
                    device=args.device,
                )
                finite_ok = finite_ok and bool(stats["finite"])
                shape_ok = shape_ok and (out.shape == image.shape)
                diff = out.astype(np.float32) - image.astype(np.float32)
                l2_values.append(float(np.sqrt(np.mean(diff**2))))
                tensor_stds.append(float(stats["tensor_std"]))
                cv2.imwrite(str(tmp_dir / image_path.name), out)

            generated_paths = sorted(iter_images(tmp_dir))
            det_stats = _detector_confidence_stats(
                detector,
                generated_paths,
                conf=float(args.conf),
                iou=float(args.iou),
                imgsz=int(args.imgsz),
            )
            rows.append(
                {
                    "timestep": float(timestep),
                    "finite_ok": finite_ok,
                    "shape_ok": shape_ok,
                    "l2_rmse_mean": float(np.mean(l2_values)) if l2_values else 0.0,
                    "l2_rmse_max": float(np.max(l2_values)) if l2_values else 0.0,
                    "tensor_std_mean": float(np.mean(tensor_stds)) if tensor_stds else 0.0,
                    **det_stats,
                }
            )

    rows.sort(key=lambda row: row["timestep"])
    csv_path = output_dir / "timestep_probe.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["timestep"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    stable_rows = [
        row
        for row in rows
        if bool(row["finite_ok"]) and bool(row["shape_ok"]) and float(row["l2_rmse_mean"]) > 5.0
    ]
    stable_rows.sort(key=lambda row: (-float(row["det_mean_conf"]), float(row["l2_rmse_mean"])))

    summary = {
        "checkpoint": str(checkpoint),
        "source_dir": str(source_dir),
        "images_evaluated": len(image_paths),
        "config": {
            "color_order": cfg.color_order,
            "scaling": cfg.scaling,
            "normalize": cfg.normalize,
        },
        "stable_candidates_ranked": stable_rows[:5],
        "rows": rows,
        "csv": str(csv_path),
    }
    summary_path = output_dir / "timestep_probe_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote timestep probe CSV: {csv_path}")
    print(f"Wrote timestep probe summary: {summary_path}")


if __name__ == "__main__":
    main()
