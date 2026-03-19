#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import inspect
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from lab.attacks import build_attack
from lab.attacks.utils import iter_images
from lab.defenses.dpc_unet_wrapper import (
    DPCUNet,
    WrapperInputConfig,
    load_checkpoint_state_dict,
    run_wrapper_on_bgr_image,
)
from lab.models import YOLOModel


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run downstream mini matrix for wrapper defense candidate.")
    parser.add_argument("--checkpoint", default="/Users/lurch/Downloads/dpc_unet_final_golden.pt")
    parser.add_argument("--source-dir", default="coco/val2017_subset500/images")
    parser.add_argument("--output-dir", default="outputs/wrapper_verification")
    parser.add_argument("--max-images", type=int, default=16)
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.7)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--timestep", type=float, default=50.0)
    parser.add_argument("--color-order", default="bgr", choices=["rgb", "bgr"])
    parser.add_argument("--scaling", default="zero_one", choices=["zero_one", "minus_one_one"])
    parser.add_argument("--normalize", action="store_true")
    return parser


def _copy_subset(source_dir: Path, target_dir: Path, *, max_images: int) -> list[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for idx, image_path in enumerate(sorted(iter_images(source_dir))):
        if max_images > 0 and idx >= max_images:
            break
        relative = image_path.relative_to(source_dir)
        out = target_dir / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        cv2.imwrite(str(out), image)
        copied.append(out)
    if not copied:
        raise ValueError(f"No readable images copied from {source_dir}")
    return copied


def _apply_wrapper_dir(
    source_dir: Path,
    target_dir: Path,
    model: DPCUNet,
    *,
    cfg: WrapperInputConfig,
    timestep: float,
    device: str,
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for image_path in sorted(iter_images(source_dir)):
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        output, stats = run_wrapper_on_bgr_image(
            image,
            model,
            timestep=timestep,
            cfg=cfg,
            device=device,
        )
        if not bool(stats["finite"]):
            raise RuntimeError(f"Non-finite wrapper output for image: {image_path}")
        relative = image_path.relative_to(source_dir)
        out_file = target_dir / relative
        out_file.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_file), output)


def _detector_stats(model: YOLO, source_dir: Path, *, conf: float, iou: float, imgsz: int) -> dict[str, float]:
    results = model.predict(source=str(source_dir), conf=conf, iou=iou, imgsz=imgsz, save=False)
    confs: list[float] = []
    images_with_detections = 0
    for result in results:
        boxes = getattr(result, "boxes", None)
        if boxes is None or boxes.conf is None:
            continue
        vals = boxes.conf.detach().cpu().numpy().astype(float).tolist()
        if vals:
            images_with_detections += 1
            confs.extend(vals)
    total_detections = len(confs)
    return {
        "images_with_detections": float(images_with_detections),
        "total_detections": float(total_detections),
        "mean_conf": float(np.mean(confs)) if confs else 0.0,
        "median_conf": float(np.median(confs)) if confs else 0.0,
    }


def _apply_attack(attack_name: str, params: dict[str, Any], source: Path, target: Path, *, model: YOLOModel) -> None:
    attack = build_attack(attack_name, params)
    signature = inspect.signature(attack.apply)
    kwargs: dict[str, Any] = {"seed": 42}
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()
    )
    if "model" in signature.parameters or accepts_var_kwargs:
        kwargs["model"] = model
    attack.apply(source, target, **kwargs)


def main() -> None:
    args = _build_parser().parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    matrix_root = output_dir / "downstream_matrix"
    matrix_root.mkdir(parents=True, exist_ok=True)

    clean_source = matrix_root / "clean_source_subset"
    _copy_subset(source_dir, clean_source, max_images=int(args.max_images))

    wrapper_model = DPCUNet()
    wrapper_model.load_state_dict(load_checkpoint_state_dict(Path(args.checkpoint).expanduser().resolve()), strict=True)
    cfg = WrapperInputConfig(
        color_order=args.color_order,
        scaling=args.scaling,
        normalize=bool(args.normalize),
    )

    detector = YOLO(args.model)
    gradient_model = YOLOModel(args.model)

    clean_defended = matrix_root / "clean_defended"
    _apply_wrapper_dir(
        clean_source,
        clean_defended,
        wrapper_model,
        cfg=cfg,
        timestep=float(args.timestep),
        device=args.device,
    )

    attack_specs: list[tuple[str, dict[str, Any]]] = [
        ("fgsm", {"epsilon": 0.005}),
        ("pgd", {"epsilon": 0.01, "alpha": 0.002, "steps": 2, "random_start": False, "restarts": 1}),
        ("deepfool", {"epsilon": 0.4, "steps": 2}),
    ]

    rows: list[dict[str, Any]] = []
    clean_stats = _detector_stats(
        detector,
        clean_source,
        conf=float(args.conf),
        iou=float(args.iou),
        imgsz=int(args.imgsz),
    )
    clean_def_stats = _detector_stats(
        detector,
        clean_defended,
        conf=float(args.conf),
        iou=float(args.iou),
        imgsz=int(args.imgsz),
    )
    rows.append(
        {
            "scenario": "clean",
            "attack": "none",
            "mean_conf_no_defense": clean_stats["mean_conf"],
            "mean_conf_with_wrapper": clean_def_stats["mean_conf"],
            "confidence_delta": clean_def_stats["mean_conf"] - clean_stats["mean_conf"],
            "detections_delta": clean_def_stats["total_detections"] - clean_stats["total_detections"],
        }
    )

    for attack_name, params in attack_specs:
        attacked_dir = matrix_root / f"{attack_name}_attacked"
        defended_dir = matrix_root / f"{attack_name}_attacked_then_wrapped"
        _apply_attack(attack_name, params, clean_source, attacked_dir, model=gradient_model)
        _apply_wrapper_dir(
            attacked_dir,
            defended_dir,
            wrapper_model,
            cfg=cfg,
            timestep=float(args.timestep),
            device=args.device,
        )
        attacked_stats = _detector_stats(
            detector,
            attacked_dir,
            conf=float(args.conf),
            iou=float(args.iou),
            imgsz=int(args.imgsz),
        )
        defended_stats = _detector_stats(
            detector,
            defended_dir,
            conf=float(args.conf),
            iou=float(args.iou),
            imgsz=int(args.imgsz),
        )
        rows.append(
            {
                "scenario": attack_name,
                "attack": attack_name,
                "mean_conf_no_defense": attacked_stats["mean_conf"],
                "mean_conf_with_wrapper": defended_stats["mean_conf"],
                "confidence_delta": defended_stats["mean_conf"] - attacked_stats["mean_conf"],
                "detections_delta": defended_stats["total_detections"] - attacked_stats["total_detections"],
                "attacked_images_with_detections": attacked_stats["images_with_detections"],
                "defended_images_with_detections": defended_stats["images_with_detections"],
            }
        )

    csv_path = matrix_root / "downstream_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    clean_row = next(row for row in rows if row["scenario"] == "clean")
    attack_rows = [row for row in rows if row["scenario"] != "clean"]
    summary = {
        "checkpoint": str(Path(args.checkpoint).expanduser().resolve()),
        "source_subset": str(clean_source),
        "images": int(args.max_images),
        "wrapper_config": {
            "color_order": cfg.color_order,
            "scaling": cfg.scaling,
            "normalize": cfg.normalize,
            "timestep": float(args.timestep),
        },
        "clean_confidence_delta": float(clean_row["confidence_delta"]),
        "clean_detections_delta": float(clean_row["detections_delta"]),
        "attack_rows": attack_rows,
        "csv": str(csv_path),
    }
    summary_path = matrix_root / "downstream_matrix_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote downstream matrix CSV: {csv_path}")
    print(f"Wrote downstream matrix summary: {summary_path}")


if __name__ == "__main__":
    main()
