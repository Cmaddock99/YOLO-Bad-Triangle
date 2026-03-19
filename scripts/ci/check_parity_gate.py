#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from lab.config.contracts import (
    DEFAULT_MAX_CONFIDENCE_DELTA_PCT,
    DEFAULT_MAX_DETECTION_DELTA_PCT,
)
from lab.health_checks import (
    log_event,
    parity_delta_values,
    parity_threshold_failures,
    read_json_file,
    require_success,
    resolve_latest_shadow_run_dir,
    run_command,
)

def main() -> None:
    parser = argparse.ArgumentParser(description="CI parity gate with enforced thresholds.")
    parser.add_argument("--config", default="configs/parity_test.yaml")
    parser.add_argument(
        "--max-detection-delta-pct",
        type=float,
        default=DEFAULT_MAX_DETECTION_DELTA_PCT,
    )
    parser.add_argument(
        "--max-confidence-delta-pct",
        type=float,
        default=DEFAULT_MAX_CONFIDENCE_DELTA_PCT,
    )
    parser.add_argument("--parity-log", default="outputs/migration_state/parity_gate_log.jsonl")
    args = parser.parse_args()
    correlation_id = os.environ.get("MIGRATION_CORRELATION_ID", "")

    command = [
        sys.executable,
        str(ROOT / "run_shadow_parity.py"),
        "--config",
        str(Path(args.config).expanduser().resolve()),
    ]
    proc = run_command(
        name="shadow-parity",
        command=command,
        cwd=ROOT,
        component="parity-gate",
    )

    shadow_root = ROOT / "outputs" / "shadow_parity"
    run_dir = resolve_latest_shadow_run_dir(shadow_root)
    parity_report_path = run_dir / "parity_report.json"
    report = read_json_file(parity_report_path)
    if "parity_pass" not in report:
        raise RuntimeError(
            "Parity gate failed: parity report missing 'parity_pass' key from "
            "lab.migration.shadow_parity comparator."
        )
    detection_abs, confidence_abs = parity_delta_values(report)

    failures = parity_threshold_failures(
        returncode=proc.returncode,
        detection_abs_pct=detection_abs,
        confidence_abs_pct=confidence_abs,
        max_detection_delta_pct=float(args.max_detection_delta_pct),
        max_confidence_delta_pct=float(args.max_confidence_delta_pct),
    )
    if failures:
        _write_parity_log(
            log_path=Path(args.parity_log).expanduser().resolve(),
            status="FAIL",
            run_dir=run_dir,
            detection_abs=detection_abs,
            confidence_abs=confidence_abs,
            issues=failures,
            correlation_id=correlation_id,
        )
        raise RuntimeError("Parity gate failed: " + "; ".join(failures))
    require_success(proc, component="parity-gate")
    _write_parity_log(
        log_path=Path(args.parity_log).expanduser().resolve(),
        status="PASS",
        run_dir=run_dir,
        detection_abs=detection_abs,
        confidence_abs=confidence_abs,
        issues=[],
        correlation_id=correlation_id,
    )
    log_event(component="parity-gate", severity="INFO", message="Parity gate PASS")


def _write_parity_log(
    *,
    log_path: Path,
    status: str,
    run_dir: Path,
    detection_abs: float,
    confidence_abs: float,
    issues: list[str],
    correlation_id: str,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "status": status,
                    "stage": "parity",
                    "issues": issues,
                    "commands": ["python run_shadow_parity.py --config configs/parity_test.yaml"],
                    "run_dir": str(run_dir),
                    "detection_abs_pct": detection_abs,
                    "confidence_abs_pct": confidence_abs,
                    "correlation_id": correlation_id,
                }
            )
            + "\n"
        )


if __name__ == "__main__":
    main()
