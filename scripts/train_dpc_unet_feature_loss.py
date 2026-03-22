#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from lab.defenses.dpc_unet_wrapper import DPCUNet
from lab.defenses.training import (
    CompositeLossWeights,
    FeatureLossConfig,
    YOLOFeatureExtractor,
    composite_denoising_loss,
    yolo_feature_matching_loss,
)
from lab.models.framework_registry import build_model


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scriptable DPC-UNet feature-loss training hook (single-step smoke path)."
    )
    parser.add_argument("--model", default="yolo", help="Framework model plugin name.")
    parser.add_argument("--weights", default="yolo26n.pt", help="YOLO weights path.")
    parser.add_argument(
        "--feature-layers",
        default="model.4,model.6,model.9",
        help="Comma-separated YOLO module names for feature matching.",
    )
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--imgsz", type=int, default=256)
    parser.add_argument("--edge-weight", type=float, default=0.15)
    parser.add_argument("--feature-weight", type=float, default=0.10)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    layer_names = tuple(part.strip() for part in args.feature_layers.split(",") if part.strip())
    if not layer_names:
        raise ValueError("At least one feature layer is required.")

    payload = {
        "model": args.model,
        "weights": args.weights,
        "feature_layers": layer_names,
        "batch_size": args.batch_size,
        "imgsz": args.imgsz,
        "edge_weight": args.edge_weight,
        "feature_weight": args.feature_weight,
    }
    print(json.dumps(payload, indent=2))
    if args.dry_run:
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    denoiser = DPCUNet().to(device)
    denoiser.train()
    optimizer = torch.optim.AdamW(denoiser.parameters(), lr=2e-5)

    model = build_model(args.model, model=args.weights)
    model.load()
    extractor = YOLOFeatureExtractor(
        model,
        config=FeatureLossConfig(layer_names=layer_names),
    )

    noisy = torch.rand((args.batch_size, 3, args.imgsz, args.imgsz), device=device)
    clean = torch.rand((args.batch_size, 3, args.imgsz, args.imgsz), device=device)
    denoised = denoiser(noisy, timestep=50)
    feature_loss = yolo_feature_matching_loss(extractor=extractor, denoised=denoised, clean=clean)
    total, terms = composite_denoising_loss(
        denoised=denoised,
        clean=clean,
        yolo_feature_loss=feature_loss,
        weights=CompositeLossWeights(
            pixel_weight=1.0,
            edge_weight=args.edge_weight,
            feature_weight=args.feature_weight,
        ),
    )
    optimizer.zero_grad(set_to_none=True)
    total.backward()
    optimizer.step()
    extractor.close()
    print(json.dumps(terms, indent=2))


if __name__ == "__main__":
    main()
