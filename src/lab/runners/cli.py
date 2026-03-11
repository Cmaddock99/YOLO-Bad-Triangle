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
        help="Optional override for output directory root.",
    )
    args = parser.parse_args()

    runner = ExperimentRunner.from_yaml(args.config)
    if args.confs:
        runner.confs = [float(part) for part in args.confs.split(",") if part.strip()]
    if args.output_root:
        runner.output_root = Path(args.output_root)
    runner.run()


if __name__ == "__main__":
    main()

