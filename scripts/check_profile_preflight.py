#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.health_checks import (  # noqa: E402
    load_config_preflight_stats,
    load_csv_preflight_stats,
    validate_profile_expectations,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate profile expectations before expensive demo execution.")
    parser.add_argument("--profile", default="demo")
    parser.add_argument("--config", required=True)
    parser.add_argument("--attack", default="fgsm")
    parser.add_argument("--csv", default="")
    parser.add_argument("--required-attack-rows", type=int, default=None)
    args = parser.parse_args()

    stats = load_config_preflight_stats(
        config_path=Path(args.config).expanduser().resolve(),
        attack_name=args.attack,
    )
    if args.csv:
        stats.update(
            load_csv_preflight_stats(
                csv_path=Path(args.csv).expanduser().resolve(),
                attack_name=args.attack,
            )
        )
    if args.required_attack_rows is not None:
        stats["required_attack_rows"] = int(args.required_attack_rows)
    stats["fgsm_required"] = True
    validate_profile_expectations(args.profile, stats)

    print(json.dumps({"status": "ok", "profile": args.profile, "stats": stats}, indent=2))


if __name__ == "__main__":
    main()
