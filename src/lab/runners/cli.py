from __future__ import annotations

import argparse
from pathlib import Path

from .experiment_runner import ExperimentRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run modular adversarial ML experiments.")
    parser.add_argument(
        "--config",
        default="configs/modular_experiments.yaml",
        help="Path to experiment YAML config.",
    )
    parser.add_argument(
        "--confs",
        default=None,
        help="Optional comma-separated confidence thresholds to override config.",
    )
    parser.add_argument(
        "--output_root",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--output-root",
        dest="output_root_dash",
        default=None,
        help="Optional override for output directory root (default: outputs/ from config).",
    )
    args = parser.parse_args()
    runner = ExperimentRunner.from_yaml(args.config)
    if args.confs:
        runner.confs = [float(part) for part in args.confs.split(",") if part.strip()]
    output_root_override = args.output_root_dash or args.output_root
    if output_root_override:
        runner.output_root = Path(output_root_override)
    runner.run()


if __name__ == "__main__":
    main()

