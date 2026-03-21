#!/usr/bin/env python3
"""Pack clean + adversarial image pairs into a zip for DPC-UNet fine-tuning in Colab.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py

Output:
    outputs/dpc_unet_training.zip (~150 MB)

Upload the zip to your Google Drive root, then open notebooks/finetune_dpc_unet.ipynb in Colab.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

SWEEP_ROOT_DEFAULT = "outputs/framework_runs/sweep_20260321T033240Z"
CLEAN_DIR_DEFAULT = "coco/val2017_subset500/images"
CHECKPOINT_DEFAULT = "dpc_unet_final_golden.pt"
OUTPUT_ZIP_DEFAULT = "outputs/dpc_unet_training.zip"

ATTACKS = {
    "fgsm": "attack_fgsm",
    "pgd": "attack_pgd",
    "deepfool": "attack_deepfool",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export training data for DPC-UNet fine-tuning.")
    parser.add_argument("--sweep-root", default=SWEEP_ROOT_DEFAULT,
                        help="Root of the sweep run directory containing attack_* subdirs.")
    parser.add_argument("--clean-dir", default=CLEAN_DIR_DEFAULT,
                        help="Directory of clean COCO validation images.")
    parser.add_argument("--checkpoint", default=CHECKPOINT_DEFAULT,
                        help="Pre-trained DPC-UNet checkpoint to include.")
    parser.add_argument("--output-zip", default=OUTPUT_ZIP_DEFAULT,
                        help="Output zip file path.")
    args = parser.parse_args()

    sweep_root = Path(args.sweep_root)
    clean_dir = Path(args.clean_dir)
    checkpoint = Path(args.checkpoint)
    output_zip = Path(args.output_zip)

    # Validate inputs
    if not clean_dir.is_dir():
        raise FileNotFoundError(f"Clean images directory not found: {clean_dir}")
    for short_name, run_name in ATTACKS.items():
        adv_dir = sweep_root / run_name / "images"
        if not adv_dir.is_dir():
            raise FileNotFoundError(
                f"Adversarial images not found: {adv_dir}\n"
                f"Run the sweep first: scripts/sweep_and_report.py --attacks {short_name}"
            )
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    clean_images = sorted(clean_dir.glob("*.jpg")) + sorted(clean_dir.glob("*.png"))
    if not clean_images:
        raise FileNotFoundError(f"No images found in {clean_dir}")

    print(f"Packing training data into {output_zip} ...")
    print(f"  Clean images:     {len(clean_images)}")

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for img in clean_images:
            zf.write(img, f"clean/{img.name}")

        for short_name, run_name in ATTACKS.items():
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
