#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_STATE_FILE = "PROJECT_STATE.md"


def _changed_files(against: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", against, "--"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"failed to inspect changed files: {proc.stderr.strip()}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _diff_contains_schema_version_change(against: str) -> bool:
    targets = [
        "src/lab/config/contracts.py",
        "src/lab/runners/run_experiment.py",
        "src/lab/reporting/legacy_compat.py",
    ]
    for target in targets:
        proc = subprocess.run(
            ["git", "diff", "--unified=0", against, "--", target],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            continue
        content = proc.stdout
        if "SCHEMA_ID_" in content or "_SCHEMA_VERSION" in content or "schema_version" in content:
            return True
    return False


def _schema_ids_backed_by_files() -> bool:
    contracts_path = ROOT / "src/lab/config/contracts.py"
    text = contracts_path.read_text(encoding="utf-8")
    ids = re.findall(r'SCHEMA_ID_[A-Z_]+\s*=\s*"([^"]+)"', text)
    schema_dir = ROOT / "schemas" / "v1"
    file_ids: set[str] = set()
    for path in schema_dir.glob("*.json"):
        try:
            payload = __import__("json").loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            file_ids.add(str(payload["id"]))
    return all(schema_id in file_ids for schema_id in ids)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Guard schema_version changes: require schema updates and migration notes."
    )
    parser.add_argument("--against", default="HEAD~1")
    args = parser.parse_args()

    changed = _changed_files(args.against)
    schema_version_changed = _diff_contains_schema_version_change(args.against)
    if not schema_version_changed:
        print("Schema change guard PASS (no schema_version change detected)")
        return

    schema_files_changed = any(path.startswith("schemas/v1/") for path in changed)
    project_state_changed = REQUIRED_STATE_FILE in changed
    if not schema_files_changed or not project_state_changed:
        raise RuntimeError(
            "schema_version change detected without required updates: "
            f"schema_files_changed={schema_files_changed}, project_state_changed={project_state_changed}"
        )
    if not _schema_ids_backed_by_files():
        raise RuntimeError(
            "schema_version change detected but one or more SCHEMA_ID_* values are not backed by schemas/v1/*.json id fields"
        )
    print("Schema change guard PASS")


if __name__ == "__main__":
    main()
