#!/usr/bin/env python3
"""Local DPC-UNet fine-tuning on adversarial examples (MPS/CPU).

Adapted from notebooks/finetune_dpc_unet.ipynb for local execution on Apple Silicon.
Trains the DPC-UNet denoising defense on (adversarial, clean) image pairs.

Usage:
    export PYTHONPATH=src
    ./.venv/bin/python scripts/train_dpc_unet_local.py

    # Square-inclusive retention mix:
    ./.venv/bin/python scripts/train_dpc_unet_local.py \
        --training-zip outputs/training_exports/square_retention_training_data.zip \
        --output dpc_unet_square_retention.pt \
        --resume outputs/dpc_unet_training_resume_square_retention.pt

    # Override defaults:
    ./.venv/bin/python scripts/train_dpc_unet_local.py \
        --epochs 40 --batch-size 8 --training-zip outputs/training_exports/training_data.zip

After training:
    ./.venv/bin/python scripts/evaluate_checkpoint.py \
        --checkpoint-a dpc_unet_final_golden.pt \
        --checkpoint-b dpc_unet_square_retention.pt \
        --images 50

    # or compare any custom output checkpoint explicitly
    ./.venv/bin/python scripts/evaluate_checkpoint.py \
        --checkpoint-a dpc_unet_final_golden.pt \
        --checkpoint-b dpc_unet_adversarial_finetuned.pt \
        --images 50
"""
from __future__ import annotations

import argparse
import random
import sys
import time
import zipfile
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAINING_ZIP = "outputs/training_exports/training_data.zip"
DEFAULT_OUTPUT = "dpc_unet_adversarial_finetuned.pt"
DEFAULT_RESUME = "outputs/dpc_unet_training_resume.pt"
PRESET_CONFIGS: dict[str, dict[str, object]] = {
    "square_retention": {
        "training_zip": "outputs/training_exports/square_retention_training_data.zip",
        "output": "dpc_unet_square_retention.pt",
        "resume": "outputs/dpc_unet_training_resume_square_retention.pt",
    },
}


# ── Device selection ─────────────────────────────────────────────────────────

def _get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ── DPC-UNet architecture (exact match to production / Colab notebook) ───────

def sinusoidal_timestep_embedding(timesteps: Tensor, dim: int = 64) -> Tensor:
    if timesteps.ndim == 0:
        timesteps = timesteps.unsqueeze(0)
    timesteps = timesteps.float()
    half = dim // 2
    if half == 0:
        return timesteps.unsqueeze(-1)
    device = timesteps.device
    exponent = torch.arange(half, device=device, dtype=torch.float32) / max(half - 1, 1)
    freq = torch.exp(-torch.log(torch.tensor(10000.0, device=device)) * exponent)
    args = timesteps.unsqueeze(-1) * freq.unsqueeze(0)
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


def _num_groups(channels: int) -> int:
    for groups in (8, 4, 2, 1):
        if channels % groups == 0:
            return groups
    return 1


class DPCResidualBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.mlp = nn.Sequential(nn.SiLU(), nn.Linear(64, out_ch))
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.norm1 = nn.GroupNorm(_num_groups(out_ch), out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.norm2 = nn.GroupNorm(_num_groups(out_ch), out_ch)

    def forward(self, x: Tensor, t_embed: Tensor) -> Tensor:
        h = self.conv1(x)
        h = h + self.mlp(t_embed).unsqueeze(-1).unsqueeze(-1)
        h = F.silu(self.norm1(h))
        h = self.conv2(h)
        h = F.silu(self.norm2(h))
        return h


class DPCUNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(nn.SiLU(), nn.Linear(64, 64))
        self.down1 = DPCResidualBlock(3, 32)
        self.down2 = DPCResidualBlock(32, 64)
        self.bottleneck = DPCResidualBlock(64, 128)
        self.up2_conv = nn.Sequential(nn.Conv2d(128, 256, kernel_size=1), nn.PixelShuffle(2))
        self.up2_block = DPCResidualBlock(128, 64)
        self.up1_conv = nn.Sequential(nn.Conv2d(64, 128, kernel_size=1), nn.PixelShuffle(2))
        self.up1_block = DPCResidualBlock(64, 32)
        self.final = nn.Conv2d(32, 3, kernel_size=1)

    def forward(self, x: Tensor, timestep=50.0) -> Tensor:
        B = x.shape[0]
        if isinstance(timestep, (int, float)):
            t = torch.full((B,), float(timestep), device=x.device)
        else:
            t = timestep.to(x.device)
        t_embed = self.time_mlp(sinusoidal_timestep_embedding(t, dim=64))

        x1 = self.down1(x, t_embed)
        x2 = self.down2(F.avg_pool2d(x1, 2), t_embed)
        x3 = self.bottleneck(F.avg_pool2d(x2, 2), t_embed)

        up2 = self.up2_conv(x3)
        if up2.shape[-2:] != x2.shape[-2:]:
            up2 = F.interpolate(up2, size=x2.shape[-2:], mode="bilinear", align_corners=False)
        up2 = self.up2_block(torch.cat([up2, x2], dim=1), t_embed)

        up1 = self.up1_conv(up2)
        if up1.shape[-2:] != x1.shape[-2:]:
            up1 = F.interpolate(up1, size=x1.shape[-2:], mode="bilinear", align_corners=False)
        up1 = self.up1_block(torch.cat([up1, x1], dim=1), t_embed)
        return self.final(up1)


# ── Dataset ──────────────────────────────────────────────────────────────────

class AdvPairDataset(Dataset):
    def __init__(self, pairs: list, patch_size: int = 192, augment: bool = True):
        self.pairs = pairs
        self.patch_size = patch_size
        self.augment = augment

    @classmethod
    def from_dirs(cls, clean_dir: Path, adv_dirs: dict, patch_size: int = 192, augment: bool = True):
        clean_paths = sorted(Path(clean_dir).glob("*.jpg"))
        pairs = []
        for clean_path in clean_paths:
            for attack_name, adv_dir in adv_dirs.items():
                adv_path = Path(adv_dir) / clean_path.name
                if adv_path.exists():
                    pairs.append((str(clean_path), str(adv_path), attack_name))
        print(f"  {len(clean_paths)} images × {len(adv_dirs)} attacks = {len(pairs)} pairs")
        return cls(pairs, patch_size=patch_size, augment=augment)

    def split(self, val_frac: float = 0.10, seed: int = 42):
        pairs = self.pairs.copy()
        random.Random(seed).shuffle(pairs)
        n_val = max(1, int(len(pairs) * val_frac))
        val_ds = AdvPairDataset(pairs[:n_val], self.patch_size, augment=False)
        train_ds = AdvPairDataset(pairs[n_val:], self.patch_size, augment=True)
        return train_ds, val_ds

    def __len__(self) -> int:
        return len(self.pairs)

    def _load_and_crop(self, clean_path: str, adv_path: str):
        clean = cv2.imread(clean_path)
        adv = cv2.imread(adv_path)
        if clean is None or adv is None:
            raise RuntimeError(f"Failed to load image pair: {clean_path}")
        p = self.patch_size
        h, w = clean.shape[:2]
        if h < p or w < p:
            ph, pw = max(0, p - h), max(0, p - w)
            clean = cv2.copyMakeBorder(clean, 0, ph, 0, pw, cv2.BORDER_REFLECT)
            adv = cv2.copyMakeBorder(adv, 0, ph, 0, pw, cv2.BORDER_REFLECT)
            h, w = clean.shape[:2]
        if self.augment:
            y = random.randint(0, h - p)
            x = random.randint(0, w - p)
        else:
            y = (h - p) // 2
            x = (w - p) // 2
        return clean[y : y + p, x : x + p], adv[y : y + p, x : x + p]

    @staticmethod
    def _to_tensor(img_bgr: np.ndarray) -> torch.Tensor:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return torch.from_numpy(img_rgb.astype(np.float32) / 255.0).permute(2, 0, 1)

    def __getitem__(self, idx: int):
        clean_path, adv_path, _ = self.pairs[idx]
        clean_bgr, adv_bgr = self._load_and_crop(clean_path, adv_path)
        if self.augment:
            if random.random() < 0.5:
                clean_bgr = cv2.flip(clean_bgr, 1)
                adv_bgr = cv2.flip(adv_bgr, 1)
            if random.random() < 0.3:
                clean_bgr = cv2.flip(clean_bgr, 0)
                adv_bgr = cv2.flip(adv_bgr, 0)
        return self._to_tensor(adv_bgr), self._to_tensor(clean_bgr)


# ── YOLO label loader (for detector-aligned loss) ────────────────────────────

def _load_yolo_labels(label_file: Path, device: torch.device):
    """Load YOLO-format label file. Returns (N,6) tensor [batch_idx, cls, cx, cy, w, h]."""
    rows = []
    for line in label_file.read_text().strip().splitlines():
        parts = line.split()
        if len(parts) != 5:
            continue
        cls, cx, cy, w, h = (float(x) for x in parts)
        rows.append([0.0, cls, cx, cy, w, h])
    return torch.tensor(rows, dtype=torch.float32, device=device) if rows else None


# ── Loss ─────────────────────────────────────────────────────────────────────

def sobel_edges(x: torch.Tensor) -> torch.Tensor:
    kx = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32, device=x.device)
    ky = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32, device=x.device)
    C = x.shape[1]
    kx = kx.view(1, 1, 3, 3).expand(C, 1, 3, 3)
    ky = ky.view(1, 1, 3, 3).expand(C, 1, 3, 3)
    gx = F.conv2d(x, kx, padding=1, groups=C)
    gy = F.conv2d(x, ky, padding=1, groups=C)
    return torch.sqrt(gx**2 + gy**2 + 1e-8)


def denoising_loss(output: torch.Tensor, target: torch.Tensor, edge_weight: float = 0.15):
    pixel = F.l1_loss(output, target)
    edge = F.l1_loss(sobel_edges(output), sobel_edges(target))
    total = pixel + edge_weight * edge
    return total, pixel.item(), edge.item()


# ── Training ─────────────────────────────────────────────────────────────────

def _resolve_training_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    preset = PRESET_CONFIGS.get(args.preset, {})
    training_zip_raw = args.training_zip or str(preset.get("training_zip", DEFAULT_TRAINING_ZIP))
    output_raw = args.output or str(preset.get("output", DEFAULT_OUTPUT))
    resume_raw = args.resume or str(preset.get("resume", DEFAULT_RESUME))
    return ROOT / training_zip_raw, ROOT / output_raw, ROOT / resume_raw


def train(args: argparse.Namespace) -> None:
    device = _get_device()
    print(f"Device: {device}")

    zip_path, save_path, resume_path = _resolve_training_paths(args)
    if args.preset:
        print(f"Preset: {args.preset}")
    print(f"Training zip: {zip_path}")
    print(f"Output checkpoint: {save_path}")
    print(f"Resume checkpoint: {resume_path}")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    resume_path.parent.mkdir(parents=True, exist_ok=True)

    deployed_checkpoint = (ROOT / DEFAULT_OUTPUT).resolve()
    if save_path.resolve() == deployed_checkpoint and args.preset:
        raise ValueError(
            f"Preset '{args.preset}' must not overwrite the deployed checkpoint; "
            f"choose --output explicitly if you really want a different path."
        )

    if not zip_path.exists():
        print(f"ERROR: Training zip not found: {zip_path}")
        print("Run: export PYTHONPATH=src && ./.venv/bin/python scripts/export_training_data.py")
        sys.exit(1)

    extract_dir = ROOT / "outputs" / "training_data" / zip_path.stem

    # Seed
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)

    # Extract training data
    if not extract_dir.exists():
        print(f"Extracting {zip_path.name}...")
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        print("  Done.")
    else:
        print(f"Training data already extracted at {extract_dir}")

    if not extract_dir.is_dir():
        print(f"ERROR: Training extraction directory missing: {extract_dir}")
        sys.exit(1)

    print(f"Extract dir: {extract_dir}")

    attack_listing = extract_dir / "adversarial"
    if attack_listing.is_dir():
        available_attack_dirs = sorted(d.name for d in attack_listing.iterdir() if d.is_dir())
        print(f"Available extracted attack dirs: {available_attack_dirs}")

    clean_dir = extract_dir / "clean"
    checkpoint_path = extract_dir / "checkpoint" / "dpc_unet_final_golden.pt"

    # Find attack directories
    adv_root = extract_dir / "adversarial"
    adv_dirs = {}
    for d in sorted(adv_root.iterdir()):
        if d.is_dir() and list(d.glob("*.jpg")):
            adv_dirs[d.name] = d
    print(f"Attacks found: {list(adv_dirs.keys())}")

    if not checkpoint_path.exists():
        # Fall back to repo root checkpoint
        checkpoint_path = ROOT / "dpc_unet_final_golden.pt"
    if not checkpoint_path.exists():
        print("ERROR: Golden checkpoint not found")
        sys.exit(1)

    # Apply oversampling — repeat pairs for specified attack dirs
    if args.oversample:
        for spec in args.oversample.split(","):
            spec = spec.strip()
            if ":" not in spec:
                continue
            name, n_str = spec.split(":", 1)
            n = int(n_str)
            if name in adv_dirs:
                for i in range(1, n):
                    adv_dirs[f"{name}_rep{i}"] = adv_dirs[name]
                print(f"  Oversampling '{name}' ×{n}")
            else:
                print(f"  WARNING: --oversample '{name}' not found in attack dirs, skipping")

    # Build dataset
    print("\nBuilding dataset...")
    full_ds = AdvPairDataset.from_dirs(clean_dir, adv_dirs, patch_size=args.patch_size, augment=True)
    train_ds, val_ds = full_ds.split(val_frac=0.10, seed=args.seed)

    # ── Detector-aligned loss setup ───────────────────────────────────────────
    yolo_inner = None
    full_adv_pairs: list = []
    labels_dir = ROOT / "coco" / "val2017_subset500" / "labels"

    if args.det_loss_weight > 0:
        yolo_ckpt = ROOT / "yolo26n.pt"
        if not yolo_ckpt.exists():
            print("WARNING: yolo26n.pt not found — detector loss disabled")
        elif not labels_dir.exists():
            print("WARNING: labels dir not found — detector loss disabled")
        else:
            from types import SimpleNamespace
            from ultralytics import YOLO as _YOLO
            yolo_inner = _YOLO(str(yolo_ckpt)).model
            # Build args SimpleNamespace with required loss weights.
            # Pretrained model saves args as a dict that may lack box/cls/dfl;
            # merge existing args then force-set the required keys.
            _required_hyp = {"box": 7.5, "cls": 0.5, "dfl": 1.5}
            _existing: dict = {}
            if hasattr(yolo_inner, "args") and yolo_inner.args is not None:
                if isinstance(yolo_inner.args, dict):
                    _existing = yolo_inner.args
                elif hasattr(yolo_inner.args, "__dict__"):
                    _existing = vars(yolo_inner.args)
            yolo_inner.args = SimpleNamespace(**{**_existing, **_required_hyp})
            # Move to device FIRST — criterion captures device via next(model.parameters()).device
            yolo_inner = yolo_inner.to(device)
            yolo_inner.criterion = yolo_inner.init_criterion()
            yolo_inner.train()
            for p in yolo_inner.parameters():
                p.requires_grad_(False)
            for clean_path, adv_path, _ in full_ds.pairs:
                lbl = labels_dir / (Path(clean_path).stem + ".txt")
                if lbl.exists():
                    full_adv_pairs.append((clean_path, adv_path))
            print(f"Detector loss: weight={args.det_loss_weight}, "
                  f"{len(full_adv_pairs)} eligible images, "
                  f"{args.det_images_per_epoch} sampled/epoch")

    # MPS doesn't support num_workers > 0 well with fork
    num_workers = 0 if device.type == "mps" else 4
    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=(device.type == "cuda"), drop_last=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=(device.type == "cuda"),
    )
    print(f"Train: {len(train_ds):>5} pairs  ({len(train_loader)} batches/epoch)")
    print(f"Val:   {len(val_ds):>5} pairs  ({len(val_loader)} batches)")

    # Model
    model = DPCUNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-7)

    # AMP — only for CUDA; MPS and CPU train in float32
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None

    start_epoch = 1
    best_val_loss = float("inf")
    history: dict[str, list] = {"train": [], "val": [], "pixel": [], "edge": []}

    # Resume or fresh start
    if resume_path.is_file() and not args.fresh:
        print(f"\nResuming from {resume_path}")
        ckpt = torch.load(str(resume_path), map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        scheduler.load_state_dict(ckpt["scheduler"])
        if scaler and "scaler" in ckpt:
            scaler.load_state_dict(ckpt["scaler"])
        start_epoch = ckpt["epoch"] + 1
        best_val_loss = ckpt["best_val_loss"]
        history = ckpt["history"]
        print(f"  Resuming from epoch {start_epoch}/{args.epochs}  (best val: {best_val_loss:.4f})")
    else:
        state_dict = torch.load(str(checkpoint_path), map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict, strict=True)
        print(f"\nFresh start — loaded: {checkpoint_path.name}")

    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Optimizer: Adam lr={args.lr}, cosine decay → 1e-7 over {args.epochs} epochs")
    print()

    t_start = time.time()

    for epoch in range(start_epoch, args.epochs + 1):
        # ── Train ──
        model.train()
        ep_loss = ep_pixel = ep_edge = 0.0

        for adv_imgs, clean_imgs in train_loader:
            adv_imgs = adv_imgs.to(device, non_blocking=True)
            clean_imgs = clean_imgs.to(device, non_blocking=True)
            t = random.uniform(args.timestep_min, args.timestep_max)

            optimizer.zero_grad(set_to_none=True)

            if use_amp:
                with torch.autocast("cuda"):
                    output = torch.clamp(model(adv_imgs, timestep=t), 0.0, 1.0)
                    loss, pixel_l, edge_l = denoising_loss(output, clean_imgs, args.edge_weight)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                scaler.step(optimizer)
                scaler.update()
            else:
                output = torch.clamp(model(adv_imgs, timestep=t), 0.0, 1.0)
                loss, pixel_l, edge_l = denoising_loss(output, clean_imgs, args.edge_weight)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                optimizer.step()

            ep_loss += loss.item()
            ep_pixel += pixel_l
            ep_edge += edge_l

        n_batches = len(train_loader)
        train_loss = ep_loss / n_batches
        train_pixel = ep_pixel / n_batches
        train_edge = ep_edge / n_batches

        # ── Validate ──
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for adv_imgs, clean_imgs in val_loader:
                adv_imgs = adv_imgs.to(device, non_blocking=True)
                clean_imgs = clean_imgs.to(device, non_blocking=True)
                output = torch.clamp(model(adv_imgs, timestep=50.0), 0.0, 1.0)
                loss, _, _ = denoising_loss(output, clean_imgs, args.edge_weight)
                val_loss += loss.item()
        val_loss /= len(val_loader)

        # ── Detector alignment pass (one update per epoch) ────────────────────
        det_loss_val = 0.0
        if yolo_inner is not None and full_adv_pairs:
            sampled = random.sample(full_adv_pairs,
                                    min(args.det_images_per_epoch, len(full_adv_pairs)))
            optimizer.zero_grad(set_to_none=True)
            n_ok = 0
            for clean_path, adv_path in sampled:
                adv_bgr = cv2.imread(adv_path)
                if adv_bgr is None:
                    continue
                adv_t = (torch.from_numpy(
                    cv2.cvtColor(cv2.resize(adv_bgr, (640, 640)),
                                 cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                ).permute(2, 0, 1).unsqueeze(0).to(device))
                lbl_t = _load_yolo_labels(
                    labels_dir / (Path(clean_path).stem + ".txt"), device)
                if lbl_t is None:
                    continue
                model.train()
                purified = torch.clamp(model(adv_t, timestep=50.0), 0.0, 1.0)
                preds = yolo_inner(purified)
                det_loss, _ = yolo_inner.loss(
                    {"img": purified, "batch_idx": lbl_t[:, 0],
                     "cls": lbl_t[:, 1], "bboxes": lbl_t[:, 2:]},
                    preds=preds,
                )
                (det_loss.sum() * args.det_loss_weight / len(sampled)).backward()
                det_loss_val += det_loss.sum().item()
                n_ok += 1
            if n_ok > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                det_loss_val /= n_ok

        scheduler.step()

        history["train"].append(train_loss)
        history["val"].append(val_loss)
        history["pixel"].append(train_pixel)
        history["edge"].append(train_edge)

        # Save best
        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss
            torch.save(model.state_dict(), str(save_path))

        # Save resume checkpoint
        resume_data = {
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
            "best_val_loss": best_val_loss,
            "history": history,
        }
        if scaler:
            resume_data["scaler"] = scaler.state_dict()
        torch.save(resume_data, str(resume_path))

        lr_now = scheduler.get_last_lr()[0]
        elapsed = time.time() - t_start
        eta = elapsed / (epoch - start_epoch + 1) * (args.epochs - epoch) if epoch > start_epoch else 0
        print(
            f"Epoch {epoch:02d}/{args.epochs}  "
            f"train={train_loss:.4f} (px={train_pixel:.4f} edge={train_edge:.4f})  "
            f"val={val_loss:.4f}  "
            + (f"det={det_loss_val:.4f}  " if yolo_inner is not None else "")
            + f"lr={lr_now:.1e}  "
            f"[{elapsed:.0f}s elapsed, ~{eta:.0f}s remaining]"
            + ("  ← best" if is_best else "")
        )

    total_time = time.time() - t_start
    print(f"\nTraining complete in {total_time:.0f}s ({total_time/60:.1f} min).")
    print(f"Best val loss: {best_val_loss:.4f}")
    print(f"Checkpoint saved: {save_path}")
    print("\nNext step — evaluate:")
    print("  export PYTHONPATH=src")
    print("  ./.venv/bin/python scripts/evaluate_checkpoint.py \\")
    print("    --checkpoint-a dpc_unet_final_golden.pt \\")
    print(f"    --checkpoint-b {save_path.name} \\")
    print("    --images 50")


def main():
    parser = argparse.ArgumentParser(description="Local DPC-UNet fine-tuning (MPS/CPU)")
    parser.add_argument(
        "--preset",
        default="",
        choices=sorted(PRESET_CONFIGS),
        help=(
            "Named training preset. "
            "square_retention uses isolated zip/output/resume paths so it won't clobber the deployed checkpoint path."
        ),
    )
    parser.add_argument("--training-zip", default="",
                        help="Path to training data zip (overrides preset/default when set)")
    parser.add_argument("--output", default="",
                        help="Output checkpoint filename relative to repo root (overrides preset/default when set)")
    parser.add_argument("--resume", default="",
                        help="Resume checkpoint path relative to repo root (overrides preset/default when set)")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--patch-size", type=int, default=192)
    parser.add_argument("--edge-weight", type=float, default=0.25)
    parser.add_argument("--timestep-min", type=float, default=5.0)
    parser.add_argument("--timestep-max", type=float, default=100.0)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fresh", action="store_true",
                        help="Ignore resume checkpoint, start fresh from golden")
    parser.add_argument(
        "--oversample",
        default="",
        help=(
            "Comma-separated ATTACK:N pairs to oversample new attack dirs, "
            "e.g. deepfool_strong:4,eot_pgd:4. Repeats those pairs N times "
            "in the dataset to counteract low sample counts."
        ),
    )
    parser.add_argument("--det-loss-weight", type=float, default=0.0,
                        help="Weight of detector-aligned loss term (0=disabled). Suggest 0.1-0.2.")
    parser.add_argument("--det-images-per-epoch", type=int, default=20,
                        help="Number of full images sampled per epoch for detector alignment pass.")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
