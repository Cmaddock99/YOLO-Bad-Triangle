#!/usr/bin/env python3
"""A/B comparison of two DPC-UNet checkpoints before deploying a new one.

Runs a quick validation sweep with each checkpoint and reports the mAP50 delta.
Returns exit code 0 if checkpoint B is equal or better than A, 1 if worse.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/evaluate_checkpoint.py \\
        --checkpoint-a dpc_unet_final_golden.pt \\
        --checkpoint-b dpc_unet_adversarial_finetuned.pt \\
        --attack blur

    # Fast smoke test (50 images):
    PYTHONPATH=src ./.venv/bin/python scripts/evaluate_checkpoint.py \\
        --checkpoint-a dpc_unet_final_golden.pt \\
        --checkpoint-b dpc_unet_adversarial_finetuned.pt \\
        --attack blur --images 50

    # Evaluate at non-default attack params (e.g. deepfool at stronger epsilon):
    PYTHONPATH=src ./.venv/bin/python scripts/evaluate_checkpoint.py \\
        --checkpoint-a dpc_unet_final_golden.pt \\
        --checkpoint-b dpc_unet_adversarial_finetuned.pt \\
        --attack deepfool --attack-params attack.params.epsilon=0.1

Output (JSON to stdout + human summary):
    {
      "checkpoint_a": {"path": "...", "mAP50": 0.558, "detections": 1287},
      "checkpoint_b": {"path": "...", "mAP50": 0.581, "detections": 1342},
      "delta_mAP50": 0.023,
      "verdict": "B is better — deploy"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from lab.config.profiles import (
    authoritative_metric as resolved_authoritative_metric,
    build_profile_config,
    resolve_profile_compatibility,
)

REPO = Path(__file__).resolve().parents[2]
PYTHON = REPO / ".venv" / "bin" / "python"

# Written automatically when --attack none is used. Presence of this file
# enables research_brief.py to run after every cycle in auto_cycle.py.
CLEAN_VALIDATION_SENTINEL = REPO / "outputs" / "eval_ab_clean.json"


def _env(checkpoint_path: str) -> dict:
    env = {
        **os.environ,
        "PYTHONPATH": str(REPO / "src"),
        "DPC_UNET_CHECKPOINT_PATH": checkpoint_path,
    }
    return env


def _run_validation(
    *,
    checkpoint_path: Path,
    attack: str,
    defense: str,
    run_name: str,
    runs_root: Path,
    max_images: int,
    config: str | None = None,
    profile: str | None = None,
    attack_params: list[str] | None = None,
    python_bin: Path | None = None,
) -> dict | None:
    """Run one validation experiment, return metrics dict or None on failure."""
    run_dir = runs_root / run_name
    metrics_file = run_dir / "metrics.json"
    _python = str(python_bin if python_bin is not None else PYTHON)

    if not metrics_file.exists():
        cmd = [
            _python, "scripts/run_unified.py", "run-one",
            "--set", f"attack.name={attack}",
            "--set", f"defense.name={defense}",
            "--set", f"runner.run_name={run_name}",
            "--set", f"runner.output_root={runs_root}",
            "--set", f"runner.max_images={max_images}",
            "--set", "validation.enabled=true",
        ]
        if profile:
            cmd[3:3] = ["--profile", profile]
        else:
            cmd[3:3] = ["--config", str(config or "configs/default.yaml")]
        for param in (attack_params or []):
            cmd += ["--set", param]
        result = subprocess.run(
            cmd,
            cwd=str(REPO),
            env=_env(str(checkpoint_path)),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  [error] run failed for {run_name}:", file=sys.stderr)
            print(result.stderr[-2000:], file=sys.stderr)
            return None

    if not metrics_file.exists():
        return None
    return json.loads(metrics_file.read_text())


def _extract(metrics: dict | None) -> tuple[float | None, int | None]:
    if not metrics:
        return None, None
    map50 = metrics.get("validation", {}).get("mAP50")
    dets = metrics.get("predictions", {}).get("total_detections")
    return map50, dets


def evaluate(
    *,
    checkpoint_a: Path,
    checkpoint_b: Path,
    attack: str,
    defense: str,
    images: int,
    output_json: Path | None,
    config: str | None = None,
    profile: str | None = None,
    attack_params: list[str] | None = None,
    python_bin: Path | None = None,
) -> int:
    """Run A/B evaluation. Returns 0 if B >= A, 1 if B is worse.

    Raises:
        FileNotFoundError: if either checkpoint path is missing.
        RuntimeError: if validation metrics cannot be extracted.
    """
    checkpoint_a = checkpoint_a if checkpoint_a.is_absolute() else REPO / checkpoint_a
    checkpoint_b = checkpoint_b if checkpoint_b.is_absolute() else REPO / checkpoint_b

    for cp, label in ((checkpoint_a, "A"), (checkpoint_b, "B")):
        if not cp.is_file():
            raise FileNotFoundError(f"Checkpoint {label} not found: {cp}")

    print("Evaluating A/B checkpoint comparison")
    print(f"  Attack:  {attack}")
    print(f"  Defense: {defense}")
    print(f"  Images:  {images}")
    print(f"  A: {checkpoint_a.name}")
    print(f"  B: {checkpoint_b.name}")
    print()

    with tempfile.TemporaryDirectory(prefix="eval_checkpoint_") as tmpdir:
        runs_root = Path(tmpdir)

        print("Running checkpoint A...")
        metrics_a = _run_validation(
            checkpoint_path=checkpoint_a,
            attack=attack,
            defense=defense,
            run_name="eval_a",
            runs_root=runs_root,
            max_images=images,
            config=config,
            profile=profile,
            attack_params=attack_params,
            python_bin=python_bin,
        )
        map50_a, dets_a = _extract(metrics_a)

        print("Running checkpoint B...")
        metrics_b = _run_validation(
            checkpoint_path=checkpoint_b,
            attack=attack,
            defense=defense,
            run_name="eval_b",
            runs_root=runs_root,
            max_images=images,
            config=config,
            profile=profile,
            attack_params=attack_params,
            python_bin=python_bin,
        )
        map50_b, dets_b = _extract(metrics_b)

    if map50_a is None or map50_b is None:
        raise RuntimeError("Could not extract mAP50 from one or both runs.")

    delta = map50_b - map50_a

    if abs(delta) < 0.001:
        verdict = "B is equivalent — safe to deploy"
    elif delta > 0:
        verdict = "B is better — deploy"
    else:
        verdict = "B is worse — do NOT deploy"

    result = {
        "checkpoint_a": {"path": str(checkpoint_a), "mAP50": round(map50_a, 6), "detections": dets_a},
        "checkpoint_b": {"path": str(checkpoint_b), "mAP50": round(map50_b, 6), "detections": dets_b},
        "delta_mAP50": round(delta, 6),
        "verdict": verdict,
        "attack": attack,
        "defense": defense,
        "images_evaluated": images,
    }
    if profile:
        profile_config = build_profile_config(profile)
        profile_config["attack"]["name"] = attack
        profile_config["defense"]["name"] = defense
        result["pipeline_profile"] = profile
        result["authoritative_metric"] = resolved_authoritative_metric(profile_config)
        result["profile_compatibility"] = resolve_profile_compatibility(profile_config)

    print()
    print("─" * 50)
    print(f"  Checkpoint A mAP50: {map50_a:.4f}  ({dets_a} detections)")
    print(f"  Checkpoint B mAP50: {map50_b:.4f}  ({dets_b} detections)")
    print(f"  Delta:              {delta:+.4f}")
    print(f"  Verdict:            {verdict}")
    print("─" * 50)

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        _tmp = output_json.with_suffix(".json.tmp")
        _tmp.write_text(json.dumps(result, indent=2))
        os.replace(_tmp, output_json)
        print(f"\nResult written to: {output_json}")

    # Auto-write clean validation sentinel when attack=none.
    # This enables research_brief.py to run after every subsequent cycle.
    if attack in ("none", ""):
        CLEAN_VALIDATION_SENTINEL.parent.mkdir(parents=True, exist_ok=True)
        _stmp = CLEAN_VALIDATION_SENTINEL.with_suffix(".json.tmp")
        _stmp.write_text(json.dumps(result, indent=2))
        os.replace(_stmp, CLEAN_VALIDATION_SENTINEL)
        print(f"\nClean validation sentinel written to: {CLEAN_VALIDATION_SENTINEL}")
        print("research_brief.py will now run automatically after each cycle.")

    # Threshold kept in sync with _GATE_THRESHOLD in train_from_signal.py (-0.005).
    # A candidate with delta in [-0.005, 0) should pass (evaluation noise floor).
    return 0 if delta >= -0.005 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A/B compare two DPC-UNet checkpoints via mAP50 validation."
    )
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Framework config to use when launching validation runs.",
    )
    config_group.add_argument(
        "--profile",
        help="Named pipeline profile to use when launching validation runs.",
    )
    parser.add_argument(
        "--checkpoint-a", required=True,
        help="Baseline checkpoint (relative to repo root or absolute path).",
    )
    parser.add_argument(
        "--checkpoint-b", required=True,
        help="Candidate checkpoint to evaluate against baseline.",
    )
    parser.add_argument(
        "--attack", default="blur",
        help="Attack to use for evaluation (default: blur).",
    )
    parser.add_argument(
        "--defense", default="c_dog",
        help="Defense to use for evaluation (default: c_dog).",
    )
    parser.add_argument(
        "--images", type=int, default=500,
        help="Number of images to evaluate (default: 500). Use 50 for a fast smoke test.",
    )
    parser.add_argument(
        "--attack-params",
        nargs="*",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Extra dotted-path overrides for the attack, e.g. "
            "attack.params.epsilon=0.1 attack.params.steps=50"
        ),
    )
    parser.add_argument(
        "--output-json",
        help="Write result JSON to this path (optional).",
    )
    parser.add_argument(
        "--python-bin",
        default=None,
        help="Python interpreter to use for inner run-unified.py subprocess. "
             "Defaults to the same interpreter that evaluate_checkpoint.py was invoked with.",
    )
    args = parser.parse_args()

    python_bin = Path(args.python_bin) if args.python_bin else PYTHON

    try:
        exit_code = evaluate(
            checkpoint_a=Path(args.checkpoint_a),
            checkpoint_b=Path(args.checkpoint_b),
            attack=args.attack,
            defense=args.defense,
            images=args.images,
            output_json=Path(args.output_json) if args.output_json else None,
            config=None if args.profile else args.config,
            profile=args.profile,
            attack_params=args.attack_params or [],
            python_bin=python_bin,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
