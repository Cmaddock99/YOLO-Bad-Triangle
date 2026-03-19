#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lab.reporting import discover_framework_runs, is_none_like, normalize_name
from lab.reporting.experiment_summary import generate_summary


def _resolve_metrics_path(path_arg: str) -> Path:
    base = Path(path_arg).expanduser().resolve()
    if base.is_dir():
        return base / "metrics.json"
    return base


def _read_metrics(path_arg: str) -> dict[str, Any]:
    metrics_path = _resolve_metrics_path(path_arg)
    if not metrics_path.is_file():
        raise FileNotFoundError(f"metrics file not found: {metrics_path}")
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"metrics payload must be a mapping: {metrics_path}")
    return payload


def _format_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.1f}%"


def _is_none_name(name: str) -> bool:
    return is_none_like(name)


def _latest_run_dirs(records: list[Any]) -> list[Any]:
    return sorted(records, key=lambda record: record.run_dir.stat().st_mtime, reverse=True)


def _manual_command_hint(baseline_dir: Path | None = None) -> str:
    baseline_arg = str(baseline_dir) if baseline_dir is not None else "<baseline_run_dir>"
    return (
        "PYTHONPATH=src python scripts/print_summary.py "
        f"--baseline {baseline_arg} --attack <attack_run_dir> [--defense <defense_run_dir>]"
    )


def _discover_auto_run_paths(runs_root: Path) -> tuple[Path, Path, Path | None]:
    records = discover_framework_runs(runs_root)
    if not records:
        raise ValueError(
            "No framework runs discovered for --auto. "
            f"Use explicit mode: {_manual_command_hint()}"
        )

    baselines = [record for record in records if _is_none_name(record.attack) and _is_none_name(record.defense)]
    if not baselines:
        raise ValueError(
            "Unable to auto-resolve baseline run (requires attack=none and defense=none). "
            f"Use explicit mode: {_manual_command_hint()}"
        )
    baseline = _latest_run_dirs(baselines)[0]

    attacks = [
        record
        for record in records
        if not _is_none_name(record.attack)
        and _is_none_name(record.defense)
        and normalize_name(record.model) == normalize_name(baseline.model)
        and record.seed == baseline.seed
    ]
    if not attacks:
        raise ValueError(
            "Unable to auto-resolve attack run matching latest baseline model/seed. "
            f"Use explicit mode: {_manual_command_hint(baseline.run_dir)}"
        )
    attack = _latest_run_dirs(attacks)[0]

    defenses = [
        record
        for record in records
        if normalize_name(record.attack) == normalize_name(attack.attack)
        and not _is_none_name(record.defense)
        and normalize_name(record.model) == normalize_name(baseline.model)
        and record.seed == baseline.seed
    ]
    defense = _latest_run_dirs(defenses)[0] if defenses else None
    return baseline.run_dir, attack.run_dir, (defense.run_dir if defense is not None else None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print derived summary from framework run metrics.")
    parser.add_argument("--baseline", help="Baseline run directory or metrics.json path.")
    parser.add_argument("--attack", help="Attack run directory or metrics.json path.")
    parser.add_argument("--defense", help="Defense run directory or metrics.json path.")
    parser.add_argument(
        "--auto",
        action="store_true",
        help=(
            "Auto-discover latest matching baseline/attack runs from framework outputs. "
            "If resolution is ambiguous/incomplete, command fails with a manual fallback hint."
        ),
    )
    parser.add_argument(
        "--runs-root",
        default="outputs/framework_runs",
        help="Framework runs root used by --auto mode.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve and print selected paths without reading metrics files.",
    )
    args = parser.parse_args()

    baseline_arg: str
    attack_arg: str
    defense_arg: str | None
    if args.auto:
        if args.baseline or args.attack or args.defense:
            parser.error("--auto cannot be combined with --baseline/--attack/--defense.")
        runs_root = Path(args.runs_root).expanduser().resolve()
        baseline_path, attack_path, defense_path = _discover_auto_run_paths(runs_root)
        baseline_arg = str(baseline_path)
        attack_arg = str(attack_path)
        defense_arg = str(defense_path) if defense_path is not None else None
        print(f"Auto baseline: {baseline_arg}")
        print(f"Auto attack: {attack_arg}")
        if defense_arg is not None:
            print(f"Auto defense: {defense_arg}")
    else:
        if not args.baseline or not args.attack:
            parser.error(
                "explicit mode requires --baseline and --attack. "
                "Or use --auto to discover runs automatically."
            )
        baseline_arg = args.baseline
        attack_arg = args.attack
        defense_arg = args.defense

    if args.dry_run:
        print(f"Resolved baseline: {baseline_arg}")
        print(f"Resolved attack:   {attack_arg}")
        if defense_arg is not None:
            print(f"Resolved defense:  {defense_arg}")
        return

    baseline_metrics = _read_metrics(baseline_arg)
    attack_metrics = _read_metrics(attack_arg)
    defense_metrics = _read_metrics(defense_arg) if defense_arg else None

    summary = generate_summary(
        baseline_metrics=baseline_metrics,
        attack_metrics=attack_metrics,
        defense_metrics=defense_metrics,
    )

    print("----------------------------------")
    print(f"Attack effectiveness: {_format_pct(summary.get('attack_effectiveness'))}")
    print(f"Defense recovery: {_format_pct(summary.get('defense_recovery'))}")
    print(f"Confidence drop: {_format_pct(summary.get('confidence_drop'))}")
    print("")
    print("Conclusion:")
    print(str(summary.get("interpretation", "Moderate robustness")))
    print("----------------------------------")


if __name__ == "__main__":
    main()
