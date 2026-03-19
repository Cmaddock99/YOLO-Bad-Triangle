from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FrameworkToHealthIntegrationTest(unittest.TestCase):
    def test_framework_adapter_schema_health_pipeline(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            framework_run = tmp_root / "framework_runs" / "run_integration"
            framework_run.mkdir(parents=True, exist_ok=True)
            (framework_run / "metrics.json").write_text(
                json.dumps(
                    {
                        "schema_version": "framework_metrics/v1",
                        "predictions": {
                            "image_count": 2,
                            "images_with_detections": 2,
                            "total_detections": 6,
                            "confidence": {"mean": 0.6, "median": 0.61, "p25": 0.5, "p75": 0.7},
                        },
                        "validation": {
                            "status": "complete",
                            "enabled": True,
                            "precision": 0.7,
                            "recall": 0.65,
                            "mAP50": 0.6,
                            "mAP50-95": 0.5,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (framework_run / "run_summary.json").write_text(
                json.dumps(
                    {
                        "schema_version": "framework_run_summary/v1",
                        "run_dir": str(framework_run),
                        "metrics_path": str(framework_run / "metrics.json"),
                        "model": {"name": "yolo11n"},
                        "attack": {"name": "fgsm", "params": {"eps": 0.03}},
                        "defense": {"name": "none", "params": {}},
                        "seed": 42,
                        "run": {"conf": 0.25, "iou": 0.7, "imgsz": 640, "session_id": "sess", "started_at_utc": "now"},
                        "config_fingerprint": "fp",
                        "validation": {"enabled": True},
                    }
                ),
                encoding="utf-8",
            )

            demo_output = tmp_root / "demo"
            health_output = tmp_root / "health"
            shadow_run = tmp_root / "shadow" / "run1"
            shadow_framework_run = shadow_run / "framework" / "run_integration"
            shadow_run.mkdir(parents=True, exist_ok=True)
            shadow_framework_run.mkdir(parents=True, exist_ok=True)
            (shadow_framework_run / "metrics.json").write_text(
                (framework_run / "metrics.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (shadow_framework_run / "run_summary.json").write_text(
                (framework_run / "run_summary.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (shadow_run / "parity_report.json").write_text(
                json.dumps(
                    {
                        "parity_pass": True,
                        "delta_summary": {
                            "detection_worst_relative_pct": 0.0,
                            "confidence_worst_relative_pct": 0.0,
                        },
                    }
                ),
                encoding="utf-8",
            )

            env = dict(os.environ)
            env["PYTHONPATH"] = "src"
            subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/generate_legacy_compat_artifacts.py"),
                    "--runs-root",
                    str(tmp_root / "framework_runs"),
                    "--output-root",
                    str(demo_output),
                ],
                cwd=str(repo_root),
                env=env,
                check=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "scripts/ci/validate_output_schemas.py"),
                    "--framework-run-dir",
                    str(framework_run),
                    "--legacy-compat-csv",
                    str(demo_output / "metrics_summary.csv"),
                ],
                cwd=str(repo_root),
                env=env,
                check=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "run_system_health_check.py"),
                    "--skip-execution",
                    "--allow-missing-baseline",
                    "--demo-output-root",
                    str(demo_output),
                    "--health-output-root",
                    str(health_output),
                    "--shadow-root",
                    str(tmp_root / "shadow"),
                    "--baseline-report",
                    str(health_output / "baseline_report_latest.json"),
                    "--baseline-history",
                    str(health_output / "baseline_history.jsonl"),
                    "--health-log",
                    str(health_output / "health_log.jsonl"),
                ],
                cwd=str(repo_root),
                env=env,
                check=True,
            )

            summary = json.loads((health_output / "system_health_summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["overall_pass"])


if __name__ == "__main__":
    unittest.main()
