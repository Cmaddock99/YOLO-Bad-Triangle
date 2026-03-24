#!/usr/bin/env python3
"""Pack clean + adversarial image pairs into a zip for DPC-UNet fine-tuning in Colab.

Usage (explicit attacks):
    PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --attacks fgsm,pgd

Usage (auto, from training signal):
    PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --from-signal

Output:
    outputs/dpc_unet_training.zip (~150 MB)

Upload the zip to your Google Drive root, then open notebooks/finetune_dpc_unet.ipynb in Colab.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

REPO = Path(__file__).parent.parent
CLEAN_DIR_DEFAULT = "coco/val2017_subset500/images"
CHECKPOINT_DEFAULT = "dpc_unet_final_golden.pt"
OUTPUT_ZIP_DEFAULT = "outputs/dpc_unet_training.zip"
SIGNAL_PATH_DEFAULT = "outputs/cycle_training_signal.json"

# Fallback attacks when no signal and no --attacks flag given
DEFAULT_ATTACKS = ["fgsm", "pgd", "deepfool", "blur"]


def _load_signal(signal_path: Path) -> dict:
    if not signal_path.is_file():
        raise FileNotFoundError(
            f"Training signal not found: {signal_path}\n"
            "Run at least one full cycle first, or pass --attacks explicitly."
        )
    signal = json.loads(signal_path.read_text())
    if "worst_attack" not in signal:
        raise ValueError(
            f"Training signal missing required key 'worst_attack': {signal_path}"
        )
    return signal


def _resolve_sweep_root(raw: str) -> Path:
    if raw:
        sweep_root = (REPO / raw).resolve()
        if not sweep_root.is_dir():
            raise FileNotFoundError(f"Sweep root not found: {sweep_root}")
        return sweep_root

    candidates = sorted(
        (REPO / "outputs" / "framework_runs").glob("sweep_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()

    raise FileNotFoundError(
        "No sweep directory found under outputs/framework_runs/. "
        "Run a sweep first or pass --sweep-root explicitly."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export training data for DPC-UNet fine-tuning.")
    parser.add_argument(
        "--from-signal",
        action="store_true",
        help=(
            f"Read {SIGNAL_PATH_DEFAULT} and export adversarial pairs for the "
            "worst_attack identified by the last completed cycle."
        ),
    )
    parser.add_argument(
        "--attacks",
        default="",
        help=(
            "Comma-separated list of attacks to include (e.g. fgsm,pgd). "
            f"Defaults to {DEFAULT_ATTACKS} if neither --from-signal nor --attacks is given."
        ),
    )
    parser.add_argument(
        "--sweep-root",
        default="",
        help=(
            "Root of the sweep run directory containing attack_* subdirs. "
            "Defaults to latest outputs/framework_runs/sweep_* if omitted."
        ),
    )
    parser.add_argument("--clean-dir", default=CLEAN_DIR_DEFAULT,
                        help="Directory of clean COCO validation images.")
    parser.add_argument("--checkpoint", default=CHECKPOINT_DEFAULT,
                        help="Pre-trained DPC-UNet checkpoint to include.")
    parser.add_argument("--output-zip", default=OUTPUT_ZIP_DEFAULT,
                        help="Output zip file path.")
    parser.add_argument("--signal-path", default=SIGNAL_PATH_DEFAULT,
                        help="Path to cycle_training_signal.json (used with --from-signal).")
    args = parser.parse_args()

    # ── Resolve attack list ───────────────────────────────────────────────────
    if args.from_signal:
        signal_path = REPO / args.signal_path
        signal = _load_signal(signal_path)
        worst_attack = signal["worst_attack"]
        attacks_to_export = [worst_attack]
        print(f"Training signal: worst_attack={worst_attack} "
              f"(cycle {signal.get('cycle_id', '?')}, "
              f"recovery={signal.get('weakest_defense_recovery', '?')})")
        print(f"  Exporting adversarial pairs for: {attacks_to_export}")
    elif args.attacks:
        attacks_to_export = [a.strip() for a in args.attacks.split(",") if a.strip()]
    else:
        attacks_to_export = list(DEFAULT_ATTACKS)

    if not attacks_to_export:
        raise ValueError("No attacks selected for export. Use --attacks or --from-signal.")

    # Map attack name → run directory name (sweep convention)
    attacks_map = {a: f"attack_{a}" for a in attacks_to_export}

    sweep_root = _resolve_sweep_root(args.sweep_root)
    clean_dir = REPO / args.clean_dir
    checkpoint = REPO / args.checkpoint
    output_zip = REPO / args.output_zip

    # ── Validate inputs ───────────────────────────────────────────────────────
    if not clean_dir.is_dir():
        raise FileNotFoundError(f"Clean images directory not found: {clean_dir}")
    for short_name, run_name in attacks_map.items():
        adv_dir = sweep_root / run_name / "images"
        if not adv_dir.is_dir():
            raise FileNotFoundError(
                f"Adversarial images not found: {adv_dir}\n"
                f"Run the sweep first: scripts/sweep_and_report.py --attacks {short_name}\n"
                f"Or pass the correct sweep directory: --sweep-root {args.sweep_root}"
            )
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    clean_images = sorted(clean_dir.glob("*.jpg")) + sorted(clean_dir.glob("*.png"))
    if not clean_images:
        raise FileNotFoundError(f"No images found in {clean_dir}")

    print(f"Packing training data into {output_zip} ...")
    print(f"  Sweep root:       {sweep_root}")
    print(f"  Clean images:     {len(clean_images)}")

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for img in clean_images:
            zf.write(img, f"clean/{img.name}")

        for short_name, run_name in attacks_map.items():
            adv_dir = sweep_root / run_name / "images"
            adv_images = sorted(adv_dir.glob("*.jpg")) + sorted(adv_dir.glob("*.png"))
            for img in adv_images:
                zf.write(img, f"adversarial/{short_name}/{img.name}")
            print(f"  {short_name:<12} adversarial: {len(adv_images)}")

        zf.write(checkpoint, f"checkpoint/{checkpoint.name}")
        print(f"  Checkpoint:       {checkpoint.name}")

    size_mb = output_zip.stat().st_size / 1024 / 1024
    print(f"\nDone. {output_zip} ({size_mb:.1f} MB)")
    print("\nNext steps:")
    print("  1. Upload outputs/dpc_unet_training.zip to your Google Drive root")
    print("  2. Open notebooks/finetune_dpc_unet.ipynb in Google Colab")
    print("  3. Runtime → Change runtime type → T4 GPU")
    print("  4. Run all cells")


if __name__ == "__main__":
    main()
