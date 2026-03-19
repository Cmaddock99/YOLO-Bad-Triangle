#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import torch

from lab.defenses.dpc_unet_wrapper import DPCUNet, load_checkpoint_state_dict, strict_load_with_report


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checkpoint(checkpoint: Path) -> dict[str, Any]:
    state_dict = load_checkpoint_state_dict(checkpoint)
    model = DPCUNet()
    load_report = strict_load_with_report(model, state_dict)
    total_params = int(sum(int(value.numel()) for value in state_dict.values()))
    first_keys = list(state_dict.keys())[:20]
    shape_preview = {key: list(state_dict[key].shape) for key in first_keys[:10]}

    verdict = "pass" if load_report.strict_passed else "investigate"
    return {
        "checkpoint_path": str(checkpoint),
        "checkpoint_sha256": _sha256(checkpoint),
        "file_size_bytes": checkpoint.stat().st_size,
        "state_dict_keys": len(state_dict),
        "total_parameters": total_params,
        "strict_load": {
            "passed": load_report.strict_passed,
            "missing_keys": load_report.missing_keys,
            "unexpected_keys": load_report.unexpected_keys,
            "error_message": load_report.error_message,
        },
        "first_keys": first_keys,
        "shape_preview": shape_preview,
        "verdict": verdict,
        "notes": (
            "Verdict PASS requires strict_load.passed=true. "
            "Investigate any missing/unexpected keys before integration."
        ),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify wrapper checkpoint contract and strict loadability.")
    parser.add_argument(
        "--checkpoint",
        default="/Users/lurch/Downloads/dpc_unet_final_golden.pt",
        help="Path to wrapper checkpoint file.",
    )
    parser.add_argument(
        "--output",
        default="outputs/wrapper_verification/checkpoint_contract.json",
        help="Output JSON report path.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    checkpoint = Path(args.checkpoint).expanduser().resolve()
    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")
    report = verify_checkpoint(checkpoint)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    torch.set_grad_enabled(False)
    main()
