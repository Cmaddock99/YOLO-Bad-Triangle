from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GateOrderAndObservabilityTest(unittest.TestCase):
    def test_observability_contract_script(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            gate_summary = tmp_root / "gate_summary.json"
            health_summary = tmp_root / "system_health_summary.json"
            status_snapshot = tmp_root / "migration_status_snapshot.json"
            payload = {
                "status": "PASS",
                "stage": "test",
                "issues": [],
                "commands": ["echo ok"],
                "timestamp_utc": "2026-03-19T00:00:00Z",
            }
            gate_summary.write_text(json.dumps(payload), encoding="utf-8")
            health_summary.write_text(json.dumps(payload), encoding="utf-8")
            status_snapshot.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/ci/check_observability_contract.py"),
                    "--gate-summary",
                    str(gate_summary),
                    "--health-summary",
                    str(health_summary),
                    "--status-snapshot",
                    str(status_snapshot),
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)


if __name__ == "__main__":
    unittest.main()
