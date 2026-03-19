#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.runners.cli import main


if __name__ == "__main__":
    print(
        "DEPRECATION NOTICE: 'scripts/run_framework.py' is a legacy batch compatibility wrapper. "
        "Prefer framework runner: 'src/lab/runners/run_experiment.py'."
    )
    main()

