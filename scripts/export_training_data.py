#!/usr/bin/env python3
"""Pack clean + adversarial image pairs into a zip for DPC-UNet fine-tuning in Colab.

Usage (explicit attacks):
    PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --attacks fgsm,pgd

Usage (auto, from training signal):
    PYTHONPATH=src ./.venv/bin/python scripts/export_training_data.py --from-signal

Output:
    outputs/training_exports/<cycle_id>_training_data.zip  (when --from-signal or called by auto_cycle)
    outputs/training_exports/training_data.zip             (manual fallback)

Upload the zip to your Google Drive root, then open notebooks/finetune_dpc_unet.ipynb in Colab.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).parent.parent
CLEAN_DIR_DEFAULT = "coco/val2017_subset500/images"
CHECKPOINT_DEFAULT = "dpc_unet_final_golden.pt"
OUTPUT_ZIP_DEFAULT = "outputs/training_exports/training_data.zip"
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
            raise FileNotFoundError(f"Runs root not found: {sweep_root}")
        return sweep_root

    framework_runs = REPO / "outputs" / "framework_runs"
    # Search sweep_* first (legacy naming), then cycle_* (current auto_cycle naming)
    for glob_pattern in ("sweep_*", "cycle_*"):
        candidates = sorted(
            framework_runs.glob(glob_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            if candidate.is_dir():
                return candidate.resolve()

    raise FileNotFoundError(
        "No run directory found under outputs/framework_runs/. "
        "Run a cycle or sweep first, or pass --sweep-root explicitly."
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
    signal_cycle_id: str | None = None
    if args.from_signal:
        signal_path = REPO / args.signal_path
        signal = _load_signal(signal_path)
        worst_attack = signal["worst_attack"]
        signal_cycle_id = signal.get("cycle_id")
        attacks_to_export = [worst_attack]
        print(f"Training signal: worst_attack={worst_attack} "
              f"(cycle {signal_cycle_id or '?'}, "
              f"recovery={signal.get('weakest_defense_recovery', '?')})")
        print(f"  Exporting adversarial pairs for: {attacks_to_export}")
    elif args.attacks:
        attacks_to_export = [a.strip() for a in args.attacks.split(",") if a.strip()]
    else:
        attacks_to_export = list(DEFAULT_ATTACKS)

    if not attacks_to_export:
        raise ValueError("No attacks selected for export. Use --attacks or --from-signal.")

    sweep_root = _resolve_sweep_root(args.sweep_root)
    clean_dir = REPO / args.clean_dir
    checkpoint = REPO / args.checkpoint

    # ── Resolve output zip path ───────────────────────────────────────────────
    # If caller did not override --output-zip and we have a cycle_id from signal,
    # use a cycle-specific path instead of the generic default.
    if args.output_zip == OUTPUT_ZIP_DEFAULT and signal_cycle_id:
        output_zip = REPO / "outputs" / "training_exports" / f"{signal_cycle_id}_training_data.zip"
    else:
        output_zip = REPO / args.output_zip

    # ── Validate inputs ───────────────────────────────────────────────────────
    if not clean_dir.is_dir():
        raise FileNotFoundError(f"Clean images directory not found: {clean_dir}")
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    # Collect usable attack dirs — warn on missing/empty, fail gracefully if none found.
    # Prefer Phase 4 validate_atk_<name>/images/ (500 images) over Phase 1 attack_<name>/images/ (32 images).
    usable_attacks: dict[str, list[Path]] = {}
    for short_name in attacks_to_export:
        candidates = [f"validate_atk_{short_name}", f"attack_{short_name}"]
        chosen_dir: Path | None = None
        for run_name in candidates:
            adv_dir = sweep_root / run_name / "images"
            if adv_dir.is_dir():
                chosen_dir = adv_dir
                break
        images = (
            sorted(chosen_dir.glob("*.jpg")) + sorted(chosen_dir.glob("*.png"))
            if chosen_dir is not None else []
        )
        if not images:
            print(
                f"[warn] No attacked images found for '{short_name}' "
                f"(tried: {', '.join(candidates)}) — skipping this attack."
            )
        else:
            print(f"  {short_name}: using {chosen_dir.parent.name}/images/ ({len(images)} images)")
            usable_attacks[short_name] = images

    if not usable_attacks:
        print(
            f"[warn] No usable attacked image pairs found under {sweep_root}. "
            "Phase 1/2 smoke runs must have completed before export. "
            "Skipping export — no zip written."
        )
        sys.exit(0)

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    clean_images = sorted(clean_dir.glob("*.jpg")) + sorted(clean_dir.glob("*.png"))
    if not clean_images:
        raise FileNotFoundError(f"No images found in {clean_dir}")

    print(f"Packing training data into {output_zip} ...")
    print(f"  Runs root:        {sweep_root}")
    print(f"  Clean images:     {len(clean_images)}")

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for img in clean_images:
            zf.write(img, f"clean/{img.name}")

        for short_name, adv_images in usable_attacks.items():
            for img in adv_images:
                zf.write(img, f"adversarial/{short_name}/{img.name}")
            print(f"  {short_name:<12} adversarial: {len(adv_images)}")

        zf.write(checkpoint, f"checkpoint/{checkpoint.name}")
        print(f"  Checkpoint:       {checkpoint.name}")

    size_mb = output_zip.stat().st_size / 1024 / 1024
    print(f"\nDone. {output_zip} ({size_mb:.1f} MB)")
    print("\nNext steps:")
    print(f"  python scripts/train_dpc_unet_local.py --training-zip {output_zip}")
    print("  (or upload to Google Drive and use notebooks/finetune_dpc_unet.ipynb on Colab)")


if __name__ == "__main__":
    main()
