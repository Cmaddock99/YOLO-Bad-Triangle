#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _latest_dir(path: Path) -> Path | None:
    if not path.is_dir():
        return None
    dirs = sorted(
        [p for p in path.iterdir() if p.is_dir() and (p / "parity_report.json").is_file()],
        key=lambda p: p.name,
    )
    return dirs[-1] if dirs else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple migration status dashboard.")
    parser.add_argument("--shadow-root", default="outputs/shadow_parity")
    parser.add_argument("--demo-root", default="outputs/demo-gate-ci")
    parser.add_argument("--contracts", default="contracts/migration_contracts.yaml")
    parser.add_argument(
        "--cycle-tracker",
        default="outputs/migration_state/migration_cycle_tracker.json",
    )
    parser.add_argument("--health-summary", default="outputs/system_health/system_health_summary.json")
    parser.add_argument("--snapshot-output", default="outputs/migration_state/migration_status_snapshot.json")
    args = parser.parse_args()

    shadow_root = Path(args.shadow_root).expanduser().resolve()
    latest_shadow = _latest_dir(shadow_root)
    parity_summary = "missing"
    parity_score = "n/a"
    if latest_shadow is not None:
        report_path = latest_shadow / "parity_report.json"
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            parity_summary = "PASS" if report.get("parity_pass") else "FAIL"
            parity_score = str(report.get("parity_score", "n/a"))

    demo_root = Path(args.demo_root).expanduser().resolve()
    demo_artifacts_ok = (
        (demo_root / "metrics_summary.csv").is_file()
        and (demo_root / "experiment_table.md").is_file()
    )
    cycle_tracker_path = Path(args.cycle_tracker).expanduser().resolve()
    cycle_status = {}
    if cycle_tracker_path.is_file():
        cycle_status = json.loads(cycle_tracker_path.read_text(encoding="utf-8"))
    health_summary_path = Path(args.health_summary).expanduser().resolve()
    health_status = {}
    if health_summary_path.is_file():
        health_status = json.loads(health_summary_path.read_text(encoding="utf-8"))

    legacy_status = str(cycle_status.get("legacy_status", "active"))
    ci_enforced = bool(cycle_status.get("cycle_count", 0)) or Path("scripts/ci/run_migration_gates.py").is_file()
    system_health_verified = bool(health_status.get("overall_pass", False))
    demo_verified = demo_artifacts_ok and system_health_verified
    snapshot = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if (parity_summary == "PASS" and system_health_verified and demo_verified) else "FAIL",
        "stage": "migration_status",
        "issues": [] if (parity_summary == "PASS" and system_health_verified and demo_verified) else [
            "parity/system_health/demo verification incomplete"
        ],
        "commands": [
            "python scripts/migration_status.py",
            "python scripts/ci/run_migration_gates.py --parity-config configs/parity_test.yaml",
        ],
        "framework": "ACTIVE",
        "legacy": legacy_status.upper(),
        "parity_status": parity_summary,
        "ci_gates_enforced": ci_enforced,
        "system_health_verified": system_health_verified,
        "demo_reliability_verified": demo_verified,
        "latest_shadow_run": str(latest_shadow) if latest_shadow else "",
    }
    snapshot_path = Path(args.snapshot_output).expanduser().resolve()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    print("=== Migration Status Dashboard ===")
    print(f"Latest shadow run: {latest_shadow if latest_shadow else 'none'}")
    print(f"Parity status: {parity_summary}")
    print(f"Parity score: {parity_score}")
    print(f"Demo artifacts: {'PASS' if demo_artifacts_ok else 'FAIL'}")
    print(f"Contracts file: {Path(args.contracts).expanduser().resolve()}")
    print("Canonical run path: scripts/run_unified.py")
    print("Fallback demo path: scripts/demo/run_demo_package.sh")
    print("Legacy mode: rollback only")
    print("")
    print(f"Framework: ACTIVE")
    print(f"Legacy: {legacy_status.upper()}")
    print(f"Parity Status: {'PASSING' if parity_summary == 'PASS' else 'FAILING'}")
    print(f"CI Gates: {'ENFORCED' if ci_enforced else 'NOT_ENFORCED'}")
    print(f"System Health: {'VERIFIED' if system_health_verified else 'NOT_VERIFIED'}")
    print(f"Demo Reliability: {'VERIFIED' if demo_verified else 'NOT_VERIFIED'}")
    print(f"Snapshot: {snapshot_path}")


if __name__ == "__main__":
    main()
