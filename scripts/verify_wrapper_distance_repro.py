#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
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
    parser = argparse.ArgumentParser(description="Compute identity-distance stats and reproducibility checks.")
    parser.add_argument("--checkpoint", default="/Users/lurch/Downloads/dpc_unet_final_golden.pt")
    parser.add_argument("--source-dir", default="coco/val2017_subset500/images")
    parser.add_argument("--output-dir", default="outputs/wrapper_verification")
    parser.add_argument("--max-images", type=int, default=64)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timestep", type=float, default=50.0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--color-order", default="bgr", choices=["rgb", "bgr"])
    parser.add_argument("--scaling", default="zero_one", choices=["zero_one", "minus_one_one"])
    parser.add_argument("--normalize", action="store_true")
    return parser


def _digest_image(image: np.ndarray) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def main() -> None:
    args = _build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = Path(args.checkpoint).expanduser().resolve()
    source_dir = Path(args.source_dir).expanduser().resolve()

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

    per_image: dict[str, dict[str, Any]] = {}
    for image_path in image_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        hashes: list[str] = []
        l2s: list[float] = []
        maes: list[float] = []
        finite_all = True
        for _ in range(max(1, int(args.repeats))):
            output, stats = run_wrapper_on_bgr_image(
                image,
                model,
                timestep=float(args.timestep),
                cfg=cfg,
                device=args.device,
            )
            finite_all = finite_all and bool(stats["finite"])
            diff = output.astype(np.float32) - image.astype(np.float32)
            l2s.append(float(np.sqrt(np.mean(diff**2))))
            maes.append(float(np.mean(np.abs(diff))))
            hashes.append(_digest_image(output))
        per_image[image_path.name] = {
            "finite_all": finite_all,
            "l2_rmse_mean": float(np.mean(l2s)),
            "l2_rmse_std": float(np.std(l2s)),
            "mae_mean": float(np.mean(maes)),
            "mae_std": float(np.std(maes)),
            "unique_output_hashes": len(set(hashes)),
            "hashes": hashes,
        }

    rows = [{"image": name, **payload} for name, payload in sorted(per_image.items())]
    csv_path = output_dir / "distance_repro_details.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "image",
            "finite_all",
            "l2_rmse_mean",
            "l2_rmse_std",
            "mae_mean",
            "mae_std",
            "unique_output_hashes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})

    all_l2 = [float(row["l2_rmse_mean"]) for row in rows]
    all_hash_counts = [int(row["unique_output_hashes"]) for row in rows]
    summary = {
        "checkpoint": str(checkpoint),
        "source_dir": str(source_dir),
        "images_evaluated": len(rows),
        "repeats": int(args.repeats),
        "timestep": float(args.timestep),
        "config": {
            "color_order": cfg.color_order,
            "scaling": cfg.scaling,
            "normalize": cfg.normalize,
        },
        "all_finite": all(bool(row["finite_all"]) for row in rows),
        "l2_rmse_mean_over_images": float(np.mean(all_l2)) if all_l2 else 0.0,
        "l2_rmse_min_over_images": float(np.min(all_l2)) if all_l2 else 0.0,
        "l2_rmse_max_over_images": float(np.max(all_l2)) if all_l2 else 0.0,
        "reproducible_all_images": all(count == 1 for count in all_hash_counts),
        "max_unique_hashes_for_any_image": max(all_hash_counts) if all_hash_counts else 0,
        "details_csv": str(csv_path),
    }
    summary_path = output_dir / "distance_repro_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote distance/repro details: {csv_path}")
    print(f"Wrote distance/repro summary: {summary_path}")


if __name__ == "__main__":
    main()
