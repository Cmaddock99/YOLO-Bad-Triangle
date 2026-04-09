#!/usr/bin/env python3
"""Remove framework_runs directories that predate the current checkpoint promotion.

A run directory is considered stale when ALL of the following are true:
  1. Its run_summary.json (or the directory itself) predates the promotion cutoff.
  2. Its run_summary.json contains a checkpoint fingerprint that does not match
     the promoted candidate checkpoint's SHA256.

Safety: directories that are entirely missing all three required artifacts
(metrics.json, run_summary.json, predictions.jsonl) are skipped — they may be
actively in-progress runs.

Usage:
  python scripts/cleanup_stale_runs.py [--dry-run] [--before-mtime ISO8601]

Without --before-mtime, the script reads the most recent training_manifest.json
from outputs/training_runs/*/training_manifest.json and uses its generated_at
timestamp as the cutoff.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"
FRAMEWORK_RUNS = OUTPUTS / "framework_runs"
TRAINING_RUNS = OUTPUTS / "training_runs"

REQUIRED_RUN_ARTIFACTS = ("metrics.json", "run_summary.json", "predictions.jsonl")


def _load_latest_manifest() -> dict | None:
    """Return the most recent training_manifest.json payload, or None."""
    manifests = sorted(
        TRAINING_RUNS.glob("*/training_manifest.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not manifests:
        return None
    try:
        return json.loads(manifests[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _parse_iso(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp and ensure it is timezone-aware."""
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _run_dir_mtime(run_dir: Path) -> datetime:
    """Return the mtime of run_summary.json if present, else the directory itself."""
    summary = run_dir / "run_summary.json"
    target = summary if summary.exists() else run_dir
    return datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc)


def _run_dir_checkpoint_sha(run_dir: Path) -> str | None:
    """Extract provenance.checkpoint_fingerprint_sha256 from run_summary.json."""
    summary = run_dir / "run_summary.json"
    if not summary.exists():
        return None
    try:
        payload = json.loads(summary.read_text(encoding="utf-8"))
        return payload.get("provenance", {}).get("checkpoint_fingerprint_sha256")
    except (OSError, json.JSONDecodeError):
        return None


def _is_incomplete(run_dir: Path) -> bool:
    """Return True if all three required artifacts are absent (run still in progress)."""
    return not any((run_dir / f).exists() for f in REQUIRED_RUN_ARTIFACTS)


def find_stale_dirs(cutoff: datetime, promoted_sha: str | None) -> list[Path]:
    """Return list of stale run directories under FRAMEWORK_RUNS."""
    stale: list[Path] = []
    if not FRAMEWORK_RUNS.is_dir():
        return stale
    for run_dir in sorted(FRAMEWORK_RUNS.iterdir()):
        if not run_dir.is_dir():
            continue
        if _is_incomplete(run_dir):
            continue
        if _run_dir_mtime(run_dir) >= cutoff:
            continue
        # Dir predates cutoff — also check fingerprint if we have one
        if promoted_sha is not None:
            dir_sha = _run_dir_checkpoint_sha(run_dir)
            if dir_sha == promoted_sha:
                # Same checkpoint — keep it (matches promoted artifact)
                continue
        stale.append(run_dir)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print stale directories without deleting them.",
    )
    parser.add_argument(
        "--before-mtime",
        metavar="ISO8601",
        help="Treat runs older than this timestamp as potentially stale. "
             "Defaults to generated_at from the most recent training_manifest.json.",
    )
    parser.add_argument(
        "--max-delete",
        type=int,
        default=20,
        metavar="N",
        help="Abort if more than N directories would be deleted (default: 20). "
             "Pass 0 to disable the limit.",
    )
    args = parser.parse_args(argv)

    # Resolve cutoff timestamp
    promoted_sha: str | None = None
    if args.before_mtime:
        try:
            cutoff = _parse_iso(args.before_mtime)
        except ValueError as exc:
            print(f"ERROR: invalid --before-mtime value: {exc}", file=sys.stderr)
            return 2
    else:
        manifest = _load_latest_manifest()
        if manifest is None:
            print(
                "ERROR: no training_manifest.json found under outputs/training_runs/. "
                "Provide --before-mtime to specify a cutoff manually.",
                file=sys.stderr,
            )
            return 2
        try:
            cutoff = _parse_iso(manifest["generated_at"])
        except (KeyError, ValueError) as exc:
            print(f"ERROR: could not parse generated_at from manifest: {exc}", file=sys.stderr)
            return 2
        promoted_sha = (manifest.get("candidate_checkpoint") or {}).get("sha256")

    stale = find_stale_dirs(cutoff, promoted_sha)

    if not stale:
        print(f"No stale run directories found (cutoff: {cutoff.isoformat()}).")
        return 0

    if args.max_delete > 0 and len(stale) > args.max_delete and not args.dry_run:
        print(
            f"ERROR: {len(stale)} stale directories found but --max-delete is {args.max_delete}. "
            f"Run with --dry-run to review, then pass --max-delete {len(stale)} to confirm.",
            file=sys.stderr,
        )
        return 2

    mode = "DRY RUN — would remove" if args.dry_run else "Removing"
    removed = 0
    for run_dir in stale:
        age_s = (datetime.now(tz=timezone.utc) - _run_dir_mtime(run_dir)).total_seconds()
        age_h = age_s / 3600
        print(f"  {mode}: {run_dir.name}  (age {age_h:.1f}h)")
        if not args.dry_run:
            shutil.rmtree(run_dir)
            removed += 1

    if args.dry_run:
        print(f"\n{len(stale)} stale director{'y' if len(stale) == 1 else 'ies'} would be removed (--dry-run).")
    else:
        kept = sum(1 for d in FRAMEWORK_RUNS.iterdir() if d.is_dir()) if FRAMEWORK_RUNS.is_dir() else 0
        print(f"\n{removed} removed, {kept} kept.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
