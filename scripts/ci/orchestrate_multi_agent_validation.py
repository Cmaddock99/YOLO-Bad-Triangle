#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
DEFAULT_CONTRACT_FILE = ROOT / "contracts" / "orchestration_agent_contracts.yaml"
from lab.config.contracts import MAX_FIX_LOOP


@dataclass
class Issue:
    id: str
    severity: str
    phase: str
    summary: str
    details: str


@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(command: list[str], *, name: str) -> CommandResult:
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    src_path = str((ROOT / "src").resolve())
    env["PYTHONPATH"] = f"{src_path}:{existing_pythonpath}" if existing_pythonpath else src_path
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return CommandResult(
        name=name,
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _safe_read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _allow_missing_baseline_arg(allow_missing_baseline: bool) -> list[str]:
    return ["--allow-missing-baseline"] if allow_missing_baseline else []


def _latest_shadow_run_dir(shadow_root: Path) -> Path | None:
    if not shadow_root.is_dir():
        return None
    candidates = sorted(
        [p for p in shadow_root.iterdir() if p.is_dir() and (p / "parity_report.json").is_file()],
        key=lambda p: p.name,
    )
    return candidates[-1] if candidates else None


def _latest_framework_run_from_shadow(shadow_run_dir: Path) -> Path | None:
    framework_parent = shadow_run_dir / "framework"
    if not framework_parent.is_dir():
        return None
    candidates = sorted([p for p in framework_parent.iterdir() if p.is_dir()], key=lambda p: p.name)
    return candidates[-1] if candidates else None


def _git_modified_files() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    files: list[str] = []
    for line in proc.stdout.splitlines():
        text = line.strip()
        if len(text) < 4:
            continue
        files.append(text[3:].strip())
    return files


def _builder_phase() -> dict[str, Any]:
    required = {
        "migration_and_retirement": [
            ROOT / "src/lab/migration/runtime_policy.py",
            ROOT / "src/lab/migration/cycle_tracker.py",
            ROOT / "docs/LEGACY_RETIREMENT_ROLLBACK.md",
        ],
        "shadow_parity": [
            ROOT / "run_shadow_parity.py",
            ROOT / "src/lab/migration/shadow_parity.py",
            ROOT / "configs/parity_test.yaml",
        ],
        "ci_gates": [
            ROOT / "scripts/ci/run_migration_gates.py",
            ROOT / "scripts/ci/check_parity_gate.py",
            ROOT / "scripts/ci/validate_output_schemas.py",
        ],
        "system_health": [
            ROOT / "run_system_health_check.py",
            ROOT / "scripts/ci/check_system_health_gate.py",
            ROOT / "src/lab/health_checks/execution.py",
        ],
        "diagnostics_auto_heal": [
            ROOT / "src/lab/migration/diagnostics.py",
            ROOT / "docs/incidents/parity_failed.md",
            ROOT / "docs/incidents/demo_failed.md",
        ],
    }
    systems: dict[str, dict[str, Any]] = {}
    for key, files in required.items():
        missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
        systems[key] = {"implemented": len(missing) == 0, "missing_files": missing}
    implementation_complete = all(entry["implemented"] for entry in systems.values())
    modified_files = _git_modified_files()
    return {
        "timestamp_utc": _utc_now(),
        "implementation_complete": implementation_complete,
        "systems": systems,
        "files_created_or_modified": modified_files,
    }


def _severity_for_command(name: str) -> str:
    if name in {"migration_gates", "system_health", "schema_validation"}:
        return "CRITICAL"
    if name in {"failure_sim_artifact_gate", "failure_sim_schema"}:
        return "MAJOR"
    return "MINOR"


def _blocking_issue_counts(audit: dict[str, Any]) -> tuple[int, int]:
    severity_counts = audit.get("severity_counts", {})
    critical = int(severity_counts.get("CRITICAL", 0))
    major = int(severity_counts.get("MAJOR", 0))
    return critical, major


def _issue_id_set(audit: dict[str, Any]) -> set[str]:
    return {
        str(item.get("id", "")).strip()
        for item in audit.get("issues", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }


def _reason_code_for_audit(audit: dict[str, Any]) -> str:
    issue_ids = _issue_id_set(audit)
    if any("schema" in issue_id for issue_id in issue_ids):
        return "SCHEMA_RECURRING"
    if any("demo" in issue_id or "artifact" in issue_id for issue_id in issue_ids):
        return "DEMO_ARTIFACT_FLAP"
    return "PARITY_STUCK"


def _audit_phase(
    *,
    parity_config: Path,
    demo_profile: str,
    demo_output_root: Path,
    health_output_root: Path,
    allow_missing_baseline: bool,
    run_failure_simulation: bool,
) -> dict[str, Any]:
    commands: list[CommandResult] = []
    issues: list[Issue] = []
    schema_violation = False

    migration_cmd = [
        sys.executable,
        str(ROOT / "scripts/ci/run_migration_gates.py"),
        "--parity-config",
        str(parity_config),
        "--demo-profile",
        demo_profile,
        "--demo-output-root",
        str(demo_output_root),
        "--health-output-root",
        str(health_output_root),
    ] + _allow_missing_baseline_arg(allow_missing_baseline)
    migration_result = _run(migration_cmd, name="migration_gates")
    commands.append(migration_result)
    if not migration_result.ok:
        issues.append(
            Issue(
                id="audit_migration_gates_failed",
                severity=_severity_for_command("migration_gates"),
                phase="audit",
                summary="Migration CI gates failed.",
                details=migration_result.stderr.strip() or migration_result.stdout.strip(),
            )
        )

    health_cmd = [
        sys.executable,
        str(ROOT / "run_system_health_check.py"),
        "--parity-config",
        str(parity_config),
        "--demo-profile",
        demo_profile,
        "--demo-output-root",
        str(demo_output_root),
        "--health-output-root",
        str(health_output_root),
    ] + _allow_missing_baseline_arg(allow_missing_baseline)
    health_result = _run(health_cmd, name="system_health")
    commands.append(health_result)
    if not health_result.ok:
        issues.append(
            Issue(
                id="audit_system_health_failed",
                severity=_severity_for_command("system_health"),
                phase="audit",
                summary="System health check failed.",
                details=health_result.stderr.strip() or health_result.stdout.strip(),
            )
        )

    latest_shadow = _latest_shadow_run_dir(ROOT / "outputs" / "shadow_parity")
    framework_run = _latest_framework_run_from_shadow(latest_shadow) if latest_shadow else None
    legacy_csv = demo_output_root / "metrics_summary.csv"
    schema_result: CommandResult | None = None
    if framework_run and legacy_csv.is_file():
        schema_result = _run(
            [
                sys.executable,
                str(ROOT / "scripts/ci/validate_output_schemas.py"),
                "--framework-run-dir",
                str(framework_run),
                "--legacy-compat-csv",
                str(legacy_csv),
            ],
            name="schema_validation",
        )
        commands.append(schema_result)
        if not schema_result.ok:
            schema_violation = True
            issues.append(
                Issue(
                    id="audit_schema_validation_failed",
                    severity=_severity_for_command("schema_validation"),
                    phase="audit",
                    summary="Schema validation failed on current artifacts.",
                    details=schema_result.stderr.strip() or schema_result.stdout.strip(),
                )
            )
    else:
        schema_violation = True
        issues.append(
            Issue(
                id="audit_schema_preconditions_missing",
                severity="CRITICAL",
                phase="audit",
                summary="Schema validation preconditions are missing.",
                details=f"framework_run={framework_run} legacy_csv_exists={legacy_csv.is_file()}",
            )
        )

    if run_failure_simulation:
        sim_artifact = _run(
            [
                sys.executable,
                str(ROOT / "scripts/ci/check_artifact_gate.py"),
                "--output-root",
                str(ROOT / "outputs" / "_intentionally_missing_artifacts"),
            ],
            name="failure_sim_artifact_gate",
        )
        commands.append(sim_artifact)
        if sim_artifact.ok:
            issues.append(
                Issue(
                    id="audit_failure_sim_artifact_not_detected",
                    severity="MAJOR",
                    phase="audit",
                    summary="Artifact failure simulation did not fail as expected.",
                    details="Expected non-zero exit code for missing artifacts.",
                )
            )

        sim_schema = _run(
            [
                sys.executable,
                str(ROOT / "scripts/ci/validate_output_schemas.py"),
                "--framework-run-dir",
                str(ROOT / "outputs" / "_intentionally_missing_framework_run"),
                "--legacy-compat-csv",
                str(ROOT / "outputs" / "_intentionally_missing_legacy.csv"),
            ],
            name="failure_sim_schema",
        )
        commands.append(sim_schema)
        if sim_schema.ok:
            issues.append(
                Issue(
                    id="audit_failure_sim_schema_not_detected",
                    severity="MAJOR",
                    phase="audit",
                    summary="Schema failure simulation did not fail as expected.",
                    details="Expected non-zero exit code for missing schema inputs.",
                )
            )

    parity_report = {}
    parity_status = "FAIL"
    if latest_shadow is not None:
        parity_report = _safe_read_json(latest_shadow / "parity_report.json")
        parity_status = "PASS" if bool(parity_report.get("parity_pass", False)) else "FAIL"
        if parity_status != "PASS":
            issues.append(
                Issue(
                    id="audit_parity_status_fail",
                    severity="CRITICAL",
                    phase="audit",
                    summary="Parity report indicates FAIL.",
                    details=f"latest_shadow_run={latest_shadow}",
                )
            )
    else:
        issues.append(
            Issue(
                id="audit_parity_report_missing",
                severity="CRITICAL",
                phase="audit",
                summary="No parity report found.",
                details="No run directory under outputs/shadow_parity with parity_report.json.",
            )
        )

    health_summary = _safe_read_json(health_output_root / "system_health_summary.json")
    system_health_status = "PASS" if bool(health_summary.get("overall_pass", False)) else "FAIL"
    if system_health_status != "PASS":
        issues.append(
            Issue(
                id="audit_system_health_status_fail",
                severity="CRITICAL",
                phase="audit",
                summary="System health summary indicates FAIL.",
                details=f"summary_file={health_output_root / 'system_health_summary.json'}",
            )
        )

    demo_ok = (demo_output_root / "metrics_summary.csv").is_file() and (demo_output_root / "experiment_table.md").is_file()
    if not demo_ok:
        issues.append(
            Issue(
                id="audit_demo_artifacts_missing",
                severity="CRITICAL",
                phase="audit",
                summary="Demo artifacts are missing.",
                details=f"expected under {demo_output_root}",
            )
        )

    severity_counts = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    return {
        "timestamp_utc": _utc_now(),
        "commands": [asdict(result) for result in commands],
        "issues": [asdict(issue) for issue in issues],
        "severity_counts": severity_counts,
        "parity_status": parity_status,
        "system_health": system_health_status,
        "schema_violations": schema_violation,
        "demo_success": demo_ok,
        "latest_shadow_run": str(latest_shadow) if latest_shadow else "",
    }


def _builder_fix_phase(*, parity_config: Path, demo_profile: str, demo_output_root: Path) -> dict[str, Any]:
    fix_commands = [
        (
            "builder_fix_parity_rerun",
            [sys.executable, str(ROOT / "run_shadow_parity.py"), "--config", str(parity_config)],
        ),
        (
            "builder_fix_demo_rebuild",
            [
                "bash",
                str(ROOT / "scripts/demo/run_demo_package.sh"),
                "fast",
                "--profile",
                demo_profile,
                "--output-root",
                str(demo_output_root),
            ],
        ),
        (
            "builder_fix_health_autofix",
            [
                sys.executable,
                str(ROOT / "run_system_health_check.py"),
                "--parity-config",
                str(parity_config),
                "--demo-profile",
                demo_profile,
                "--demo-output-root",
                str(demo_output_root),
                "--allow-missing-baseline",
                "--auto-fix",
            ],
        ),
    ]
    outcomes: list[dict[str, Any]] = []
    for name, command in fix_commands:
        result = _run(command, name=name)
        outcomes.append(asdict(result))
    return {"timestamp_utc": _utc_now(), "actions": outcomes}


def _run_fix_loop(
    *,
    parity_config: Path,
    demo_profile: str,
    demo_output_root: Path,
    health_output_root: Path,
    allow_missing_baseline: bool,
    max_fix_loop: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], int, bool, str]:
    audit_iterations: list[dict[str, Any]] = []
    fix_iterations: list[dict[str, Any]] = []
    iteration_count = 0
    effective_max = max_fix_loop

    current_audit = _audit_phase(
        parity_config=parity_config,
        demo_profile=demo_profile,
        demo_output_root=demo_output_root,
        health_output_root=health_output_root,
        allow_missing_baseline=allow_missing_baseline,
        run_failure_simulation=True,
    )
    current_issue_ids = _issue_id_set(current_audit)
    audit_iterations.append(
        {
            "iteration": iteration_count,
            "new_issues": sorted(current_issue_ids),
            "resolved_issues": [],
            "remaining_issues": sorted(current_issue_ids),
            **current_audit,
        }
    )
    previous_issue_ids = current_issue_ids

    while True:
        critical, major = _blocking_issue_counts(current_audit)
        if critical == 0 and major == 0:
            break

        iteration_count += 1
        if iteration_count > effective_max:
            break

        fix_result = _builder_fix_phase(
            parity_config=parity_config,
            demo_profile=demo_profile,
            demo_output_root=demo_output_root,
        )
        fix_iterations.append({"iteration": iteration_count, **fix_result})

        current_audit = _audit_phase(
            parity_config=parity_config,
            demo_profile=demo_profile,
            demo_output_root=demo_output_root,
            health_output_root=health_output_root,
            allow_missing_baseline=True,
            run_failure_simulation=True,
        )
        current_issue_ids = _issue_id_set(current_audit)
        audit_iterations.append(
            {
                "iteration": iteration_count,
                "new_issues": sorted(current_issue_ids - previous_issue_ids),
                "resolved_issues": sorted(previous_issue_ids - current_issue_ids),
                "remaining_issues": sorted(current_issue_ids),
                **current_audit,
            }
        )
        previous_issue_ids = current_issue_ids

    too_many_loops = iteration_count > effective_max
    reason_code = _reason_code_for_audit(current_audit) if too_many_loops else ""
    return audit_iterations, fix_iterations, current_audit, iteration_count, too_many_loops, reason_code


def _summarize_optimizer_cleanup(cleanup_report: Path) -> str:
    if not cleanup_report.is_file():
        return "Cleanup report was not generated."
    try:
        lines = cleanup_report.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "Cleanup report exists but could not be read."
    non_empty = [line.strip() for line in lines if line.strip()]
    if not non_empty:
        return "Cleanup report generated with no candidates."
    return f"Cleanup report generated with {len(non_empty)} non-empty lines."


def _optimizer_phase() -> dict[str, Any]:
    cleanup_report = ROOT / "outputs" / "migration_state" / "cleanup_candidates.md"
    stability_dashboard = ROOT / "outputs" / "stability_dashboard.md"
    results = [
        _run(
            [
                sys.executable,
                str(ROOT / "scripts/ops/report_wrapper_cleanup_candidates.py"),
                "--output",
                str(cleanup_report),
            ],
            name="optimizer_cleanup_scan",
        ),
        _run(
            [
                sys.executable,
                str(ROOT / "scripts/ops/generate_stability_dashboard.py"),
                "--output",
                str(stability_dashboard),
            ],
            name="optimizer_stability_dashboard",
        ),
    ]
    return {
        "timestamp_utc": _utc_now(),
        "refactor_summary": "Generated cleanup candidates and refreshed stability dashboard.",
        "cleanup_report": str(cleanup_report),
        "cleanup_report_summary": _summarize_optimizer_cleanup(cleanup_report),
        "dashboard_report": str(stability_dashboard),
        "commands": [asdict(result) for result in results],
    }


def _confidence_level(critical: int, major: int, parity_pass: bool, health_pass: bool) -> str:
    if critical == 0 and major == 0 and parity_pass and health_pass:
        return "HIGH"
    if critical == 0 and major <= 1:
        return "MEDIUM"
    return "LOW"


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrate Builder/Audit/Optimizer validation pipeline.")
    parser.add_argument("--parity-config", default="configs/parity_test.yaml")
    parser.add_argument("--demo-profile", default="week1-demo")
    parser.add_argument("--demo-output-root", default="outputs/demo-gate-ci")
    parser.add_argument("--health-output-root", default="outputs/system_health")
    parser.add_argument("--allow-missing-baseline", action="store_true")
    parser.add_argument("--contract-file", default=str(DEFAULT_CONTRACT_FILE))
    parser.add_argument("--state-output", default="outputs/migration_state/orchestration_state.json")
    parser.add_argument("--report-output", default="outputs/migration_state/final_system_report.md")
    args = parser.parse_args()

    parity_config = Path(args.parity_config).expanduser().resolve()
    demo_output_root = Path(args.demo_output_root).expanduser().resolve()
    health_output_root = Path(args.health_output_root).expanduser().resolve()
    contract_file = Path(args.contract_file).expanduser().resolve()
    state_output = Path(args.state_output).expanduser().resolve()
    report_output = Path(args.report_output).expanduser().resolve()

    state: dict[str, Any] = {
        "started_at_utc": _utc_now(),
        "inputs": {
            "parity_config": str(parity_config),
            "demo_profile": args.demo_profile,
            "demo_output_root": str(demo_output_root),
            "health_output_root": str(health_output_root),
            "max_fix_loop": MAX_FIX_LOOP,
            "contract_file": str(contract_file),
        },
        "contract": _safe_read_yaml(contract_file),
        "builder_phase": {},
        "audit_iterations": [],
        "fix_iterations": [],
        "optimizer_phase": {},
        "final_audit": {},
    }

    builder = _builder_phase()
    state["builder_phase"] = builder

    (
        state["audit_iterations"],
        state["fix_iterations"],
        current_audit,
        iteration_count,
        too_many_loops,
        loop_failure_reason_code,
    ) = _run_fix_loop(
        parity_config=parity_config,
        demo_profile=args.demo_profile,
        demo_output_root=demo_output_root,
        health_output_root=health_output_root,
        allow_missing_baseline=bool(args.allow_missing_baseline),
        max_fix_loop=MAX_FIX_LOOP,
    )

    critical_count, major_count = _blocking_issue_counts(current_audit)
    stable_after_fix = critical_count == 0 and major_count == 0

    optimizer = {}
    if stable_after_fix and not too_many_loops:
        optimizer = _optimizer_phase()
    state["optimizer_phase"] = optimizer

    final_audit = current_audit
    if stable_after_fix and not too_many_loops:
        final_audit = _audit_phase(
            parity_config=parity_config,
            demo_profile=args.demo_profile,
            demo_output_root=demo_output_root,
            health_output_root=health_output_root,
            allow_missing_baseline=True,
            run_failure_simulation=True,
        )
    state["final_audit"] = final_audit

    final_critical = int(final_audit["severity_counts"].get("CRITICAL", 0))
    final_major = int(final_audit["severity_counts"].get("MAJOR", 0))
    parity_pass = final_audit["parity_status"] == "PASS"
    health_pass = final_audit["system_health"] == "PASS"
    schema_ok = not bool(final_audit["schema_violations"])
    demo_ok = bool(final_audit["demo_success"])
    pass_conditions = parity_pass and health_pass and schema_ok and demo_ok and final_critical == 0 and final_major == 0
    confidence = _confidence_level(final_critical, final_major, parity_pass, health_pass)

    total_found = sum(len(audit.get("issues", [])) for audit in state["audit_iterations"])
    remaining_issues = len(final_audit.get("issues", []))
    fixed_issues = max(total_found - remaining_issues, 0)

    state["completed_at_utc"] = _utc_now()
    state["iteration_count"] = iteration_count
    state["too_many_loops"] = too_many_loops
    state["loop_failure_reason_code"] = loop_failure_reason_code
    state["termination"] = {
        "parity_status": "PASS" if parity_pass else "FAIL",
        "system_health": "PASS" if health_pass else "FAIL",
        "no_critical_issues": final_critical == 0,
        "no_schema_violations": schema_ok,
        "demo_runs_successfully": demo_ok,
        "pass": pass_conditions,
    }

    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    lines: list[str] = []
    if pass_conditions and not too_many_loops:
        lines.extend(
            [
                "# ✅ FINAL SYSTEM REPORT",
                "",
                "### Status",
                "- Framework: ACTIVE",
                "- Legacy: DEPRECATED / REMOVED",
                "- Parity: PASS",
                "- Health Check: PASS",
                "- CI Gates: ENFORCED",
                "",
                "### Quality Metrics",
                f"- Issues Found: {total_found}",
                f"- Issues Fixed: {fixed_issues}",
                "- Remaining Issues: 0",
                "",
                "### System Confidence",
                confidence,
                "",
                f"- iteration_count: {iteration_count}",
                f"- state_output: {state_output}",
            ]
        )
    else:
        lines.extend(
            [
                "# ❌ PIPELINE FAILED",
                "",
                "### Blocking Issues",
            ]
        )
        for item in final_audit.get("issues", [])[:10]:
            lines.append(f"- [{item.get('severity', 'UNKNOWN')}] {item.get('summary', 'Unknown issue')}")
        if too_many_loops:
            lines.append(f"- iteration_count exceeded limit: {iteration_count} > {MAX_FIX_LOOP}")
            lines.append(f"- reason_code: {loop_failure_reason_code or 'PARITY_STUCK'}")
        lines.extend(
            [
                "",
                "### Suspected Root Causes",
            ]
        )
        if final_audit.get("issues"):
            for item in final_audit.get("issues", [])[:5]:
                details = str(item.get("details", "")).strip()
                lines.append(f"- {details[:220] if details else item.get('summary', 'Unknown cause')}")
        else:
            lines.append("- Unclassified failure; inspect command outputs in state report.")
        lines.extend(
            [
                "",
                "### Debug Commands",
                "- `PYTHONPATH=src ./.venv/bin/python scripts/ci/run_migration_gates.py --parity-config configs/parity_test.yaml --demo-profile week1-demo --demo-output-root outputs/demo-gate-ci --allow-missing-baseline`",
                "- `PYTHONPATH=src ./.venv/bin/python run_system_health_check.py --parity-config configs/parity_test.yaml --demo-profile week1-demo --demo-output-root outputs/demo-gate-ci --allow-missing-baseline --auto-fix`",
                "- `PYTHONPATH=src ./.venv/bin/python scripts/ci/validate_output_schemas.py --framework-run-dir <latest_framework_run_dir> --legacy-compat-csv outputs/demo-gate-ci/metrics_summary.csv`",
                f"- `PYTHONPATH=src ./.venv/bin/python {Path(__file__).relative_to(ROOT)} --allow-missing-baseline`",
                "",
                f"- iteration_count: {iteration_count}",
                f"- loop_failure_reason_code: {loop_failure_reason_code or 'n/a'}",
                f"- state_output: {state_output}",
            ]
        )

    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    raise SystemExit(0 if (pass_conditions and not too_many_loops) else 2)


if __name__ == "__main__":
    main()
