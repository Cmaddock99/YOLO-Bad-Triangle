#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lab.health_checks import (
    assert_baseline_differs,
    assert_metrics_present,
    assert_not_all_zero_attack,
    choose_attack_name,
    filter_rows_by_session,
    latest_session_id,
    latest_rows_by_run,
    load_csv_rows,
    log_event,
    resolve_runtime_profile,
    run_fgsm_sanity_checks,
)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail if attack sweep metrics look unexpectedly unchanged."
    )
    parser.add_argument("--csv", default="outputs/metrics_summary.csv", help="Path to metrics CSV.")
    parser.add_argument(
        "--profile",
        default="strict",
        help="Run profile name used to determine default attack check target.",
    )
    parser.add_argument("--attack", default=None, help="Attack name to check (overrides profile default).")
    parser.add_argument(
        "--run-session-id",
        default=None,
        help="Optional run_session_id to isolate a single fresh run session.",
    )
    parser.add_argument(
        "--use-latest-session",
        action="store_true",
        help="Auto-select latest run_session_id from CSV when present.",
    )
    parser.add_argument(
        "--fail-on-all-zero-fgsm",
        action="store_true",
        help="Fail when all FGSM rows have approximately zero validation metrics.",
    )
    parser.add_argument(
        "--zero-epsilon",
        type=float,
        default=1e-12,
        help="Absolute tolerance used by --fail-on-all-zero-fgsm (default: 1e-12).",
    )
    parser.add_argument(
        "--allow-incomplete-sweep",
        action="store_true",
        help=(
            "Allow pass when sweep is incomplete (fewer than 2 attack rows or "
            "single attack param variant). Default-enabled for profile=week1-demo."
        ),
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Metrics CSV not found: {csv_path}")
    rows = load_csv_rows(csv_path=csv_path, require_columns=False)
    if not rows:
        raise ValueError(f"No rows found in metrics CSV: {csv_path}")

    profile_policy = resolve_runtime_profile(args.profile)
    attack_name = choose_attack_name(profile=profile_policy["name"], attack=args.attack)

    session_id = args.run_session_id
    if args.use_latest_session and not session_id:
        session_id = latest_session_id(rows)

    latest_rows = latest_rows_by_run(rows)
    scoped_rows = filter_rows_by_session(latest_rows, session_id=session_id)
    if not scoped_rows:
        raise ValueError("No rows left after applying run-session filter.")
    allow_incomplete = bool(args.allow_incomplete_sweep or profile_policy["allow_sparse_fgsm"])

    try:
        scoped_rows = run_fgsm_sanity_checks(
            rows=rows,
            attack_name=attack_name,
            session_id=session_id,
            fail_on_all_zero_attack=args.fail_on_all_zero_fgsm,
            zero_epsilon=float(args.zero_epsilon),
        )
    except ValueError as exc:
        message = str(exc)
        incomplete_sweep = (
            f"Need at least two '{attack_name}' rows" in message
            or f"Need multiple attack param variants for '{attack_name}' sweep" in message
        )
        if not (allow_incomplete and incomplete_sweep):
            raise
        assert_metrics_present(scoped_rows)
        try:
            assert_baseline_differs(scoped_rows, attack_name=attack_name)
        except ValueError as baseline_exc:
            if not profile_policy["allow_baseline_equals_attack"]:
                raise
            log_event(
                component="fgsm-sanity",
                severity="WARNING",
                message=(
                    f"Baseline-vs-{attack_name} equivalence accepted for profile={profile_policy['name']}: "
                    f"{baseline_exc}"
                ),
            )
        if args.fail_on_all_zero_fgsm:
            assert_not_all_zero_attack(
                scoped_rows,
                attack_name=attack_name,
                zero_epsilon=float(args.zero_epsilon),
            )
        log_event(
            component="fgsm-sanity",
            severity="WARNING",
            message=(
                f"Incomplete {attack_name} sweep accepted for profile={profile_policy['name']}: {message}"
            ),
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "csv": str(csv_path),
                "rows_total": len(rows),
                "rows_latest_by_run": len(latest_rows),
                "rows_checked": len(scoped_rows),
                "attack_checked": attack_name,
                "profile": profile_policy["name"],
                "profile_requested": profile_policy["requested"],
                "run_session_id": session_id or "",
            },
            indent=2,
        )
    )
    log_event(component="fgsm-sanity", severity="INFO", message="FGSM sanity PASS")


if __name__ == "__main__":
    main()
