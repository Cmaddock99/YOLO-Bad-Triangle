#!/usr/bin/env python3
"""Generate a compact HTML failure gallery from framework run artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path

from lab.reporting.local import generate_failure_gallery

generate_gallery = generate_failure_gallery


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a lightweight HTML failure gallery.")
    parser.add_argument("--runs-root", required=True, help="Directory containing framework run subdirectories.")
    parser.add_argument("--output", help="Output HTML path. Defaults to <runs-root>/../failure_gallery.html.")
    parser.add_argument("--max-images", type=int, default=20, help="Maximum ranked images per section.")
    args = parser.parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else (runs_root.parent / "failure_gallery.html").resolve()
    )
    written = generate_failure_gallery(
        runs_root=runs_root,
        output_path=output_path,
        max_images=max(1, int(args.max_images)),
    )
    print(f"Failure gallery: {written}")


if __name__ == "__main__":
    main()
