#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners import ExperimentRunner


def main() -> None:
    runner = ExperimentRunner.from_yaml(ROOT / "configs" / "baseline_blur_compat.yaml")
    runner.run()
    print("\nAll experiments completed successfully.")


if __name__ == "__main__":
    main()