#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm


DEFAULT_ATTACKS = ("bim", "blur", "deepfool", "fgsm", "gaussian_blur", "ifgsm", "pgd")
DEFAULT_DEFENSES = ("median_preprocess",)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_command(command: list[str], *, dry_run: bool) -> None:
    rendered = " ".join(shlex.quote(part) for part in command)
    print(f"$ {rendered}")
    if dry_run:
        return
    subprocess.run(command, check=True)


def _metrics_exists(run_dir: Path) -> bool:
    return (run_dir / "metrics.json").is_file()


def _parse_csv_list(raw: str, label: str) -> list[str]:
    items = [part.strip() for part in raw.split(",") if part.strip()]
    if not items:
        raise ValueError(f"Expected at least one {label} in --{label}s.")
    return items


def _parse_attacks(raw: str) -> list[str]:
    return _parse_csv_list(raw, "attack")


def _parse_defenses(raw: str) -> list[str]:
    return _parse_csv_list(raw, "defense")


def _experiment_command(
    *,
    python_bin: str,
    config: Path,
    output_root: Path,
    run_name: str,
    attack_name: str,
    defense_name: str,
    seed: int,
    max_images: int,
    validation_enabled: bool,
) -> list[str]:
    return [
        python_bin,
        "src/lab/runners/run_experiment.py",
        "--config",
        str(config),
        "--set",
        f"runner.output_root={output_root}",
        "--set",
        f"runner.run_name={run_name}",
        "--set",
        f"runner.seed={seed}",
        "--set",
        f"runner.max_images={max_images}",
        "--set",
        f"attack.name={attack_name}",
        "--set",
        f"defense.name={defense_name}",
        "--set",
        f"validation.enabled={str(validation_enabled).lower()}",
        "--set",
        "summary.enabled=false",
    ]


def _print_summary_command(
    *,
    python_bin: str,
    baseline_dir: Path,
    attack_dir: Path,
) -> list[str]:
    return [
        python_bin,
        "scripts/print_summary.py",
        "--baseline",
        str(baseline_dir),
        "--attack",
        str(attack_dir),
    ]


def _generate_framework_report_command(
    *,
    python_bin: str,
    runs_root: Path,
    output_dir: Path,
) -> list[str]:
    return [
        python_bin,
        "scripts/generate_framework_report.py",
        "--runs-root",
        str(runs_root),
        "--output-dir",
        str(output_dir),
    ]


def _generate_team_summary_command(
    *,
    python_bin: str,
    report_root: Path,
) -> list[str]:
    return [
        python_bin,
        "scripts/generate_team_summary.py",
        "--report-root",
        str(report_root),
    ]


def _default_max_images(preset: str) -> int:
    if preset == "full":
        return 0
    return 8


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run baseline + attack sweep (+ optional defense sweep) and generate reports."
    )
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--python-bin", default="./.venv/bin/python")
    parser.add_argument("--runs-root", help="Optional output root for framework runs.")
    parser.add_argument("--report-root", help="Optional output root for report artifacts.")
    parser.add_argument("--attacks", default=",".join(DEFAULT_ATTACKS))
    parser.add_argument(
        "--defenses",
        default=",".join(DEFAULT_DEFENSES),
        help="Comma-separated defenses to sweep against each attack. "
             "Set to 'none' to skip the defense sweep entirely.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-images", type=int)
    parser.add_argument("--baseline-run-name", default="baseline_none")
    parser.add_argument(
        "--preset",
        choices=("smoke", "full"),
        default="smoke",
        help="smoke=fast sanity defaults, full=all images by default.",
    )
    parser.add_argument("--validation-enabled", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Skip runs that already have metrics.json.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing.")
    parser.add_argument(
        "--team-summary",
        dest="team_summary",
        action="store_true",
        help="Generate team_summary.json and team_summary.md after aggregate report.",
    )
    parser.add_argument(
        "--no-team-summary",
        dest="team_summary",
        action="store_false",
    )
    parser.set_defaults(team_summary=True)
    try:
        args = parser.parse_args()

        runs_root = (
            Path(args.runs_root).expanduser().resolve()
            if args.runs_root
            else Path(f"outputs/framework_runs/sweep_{_timestamp()}").resolve()
        )
        report_root = (
            Path(args.report_root).expanduser().resolve()
            if args.report_root
            else Path(f"outputs/framework_reports/{runs_root.name}").resolve()
        )
        config = Path(args.config).expanduser().resolve()
        if not config.is_file():
            raise FileNotFoundError(f"Config not found: {config}")
        python_bin_path = Path(args.python_bin).expanduser()
        if not python_bin_path.is_file():
            raise FileNotFoundError(f"Python binary not found: {python_bin_path}")

        max_images = args.max_images if args.max_images is not None else _default_max_images(args.preset)
        attacks = _parse_attacks(args.attacks)
        raw_defenses = _parse_defenses(args.defenses)
        defenses = [d for d in raw_defenses if d.lower() != "none"]

        runs_root.mkdir(parents=True, exist_ok=True)
        report_root.mkdir(parents=True, exist_ok=True)
        print(f"Runs root:    {runs_root}")
        print(f"Reports root: {report_root}")
        print(f"Attacks:      {attacks}")
        if defenses:
            print(f"Defenses:     {defenses}")

        # --- Phase 1: Baseline ---
        baseline_dir = runs_root / args.baseline_run_name
        if not (args.resume and _metrics_exists(baseline_dir)):
            _run_command(
                _experiment_command(
                    python_bin=args.python_bin,
                    config=config,
                    output_root=runs_root,
                    run_name=args.baseline_run_name,
                    attack_name="none",
                    defense_name="none",
                    seed=args.seed,
                    max_images=max_images,
                    validation_enabled=args.validation_enabled,
                ),
                dry_run=args.dry_run,
            )
        else:
            print(f"Resume: skipping baseline ({baseline_dir})")

        # --- Phase 2: Attack sweep ---
        for attack in tqdm(attacks, desc="Phase 2: attack sweep", unit="attack", dynamic_ncols=True):
            attack_run_name = f"attack_{attack}"
            attack_dir = runs_root / attack_run_name
            if not (args.resume and _metrics_exists(attack_dir)):
                _run_command(
                    _experiment_command(
                        python_bin=args.python_bin,
                        config=config,
                        output_root=runs_root,
                        run_name=attack_run_name,
                        attack_name=attack,
                        defense_name="none",
                        seed=args.seed,
                        max_images=max_images,
                        validation_enabled=args.validation_enabled,
                    ),
                    dry_run=args.dry_run,
                )
            else:
                print(f"Resume: skipping attack run ({attack_dir})")

            summary_command = _print_summary_command(
                python_bin=args.python_bin,
                baseline_dir=baseline_dir,
                attack_dir=attack_dir,
            )
            summary_out = report_root / f"summary_{attack}.txt"
            rendered = " ".join(shlex.quote(part) for part in summary_command)
            print(f"$ {rendered} > {shlex.quote(str(summary_out))}")
            if not args.dry_run:
                with summary_out.open("w", encoding="utf-8") as handle:
                    subprocess.run(summary_command, check=True, stdout=handle)

        # --- Phase 3: Defense sweep ---
        defense_pairs = [(a, d) for a in attacks for d in defenses]
        for attack, defense in tqdm(defense_pairs, desc="Phase 3: defense sweep", unit="run", dynamic_ncols=True):
            defended_run_name = f"defended_{attack}_{defense}"
            defended_dir = runs_root / defended_run_name
            if not (args.resume and _metrics_exists(defended_dir)):
                _run_command(
                    _experiment_command(
                        python_bin=args.python_bin,
                        config=config,
                        output_root=runs_root,
                        run_name=defended_run_name,
                        attack_name=attack,
                        defense_name=defense,
                        seed=args.seed,
                        max_images=max_images,
                        validation_enabled=args.validation_enabled,
                    ),
                    dry_run=args.dry_run,
                )
            else:
                print(f"Resume: skipping defended run ({defended_dir})")

        # --- Phase 4: Reports ---
        _run_command(
            _generate_framework_report_command(
                python_bin=args.python_bin,
                runs_root=runs_root,
                output_dir=report_root,
            ),
            dry_run=args.dry_run,
        )
        if args.team_summary:
            _run_command(
                _generate_team_summary_command(
                    python_bin=args.python_bin,
                    report_root=report_root,
                ),
                dry_run=args.dry_run,
            )

        print("")
        print("Done.")
        print(f"Per-attack summaries: {report_root}/summary_*.txt")
        print(f"Aggregate CSV:        {report_root}/framework_run_summary.csv")
        print(f"Aggregate Markdown:   {report_root}/framework_run_report.md")
        if args.team_summary:
            print(f"Team JSON summary:    {report_root}/team_summary.json")
            print(f"Team MD summary:      {report_root}/team_summary.md")
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
