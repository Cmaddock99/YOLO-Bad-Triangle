#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from lab.attacks.utils import iter_images
from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    load_checkpoint_state_dict,
    run_wrapper_on_bgr_image,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep input conventions for DPC-UNet wrapper.")
    parser.add_argument("--checkpoint", default="/Users/lurch/Downloads/dpc_unet_final_golden.pt")
    parser.add_argument("--source-dir", default="coco/val2017_subset500/images")
    parser.add_argument("--output-dir", default="outputs/wrapper_verification")
    parser.add_argument("--max-images", type=int, default=24)
    parser.add_argument("--timestep", type=float, default=100.0)
    parser.add_argument("--device", default="cpu")
    return parser


def _distortion_stats(src: np.ndarray, out: np.ndarray) -> dict[str, float]:
    src_f = src.astype(np.float32)
    out_f = out.astype(np.float32)
    diff = out_f - src_f
    mse = float(np.mean(diff**2))
    mae = float(np.mean(np.abs(diff)))
    l2 = float(np.sqrt(np.mean(diff**2)))
    sat = float(np.mean((out <= 1) | (out >= 254)))
    return {
        "mse": mse,
        "mae": mae,
        "l2_rmse": l2,
        "saturation_ratio": sat,
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    keys = ("tensor_min", "tensor_max", "tensor_mean", "tensor_std", "mse", "mae", "l2_rmse", "saturation_ratio")
    out: dict[str, Any] = {
        "images": len(rows),
        "all_finite": all(bool(row["finite"]) for row in rows),
        "all_shapes_preserved": all(bool(row["shape_preserved"]) for row in rows),
        "extreme_artifacts": sum(1 for row in rows if bool(row["artifact_extreme"])),
    }
    for key in keys:
        values = [float(row[key]) for row in rows]
        out[f"{key}_mean"] = float(np.mean(values))
        out[f"{key}_min"] = float(np.min(values))
        out[f"{key}_max"] = float(np.max(values))
    return out


def main() -> None:
    args = _build_parser().parse_args()
    checkpoint = Path(args.checkpoint).expanduser().resolve()
    source_dir = Path(args.source_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not checkpoint.exists():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint}")
    if not source_dir.exists():
        raise FileNotFoundError(f"source dir not found: {source_dir}")

    model = DPCUNet()
    model.load_state_dict(load_checkpoint_state_dict(checkpoint), strict=True)
    model.eval()

    image_paths = sorted(iter_images(source_dir))
    if args.max_images > 0:
        image_paths = image_paths[: args.max_images]
    if not image_paths:
        raise ValueError(f"no images found in source dir: {source_dir}")

    combos: list[WrapperInputConfig] = []
    for color in ("rgb", "bgr"):
        for scaling in ("zero_one", "minus_one_one"):
            for normalize in (False, True):
                combos.append(WrapperInputConfig(color_order=color, scaling=scaling, normalize=normalize))

    detail_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for cfg in combos:
        combo_name = f"color={cfg.color_order}|scaling={cfg.scaling}|normalize={int(cfg.normalize)}"
        combo_rows: list[dict[str, Any]] = []
        for image_path in image_paths:
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            output, stats = run_wrapper_on_bgr_image(
                image,
                model,
                timestep=args.timestep,
                cfg=cfg,
                device=args.device,
            )
            shape_preserved = image.shape == output.shape
            dstats = _distortion_stats(image, output)
            artifact_extreme = bool((not bool(stats["finite"])) or (dstats["saturation_ratio"] > 0.95))
            row = {
                "combo": combo_name,
                "image": image_path.name,
                "finite": bool(stats["finite"]),
                "shape_preserved": shape_preserved,
                "artifact_extreme": artifact_extreme,
                **stats,
                **dstats,
            }
            detail_rows.append(row)
            combo_rows.append(row)
        summary_rows.append({"combo": combo_name, **_aggregate(combo_rows)})

    detail_csv = output_dir / "input_sweep_details.csv"
    summary_json = output_dir / "input_sweep_summary.json"
    with detail_csv.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(detail_rows[0].keys()) if detail_rows else ["combo", "image"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)
    summary_json.write_text(
        json.dumps(
            {
                "checkpoint": str(checkpoint),
                "source_dir": str(source_dir),
                "images_evaluated": len(image_paths),
                "timestep": args.timestep,
                "combinations": summary_rows,
                "detail_csv": str(detail_csv),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"Wrote detail CSV: {detail_csv}")
    print(f"Wrote summary JSON: {summary_json}")


if __name__ == "__main__":
    main()
