#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from lab.health_checks import (
    log_event,
    resolve_latest_dir,
    resolve_latest_framework_run,
    resolve_latest_shadow_run_dir,
    run_and_require_success,
)
from lab.migration import update_migration_cycle_tracker


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all framework-first migration CI gates.")
    parser.add_argument("--parity-config", default="configs/parity_test.yaml")
    parser.add_argument("--demo-profile", default="demo")
    parser.add_argument("--demo-output-root", default="outputs/demo-gate-ci")
    parser.add_argument("--schema-framework-runs-root", default="")
    parser.add_argument("--schema-legacy-csv", default="")
    parser.add_argument("--health-output-root", default="outputs/system_health")
    parser.add_argument("--cycle-name", default="")
    parser.add_argument("--ci-log", default="outputs/migration_state/ci_gate_log.jsonl")
    parser.add_argument("--gate-summary-output", default="outputs/migration_state/gate_summary.json")
    parser.add_argument(
        "--allow-missing-baseline",
        action="store_true",
        help="Allow first-run bootstrap when baseline_report_latest.json is missing.",
    )
    args = parser.parse_args()

    gate_results: dict[str, bool] = {
        "legacy_policy_guard": False,
        "legacy_usage_enforcement": False,
        "schema_change_guard": False,
        "operator_docs_enforcement": False,
        "framework_boundary_enforcement": False,
        "framework_duplication_ast_enforcement": False,
        "contract_ownership": False,
        "parity": False,
        "demo": False,
        "artifact": False,
        "schema": False,
        "system_health": False,
        "observability_contract": False,
    }
    required_gate_order = ["parity", "demo", "artifact", "schema", "system_health"]
    executed_gate_order: list[str] = []
    gate_records: list[dict[str, object]] = []
    correlation_id = os.environ.get("MIGRATION_CORRELATION_ID", str(uuid4()))
    gate_env = {"MIGRATION_CORRELATION_ID": correlation_id}
    demo_output_root = Path(args.demo_output_root).expanduser().resolve()
    gate_error: Exception | None = None
    try:
        run_and_require_success(
            name="legacy_policy_guard",
            command=[sys.executable, str(ROOT / "scripts/ci/check_legacy_policy_branch_guard.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["legacy_policy_guard"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "legacy_policy_guard",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_legacy_policy_branch_guard.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="legacy_usage_enforcement",
            command=[sys.executable, str(ROOT / "scripts/ci/check_legacy_usage_enforcement.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["legacy_usage_enforcement"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "legacy_usage_enforcement",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_legacy_usage_enforcement.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="schema_change_guard",
            command=[sys.executable, str(ROOT / "scripts/ci/check_schema_change_guard.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["schema_change_guard"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "schema_change_guard",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_schema_change_guard.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="operator_docs_enforcement",
            command=[sys.executable, str(ROOT / "scripts/ci/check_operator_docs.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["operator_docs_enforcement"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "operator_docs_enforcement",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_operator_docs.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="framework_boundary_enforcement",
            command=[sys.executable, str(ROOT / "scripts/ci/check_framework_boundaries.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["framework_boundary_enforcement"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "framework_boundary_enforcement",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_framework_boundaries.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="framework_duplication_ast_enforcement",
            command=[sys.executable, str(ROOT / "scripts/ci/check_framework_duplication_ast.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["framework_duplication_ast_enforcement"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "framework_duplication_ast_enforcement",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_framework_duplication_ast.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="contract_ownership",
            command=[sys.executable, str(ROOT / "scripts/ci/check_contract_ownership.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["contract_ownership"] = True
        run_and_require_success(
            name="parity",
            command=[
                sys.executable,
                str(ROOT / "scripts/ci/check_parity_gate.py"),
                "--config",
                str(Path(args.parity_config).expanduser().resolve()),
            ],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["parity"] = True
        executed_gate_order.append("parity")
        gate_records.append(
            {
                "status": "PASS",
                "stage": "parity",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_parity_gate.py --config {args.parity_config}"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="demo",
            command=[
                sys.executable,
                str(ROOT / "scripts/ci/check_demo_gate.py"),
                "--profile",
                args.demo_profile,
                "--output-root",
                str(demo_output_root),
            ],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["demo"] = True
        executed_gate_order.append("demo")
        gate_records.append(
            {
                "status": "PASS",
                "stage": "demo",
                "issues": [],
                "commands": [
                    f"{sys.executable} scripts/ci/check_demo_gate.py --profile {args.demo_profile} --output-root {demo_output_root}"
                ],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="artifact",
            command=[
                sys.executable,
                str(ROOT / "scripts/ci/check_artifact_gate.py"),
                "--output-root",
                str(demo_output_root),
            ],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["artifact"] = True
        executed_gate_order.append("artifact")
        gate_records.append(
            {
                "status": "PASS",
                "stage": "artifact",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_artifact_gate.py --output-root {demo_output_root}"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        if args.schema_framework_runs_root:
            runs_root = Path(args.schema_framework_runs_root).expanduser().resolve()
            latest_framework_run = resolve_latest_framework_run(runs_root)
        else:
            shadow_latest = resolve_latest_shadow_run_dir(ROOT / "outputs" / "shadow_parity")
            latest_framework_run = resolve_latest_dir(
                shadow_latest / "framework",
                description="framework run directories",
            )
        legacy_csv = (
            Path(args.schema_legacy_csv).expanduser().resolve()
            if args.schema_legacy_csv
            else demo_output_root / "metrics_summary.csv"
        )
        run_and_require_success(
            name="schema",
            command=[
                sys.executable,
                str(ROOT / "scripts/ci/validate_output_schemas.py"),
                "--framework-run-dir",
                str(latest_framework_run),
                "--legacy-compat-csv",
                str(legacy_csv),
            ],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["schema"] = True
        executed_gate_order.append("schema")
        gate_records.append(
            {
                "status": "PASS",
                "stage": "schema",
                "issues": [],
                "commands": [
                    f"{sys.executable} scripts/ci/validate_output_schemas.py --framework-run-dir {latest_framework_run} --legacy-compat-csv {legacy_csv}"
                ],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        health_command = [
            sys.executable,
            str(ROOT / "run_system_health_check.py"),
            "--parity-config",
            str(Path(args.parity_config).expanduser().resolve()),
            "--demo-profile",
            args.demo_profile,
            "--demo-output-root",
            str(demo_output_root),
            "--health-output-root",
            str(Path(args.health_output_root).expanduser().resolve()),
        ]
        if args.allow_missing_baseline:
            health_command.append("--allow-missing-baseline")
        run_and_require_success(
            name="system_health",
            command=health_command,
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["system_health"] = True
        executed_gate_order.append("system_health")
        gate_records.append(
            {
                "status": "PASS",
                "stage": "system_health",
                "issues": [],
                "commands": [" ".join(health_command)],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        run_and_require_success(
            name="observability_contract",
            command=[
                sys.executable,
                str(ROOT / "scripts/migration_status.py"),
                "--health-summary",
                str(Path(args.health_output_root).expanduser().resolve() / "system_health_summary.json"),
                "--snapshot-output",
                str(ROOT / "outputs/migration_state/migration_status_snapshot.json"),
            ],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        run_and_require_success(
            name="observability_contract",
            command=[sys.executable, str(ROOT / "scripts/ci/check_observability_contract.py")],
            cwd=ROOT,
            component="migration-gates",
            extra_env=gate_env,
        )
        gate_results["observability_contract"] = True
        gate_records.append(
            {
                "status": "PASS",
                "stage": "observability_contract",
                "issues": [],
                "commands": [f"{sys.executable} scripts/ci/check_observability_contract.py"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        if executed_gate_order != required_gate_order:
            raise RuntimeError(
                f"Gate order violation: expected {required_gate_order}, got {executed_gate_order}"
            )
    except Exception as exc:
        gate_error = exc
        gate_records.append(
            {
                "status": "FAIL",
                "stage": "migration_gates",
                "issues": [str(exc)],
                "commands": [],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        log_event(
            component="migration-gates",
            severity="ERROR",
            message=f"Gate execution halted: {exc}",
        )
        # Continue to tracker/log update, then re-raise.
        pass
    all_pass = all(gate_results.values())
    cycle_name = args.cycle_name or datetime.now(timezone.utc).strftime("ci_cycle_%Y%m%dT%H%M%SZ")
    cycle_state = update_migration_cycle_tracker(
        cycle_name=cycle_name,
        gate_results={
            "contract_ownership": gate_results["contract_ownership"],
            "parity": gate_results["parity"],
            "demo": gate_results["demo"],
            "artifact": gate_results["artifact"],
            "schema": gate_results["schema"],
            "system_health": gate_results["system_health"],
        },
    )
    log_path = Path(args.ci_log).expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "cycle_name": cycle_name,
                    "correlation_id": correlation_id,
                    "status": "PASS" if all_pass else "FAIL",
                    "gate_results": gate_results,
                    "gate_order": executed_gate_order,
                    "consecutive_full_passes": cycle_state.consecutive_full_passes,
                    "legacy_status": cycle_state.legacy_status,
                }
            )
            + "\n"
        )
    gate_summary_path = Path(args.gate_summary_output).expanduser().resolve()
    gate_summary_path.parent.mkdir(parents=True, exist_ok=True)
    gate_summary_path.write_text(
        json.dumps(
            {
                "status": "PASS" if all_pass else "FAIL",
                "stage": "migration_gates",
                "issues": [] if all_pass else [str(gate_error) if gate_error else "unknown gate failure"],
                "commands": [record.get("commands", []) for record in gate_records],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id,
                "gate_order_expected": required_gate_order,
                "gate_order_executed": executed_gate_order,
                "gate_results": gate_results,
                "records": gate_records,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    if all_pass:
        log_event(component="migration-gates", severity="INFO", message="All migration gates PASS")
    else:
        log_event(
            component="migration-gates",
            severity="ERROR",
            message=f"Migration gates FAIL: {gate_results}",
        )
    log_event(
        component="migration-gates",
        severity="INFO",
        message=(
            f"Cycle tracker updated: consecutive_full_passes={cycle_state.consecutive_full_passes} "
            f"legacy_status={cycle_state.legacy_status}"
        ),
    )
    if not all_pass:
        if gate_error is not None:
            raise RuntimeError(f"One or more migration gates failed: {gate_results}") from gate_error
        raise RuntimeError(f"One or more migration gates failed: {gate_results}")


if __name__ == "__main__":
    main()
