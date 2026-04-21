#!/usr/bin/env python3
"""Run the full signal-driven training ritual after a completed auto_cycle.

Steps:
  1. Validate that outputs/cycle_training_signal.json exists and is fresh
     (mtime within --max-age-hours, default 24).
  2. Run export_training_data.py → writes outputs/training_exports/<cycle_id>/
  3. Run train_from_signal.py → trains, gates, and writes training_manifest.json
  4. Print the final verdict from training_manifest.json.

Usage:
  python scripts/run_training_ritual.py [--dry-run] [--max-age-hours 24]
                                        [--python-bin PATH]

The script exits non-zero on any failure and prints a clear reason to stderr.
Promotion remains manual: the script will print the exact mv/cp commands when
train_from_signal.py reaches PROMOTION READY.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUTS = REPO / "outputs"
SIGNAL_PATH = OUTPUTS / "cycle_training_signal.json"

from lab.runners.cli_utils import build_repo_python_command, resolve_python_bin  # noqa: E402
from lab.config.profiles import learned_defense_compatibility  # noqa: E402


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _check_signal(max_age_hours: float) -> dict:
    """Load and validate the training signal file. Raises SystemExit on failure."""
    if not SIGNAL_PATH.exists():
        print(
            f"ERROR: signal file not found: {SIGNAL_PATH}\n"
            "Run auto_cycle.py until _write_training_signal completes.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    age = _now() - datetime.fromtimestamp(SIGNAL_PATH.stat().st_mtime, tz=timezone.utc)
    if age > timedelta(hours=max_age_hours):
        print(
            f"ERROR: signal file is {age.total_seconds() / 3600:.1f}h old "
            f"(max allowed: {max_age_hours}h): {SIGNAL_PATH}\n"
            "Run auto_cycle.py again or pass --max-age-hours to relax the limit.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    try:
        return json.loads(SIGNAL_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not parse signal file: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def _run_step(label: str, cmd: list[str], *, dry_run: bool) -> None:
    """Print and optionally execute a subprocess step. Raises SystemExit on non-zero."""
    print(f"\n[ritual] {label}")
    print(f"  $ {' '.join(cmd)}")
    if dry_run:
        print("  (dry-run — skipped)")
        return
    result = subprocess.run(cmd, cwd=REPO)
    if result.returncode != 0:
        print(
            f"\nERROR: {label} failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        raise SystemExit(result.returncode)


def _print_verdict(signal: dict) -> None:
    """Read and print the final verdict from the most recent training_manifest.json."""
    cycle_id = signal.get("cycle_id", "")
    manifest_path = OUTPUTS / "training_runs" / cycle_id / "training_manifest.json"
    if not manifest_path.exists():
        print("\n[ritual] training_manifest.json not found — dry-run or early exit.")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"\n[ritual] WARNING: could not read manifest: {exc}")
        return

    verdict = manifest.get("final_verdict", "unknown")
    clean_delta = (manifest.get("clean_gate") or {}).get("delta_mAP50")
    attack_delta = (manifest.get("attack_gate") or {}).get("delta_mAP50")

    print(f"\n[ritual] Final verdict: {verdict}")
    if clean_delta is not None:
        print(f"         Clean gate delta mAP50:  {clean_delta:+.4f}")
    if attack_delta is not None:
        print(f"         Attack gate delta mAP50: {attack_delta:+.4f}")
    if verdict == "passed_both_manual_promotion_required":
        print("\n[ritual] PROMOTION READY — run the mv/cp commands printed above.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print commands without executing them.",
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=24.0,
        metavar="H",
        help="Reject the signal file if it is older than H hours (default: 24).",
    )
    parser.add_argument(
        "--python-bin",
        default=None,
        metavar="PATH",
        help="Python interpreter to use for subprocesses. Defaults to venv discovery.",
    )
    parser.add_argument(
        "--profile",
        help="Optional pipeline profile. When set, learned-defense training must be compatible with it.",
    )
    args = parser.parse_args(argv)

    python_bin = args.python_bin or resolve_python_bin(REPO)

    # Step 1: validate signal
    try:
        signal = _check_signal(args.max_age_hours)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 2
    cycle_id = signal.get("cycle_id", "unknown")
    worst_attack = signal.get("worst_attack", "unknown")
    print(f"[ritual] Signal OK — cycle_id={cycle_id}, worst_attack={worst_attack}")
    if args.profile:
        compatibility = learned_defense_compatibility(args.profile)
        if not bool(compatibility.get("trainable", False)):
            reason = str(compatibility.get("reason") or f"{args.profile} does not support learned-defense training.")
            print(
                f"[ritual] Non-promotable: profile '{args.profile}' blocks learned-defense training. {reason}",
                file=sys.stderr,
            )
            return 2

    # Step 2: export training data
    export_cmd = build_repo_python_command(
        REPO,
        "scripts/export_training_data.py",
        ["--from-signal", str(SIGNAL_PATH)],
        python_bin=python_bin,
    )
    try:
        _run_step("export_training_data", export_cmd, dry_run=args.dry_run)
    except SystemExit as exc:
        code = exc.code
        if code == 2:
            print(
                "\nERROR: export found no usable attacks — check signal or re-run auto_cycle.",
                file=sys.stderr,
            )
        return int(code) if code is not None else 1

    # Step 3: train from signal
    train_cmd = build_repo_python_command(
        REPO,
        "scripts/train_from_signal.py",
        (["--profile", args.profile] if args.profile else []),
        python_bin=python_bin,
    )
    try:
        _run_step("train_from_signal", train_cmd, dry_run=args.dry_run)
    except SystemExit as exc:
        _print_verdict(signal)
        return int(exc.code) if exc.code is not None else 1

    # Step 4: report verdict
    _print_verdict(signal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
