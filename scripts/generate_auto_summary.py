"""Generate auto-summary artifacts for a framework runs directory.

Usage:
    PYTHONPATH=src python scripts/generate_auto_summary.py \\
        --runs-root outputs/framework_runs/cycle_20260326_112654

Outputs (written to --output-dir, default outputs/summaries/<runs_root_name>/):
    summary.json              — full payload (schema: cycle_summary/v1)
    summary.md                — human-readable markdown
    headline_metrics.csv      — 34-column attack/defense matrix
    per_class_vulnerability.csv — 15-column per-class detection drop
    warnings.json             — warning codes (schema: warnings/v1)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate auto-summary artifacts for a framework runs directory."
    )
    p.add_argument(
        "--runs-root",
        required=True,
        type=Path,
        help="Directory containing framework run subdirs (each with metrics.json + run_summary.json).",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to outputs/summaries/<runs_root_name>.",
    )
    p.add_argument(
        "--no-bootstrap",
        action="store_true",
        default=False,
        help="Skip bootstrap CI computation (faster, no confidence intervals).",
    )
    p.add_argument(
        "--bootstrap-n",
        type=int,
        default=2000,
        help="Number of bootstrap resamples (default: 2000).",
    )
    p.add_argument(
        "--bootstrap-seed",
        type=int,
        default=42,
        help="RNG seed for bootstrap (default: 42).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    runs_root = args.runs_root.expanduser().resolve()
    if not runs_root.exists():
        print(f"ERROR: runs-root does not exist: {runs_root}", file=sys.stderr)
        sys.exit(1)
    if not runs_root.is_dir():
        print(f"ERROR: runs-root is not a directory: {runs_root}", file=sys.stderr)
        sys.exit(1)

    if args.output_dir is not None:
        output_dir = args.output_dir.expanduser().resolve()
    else:
        output_dir = Path("outputs/summaries") / runs_root.name

    from lab.reporting.auto_summary import write_auto_summary

    print(f"Runs root  : {runs_root}")
    print(f"Output dir : {output_dir}")
    print(f"Bootstrap  : {'disabled' if args.no_bootstrap else f'enabled (n={args.bootstrap_n}, seed={args.bootstrap_seed})'}")
    print()

    paths = write_auto_summary(
        runs_root,
        output_dir,
        bootstrap=not args.no_bootstrap,
        bootstrap_n=args.bootstrap_n,
        bootstrap_seed=args.bootstrap_seed,
    )

    print("Artifacts written:")
    for name, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {name:25s} {path}  ({size:,} bytes)")

    # Print warning count from warnings.json
    import json
    warnings_data = json.loads(paths["warnings_json"].read_text(encoding="utf-8"))
    n_warnings = warnings_data.get("warning_count", 0)
    if n_warnings:
        print(f"\n{n_warnings} warning(s) — see {paths['warnings_json']}")
        for w in warnings_data.get("warnings", []):
            print(f"  [{w['code']}] {w['message']}")
    else:
        print("\nNo warnings.")


if __name__ == "__main__":
    main()
