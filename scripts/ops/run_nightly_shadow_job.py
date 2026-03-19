#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Nightly shadow parity job runner.")
    parser.add_argument("--config", default="configs/parity_test.yaml")
    parser.add_argument("--log-path", default="outputs/migration_state/nightly_shadow_log.jsonl")
    args = parser.parse_args()

    command = [sys.executable, str(ROOT / "run_shadow_parity.py"), "--config", args.config]
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    proc = subprocess.run(command, cwd=str(ROOT), env=env, capture_output=True, text=True, check=False)
    log_path = Path(args.log_path).expanduser().resolve()
    previous_rows: list[dict[str, object]] = []
    if log_path.is_file():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            text = line.strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                previous_rows.append(parsed)
    status = "PASS" if proc.returncode == 0 else "FAIL"
    correlation_id = os.environ.get("MIGRATION_CORRELATION_ID", "")
    failure_category = "none"
    if status == "FAIL":
        stderr_lower = proc.stderr.lower()
        if "schema" in stderr_lower:
            failure_category = "schema"
        elif "artifact" in stderr_lower:
            failure_category = "artifact"
        elif "parity" in stderr_lower:
            failure_category = "parity"
        else:
            failure_category = "execution"
    recent_statuses = [str(row.get("status", "")).upper() for row in previous_rows[-3:]]
    flaky_marker = bool(recent_statuses and any(item != status for item in recent_statuses))
    run_record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "stage": "nightly_shadow_parity",
        "issues": [] if status == "PASS" else [f"failure_category={failure_category}"],
        "commands": [" ".join(command)],
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "failure_category": failure_category,
        "flaky_marker": flaky_marker,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
        "correlation_id": correlation_id,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(run_record) + "\n")
    print(json.dumps(run_record, indent=2))
    if proc.returncode != 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
