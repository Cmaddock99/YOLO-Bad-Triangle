#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).replace(microsecond=0).isoformat()


def _collect_progress(runs_root: Path) -> dict[str, Any]:
    run_dirs = [path for path in runs_root.iterdir() if path.is_dir()] if runs_root.is_dir() else []
    completed_runs = 0
    prepared_images_total = 0
    latest_mtime = 0.0
    active_run = None
    active_score = -1

    for run_dir in sorted(run_dirs):
        metrics_path = run_dir / "metrics.json"
        prepared_dir = run_dir / "prepared_images"
        prepared_count = 0
        if prepared_dir.is_dir():
            prepared_count = sum(1 for _ in prepared_dir.iterdir())
            prepared_images_total += prepared_count
            latest_mtime = max(latest_mtime, prepared_dir.stat().st_mtime)
        if metrics_path.is_file():
            completed_runs += 1
            latest_mtime = max(latest_mtime, metrics_path.stat().st_mtime)
        score = prepared_count + (100000 if metrics_path.is_file() else 0)
        if score > active_score:
            active_score = score
            active_run = run_dir.name

    return {
        "run_dirs_discovered": len(run_dirs),
        "completed_runs": completed_runs,
        "prepared_images_total": prepared_images_total,
        "active_run": active_run,
        "latest_mtime_epoch": latest_mtime,
    }


def _resource_snapshot(pid: int) -> dict[str, Any]:
    command = ["ps", "-o", "pid=,%cpu=,rss=,vsz=,etime=,state=", "-p", str(pid)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        return {"ok": False, "error": f"ps invocation failed: {exc}"}
    line = (result.stdout or "").strip()
    if not line:
        return {"ok": False, "error": "no ps output"}
    parts = line.split()
    if len(parts) < 6:
        return {"ok": False, "error": f"unexpected ps output: {line}"}
    return {
        "ok": True,
        "pid": int(parts[0]),
        "cpu_pct": float(parts[1]),
        "rss_kb": int(parts[2]),
        "vsz_kb": int(parts[3]),
        "elapsed": parts[4],
        "state": parts[5],
    }


def _validate_artifacts(report_root: Path) -> dict[str, Any]:
    required = {
        "framework_run_summary_csv": report_root / "framework_run_summary.csv",
        "framework_run_report_md": report_root / "framework_run_report.md",
        "team_summary_json": report_root / "team_summary.json",
        "team_summary_md": report_root / "team_summary.md",
    }
    checks: dict[str, bool] = {}
    for label, path in required.items():
        checks[label] = path.is_file()
    parse_errors: list[str] = []
    if checks["team_summary_json"]:
        try:
            payload = json.loads((report_root / "team_summary.json").read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                parse_errors.append("team_summary.json is not a JSON object")
        except (OSError, json.JSONDecodeError) as exc:
            parse_errors.append(f"team_summary.json parse error: {exc}")
    return {
        "checks": checks,
        "all_present": all(checks.values()),
        "parse_errors": parse_errors,
        "parse_ok": not parse_errors,
    }


def _run_smoke_command(command: list[str], *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"command": command, "dry_run": True, "return_code": 0, "ok": True}
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "command": command,
        "return_code": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout_tail": (completed.stdout or "").splitlines()[-10:],
        "stderr_tail": (completed.stderr or "").splitlines()[-10:],
    }


def _run_post_stress_smoke(*, python_bin: str, dry_run: bool, root: Path) -> dict[str, Any]:
    framework_smoke = [
        python_bin,
        "src/lab/runners/run_experiment.py",
        "--config",
        "configs/default.yaml",
        "--set",
        f"runner.output_root={root / 'outputs/overnight_post_stress'}",
        "--set",
        "runner.run_name=framework_smoke",
        "--set",
        "runner.max_images=4",
        "--set",
        "attack.name=blur",
        "--set",
        "validation.enabled=false",
        "--set",
        "summary.enabled=false",
    ]
    legacy_list = [python_bin, "run_experiment.py", "--list-attacks"]
    env_check = [python_bin, "scripts/check_environment.py"]
    results = {
        "framework_smoke": _run_smoke_command(framework_smoke, dry_run=dry_run),
        "legacy_list": _run_smoke_command(legacy_list, dry_run=dry_run),
        "environment_check": _run_smoke_command(env_check, dry_run=dry_run),
    }
    results["all_ok"] = all(item.get("ok") for item in results.values() if isinstance(item, dict))
    return results


def _classify_final_status(
    *,
    timed_out: bool,
    exit_code: int | None,
    artifact_result: dict[str, Any],
    smoke_result: dict[str, Any],
) -> str:
    smoke_ok = bool(smoke_result.get("all_ok"))
    artifacts_ok = bool(artifact_result.get("all_present")) and bool(artifact_result.get("parse_ok"))
    if timed_out and smoke_ok:
        return "timed_out_resumable"
    if exit_code == 0 and artifacts_ok and smoke_ok:
        return "completed_clean"
    if exit_code == 0 and smoke_ok:
        return "completed_with_caveats"
    return "failed_needs_attention"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _build_summary_markdown(
    *,
    status: dict[str, Any],
    artifact_result: dict[str, Any],
    smoke_result: dict[str, Any],
) -> str:
    lines = [
        "# Overnight Stress Summary",
        "",
        f"- Final status: **{status.get('final_status', 'unknown')}**",
        f"- Started: `{status.get('started_at')}`",
        f"- Ended: `{status.get('ended_at')}`",
        f"- Timeout seconds: `{status.get('timeout_seconds')}`",
        f"- Timed out: `{status.get('timed_out')}`",
        f"- Sweep exit code: `{status.get('sweep_exit_code')}`",
        "",
        "## Artifact Validation",
        "",
        f"- All required artifacts present: `{artifact_result.get('all_present')}`",
        f"- Parse checks passed: `{artifact_result.get('parse_ok')}`",
    ]
    checks = artifact_result.get("checks", {})
    for label in sorted(checks):
        lines.append(f"- {label}: `{checks[label]}`")
    parse_errors = artifact_result.get("parse_errors") or []
    if parse_errors:
        lines.append("- Parse errors:")
        for error in parse_errors:
            lines.append(f"  - {error}")
    lines.extend(
        [
            "",
            "## Post-Stress Smoke Checks",
            "",
            f"- Overall smoke status: `{smoke_result.get('all_ok')}`",
        ]
    )
    for name in ("framework_smoke", "legacy_list", "environment_check"):
        result = smoke_result.get(name, {})
        lines.append(f"- {name}: `{result.get('ok')}` (rc={result.get('return_code')})")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run overnight full stress sweep with timeout, heartbeat monitoring, and recovery checks."
    )
    parser.add_argument("--python-bin", default="./.venv/bin/python")
    parser.add_argument("--window-hours", type=float, default=10.0)
    parser.add_argument("--heartbeat-seconds", type=int, default=300)
    parser.add_argument("--stale-seconds", type=int, default=1800)
    parser.add_argument("--runs-root", default="outputs/overnight_stress_runs")
    parser.add_argument("--report-root", default="outputs/overnight_stress_reports")
    parser.add_argument("--attacks", default=None, help="Optional comma-separated attack list override.")
    parser.add_argument("--resume", action="store_true", help="Resume from completed runs when possible.")
    parser.add_argument("--validation-enabled", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    try:
        args = parser.parse_args()

        repo_root = Path(__file__).resolve().parents[1]
        python_bin_path = (repo_root / args.python_bin).resolve() if not Path(args.python_bin).is_absolute() else Path(args.python_bin).resolve()
        if not python_bin_path.is_file():
            raise FileNotFoundError(f"Python binary not found: {python_bin_path}")

        runs_root = (repo_root / args.runs_root).resolve()
        report_root = (repo_root / args.report_root).resolve()
        runs_root.mkdir(parents=True, exist_ok=True)
        report_root.mkdir(parents=True, exist_ok=True)

        status_path = report_root / "overnight_status.json"
        heartbeat_path = report_root / "overnight_heartbeat.jsonl"
        summary_path = report_root / "overnight_summary.md"
        stress_log_path = report_root / "overnight_stress.log"

        timeout_seconds = max(1, int(args.window_hours * 3600))
        sweep_command = [
            args.python_bin,
            "scripts/sweep_and_report.py",
            "--preset",
            "full",
            "--runs-root",
            str(runs_root),
            "--report-root",
            str(report_root),
        ]
        if args.resume:
            sweep_command.append("--resume")
        if args.attacks:
            sweep_command.extend(["--attacks", args.attacks])
        if args.validation_enabled:
            sweep_command.append("--validation-enabled")
        if args.dry_run:
            sweep_command.append("--dry-run")

        status: dict[str, Any] = {
            "started_at": _utc_iso(),
            "runs_root": str(runs_root),
            "report_root": str(report_root),
            "timeout_seconds": timeout_seconds,
            "heartbeat_seconds": args.heartbeat_seconds,
            "stale_seconds": args.stale_seconds,
            "sweep_command": sweep_command,
            "timed_out": False,
            "stale_warnings": 0,
        }
        _write_json(status_path, status)

        if args.dry_run:
            status["sweep_exit_code"] = 0
            status["ended_at"] = _utc_iso()
            artifact_result = _validate_artifacts(report_root)
            smoke_result = _run_post_stress_smoke(python_bin=args.python_bin, dry_run=True, root=repo_root)
            status["final_status"] = _classify_final_status(
                timed_out=False,
                exit_code=0,
                artifact_result=artifact_result,
                smoke_result=smoke_result,
            )
            _write_json(status_path, status)
            summary_path.write_text(
                _build_summary_markdown(status=status, artifact_result=artifact_result, smoke_result=smoke_result),
                encoding="utf-8",
            )
            print("Dry-run complete.")
            print(f"Status: {status_path}")
            print(f"Summary: {summary_path}")
            return

        started_monotonic = time.monotonic()
        stale_started_at: float | None = None
        last_signature: tuple[Any, ...] | None = None
        sweep_exit_code: int | None = None

        with stress_log_path.open("a", encoding="utf-8") as stress_log:
            process = subprocess.Popen(
                sweep_command,
                cwd=repo_root,
                stdout=stress_log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            status["sweep_pid"] = process.pid
            _write_json(status_path, status)

            while process.poll() is None:
                now = _utc_now()
                elapsed = int(time.monotonic() - started_monotonic)
                progress = _collect_progress(runs_root)
                resources = _resource_snapshot(process.pid)
                signature = (
                    progress["completed_runs"],
                    progress["prepared_images_total"],
                    progress["latest_mtime_epoch"],
                )
                if signature != last_signature:
                    stale_started_at = None
                    last_signature = signature
                else:
                    if stale_started_at is None:
                        stale_started_at = time.monotonic()
                    elif (time.monotonic() - stale_started_at) >= args.stale_seconds:
                        status["stale_warnings"] = int(status.get("stale_warnings", 0)) + 1
                        stale_started_at = time.monotonic()

                heartbeat = {
                    "timestamp": _utc_iso(now),
                    "elapsed_seconds": elapsed,
                    "timed_out": False,
                    "progress": progress,
                    "resources": resources,
                    "stale_warnings": status.get("stale_warnings", 0),
                }
                _append_jsonl(heartbeat_path, heartbeat)

                if elapsed >= timeout_seconds:
                    status["timed_out"] = True
                    process.terminate()
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=30)
                    break
                time.sleep(max(1, args.heartbeat_seconds))

            sweep_exit_code = process.poll()

        artifact_result = _validate_artifacts(report_root)
        smoke_result = _run_post_stress_smoke(python_bin=args.python_bin, dry_run=False, root=repo_root)

        status["sweep_exit_code"] = sweep_exit_code
        status["artifact_validation"] = artifact_result
        status["post_stress_smoke"] = smoke_result
        status["ended_at"] = _utc_iso()
        status["final_status"] = _classify_final_status(
            timed_out=bool(status.get("timed_out")),
            exit_code=sweep_exit_code,
            artifact_result=artifact_result,
            smoke_result=smoke_result,
        )
        _write_json(status_path, status)
        summary_path.write_text(
            _build_summary_markdown(status=status, artifact_result=artifact_result, smoke_result=smoke_result),
            encoding="utf-8",
        )

        print(f"Overnight run complete with status: {status['final_status']}")
        print(f"Status JSON:   {status_path}")
        print(f"Heartbeat log: {heartbeat_path}")
        print(f"Summary MD:    {summary_path}")
        print(f"Stress log:    {stress_log_path}")
    except (ValueError, FileNotFoundError, subprocess.SubprocessError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
