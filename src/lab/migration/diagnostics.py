from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Mapping


def _is_nan_like(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    text = str(value).strip().lower()
    return text in {"", "nan", "none", "null"}


def _csv_issue_details(path: Path, required_columns: list[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not path.is_file():
        issues.append(
            {
                "missing_field": "<file>",
                "expected_type": "file",
                "actual": None,
                "likely_cause": "artifact not generated",
            }
        )
        return issues
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        for col in required_columns:
            if col not in headers:
                issues.append(
                    {
                        "missing_field": col,
                        "expected_type": "column",
                        "actual": None,
                        "likely_cause": "adapter schema mismatch",
                    }
                )
        rows = list(reader)
        for col in ("precision", "recall", "mAP50", "mAP50-95"):
            if col in headers and rows and all(_is_nan_like(row.get(col)) for row in rows):
                issues.append(
                    {
                        "missing_field": col,
                        "expected_type": "float",
                        "actual": None,
                        "likely_cause": "validation metrics not written",
                    }
                )
    return issues


def _primary_component_file(context: Mapping[str, Any]) -> str:
    artifact_path = context.get("artifact_path")
    if artifact_path:
        return str(artifact_path)
    return str(context.get("component", "unknown"))


def diagnose_failure(context: Mapping[str, Any]) -> dict[str, Any]:
    stage = str(context.get("stage", "unknown"))
    component = str(context.get("component", "unknown"))
    failure_type = str(context.get("failure_type", "unknown"))
    file_path = _primary_component_file(context)
    issue_details: list[dict[str, Any]] = []
    likely_cause = str(context.get("likely_cause", "unknown"))

    artifact_path_raw = context.get("artifact_path")
    required_columns = list(context.get("required_columns", []))
    if artifact_path_raw and required_columns:
        issue_details.extend(
            _csv_issue_details(Path(str(artifact_path_raw)).expanduser().resolve(), required_columns)
        )
        if issue_details:
            likely_cause = issue_details[0].get("likely_cause", likely_cause)

    if failure_type in {"schema_mismatch", "artifact_validation", "parity_failure", "execution_failure"}:
        severity = "CRITICAL"
    elif failure_type in {"regression_warning", "drift_warning"}:
        severity = "WARNING"
    else:
        severity = "INFO"

    suggestions = []
    if any(item.get("missing_field") in {"precision", "recall", "mAP50", "mAP50-95"} for item in issue_details):
        suggestions.append("Enable validation in run config (validation.enabled=true).")
    if failure_type == "parity_failure":
        suggestions.append("Normalize model/attack/defense naming via normalize_run_metadata().")
        suggestions.append("Re-run paired parity with run_shadow_parity.py.")
    if failure_type == "artifact_validation":
        suggestions.append("Ensure adapter writes metrics_summary.csv and experiment_table.md after framework runs.")
    if failure_type == "schema_mismatch":
        suggestions.append("Re-run schema validation and confirm schema_version fields are present and correct.")
    if not suggestions:
        suggestions.append("Inspect stage logs and rerun the failing gate with verbose output.")

    if failure_type == "execution_failure":
        commands = [
            "PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one --config configs/lab_framework_phase5.yaml --set validation.enabled=true",
            "PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py sweep --config configs/lab_framework_phase5.yaml --attacks fgsm --validation-enabled",
            "PYTHONPATH=src ./.venv/bin/python run_system_health_check.py --parity-config configs/parity_test.yaml",
        ]
    elif failure_type == "schema_mismatch":
        commands = [
            "PYTHONPATH=src ./.venv/bin/python scripts/ci/validate_output_schemas.py --framework-run-dir <framework_run_dir> --legacy-compat-csv outputs/demo-gate-ci/metrics_summary.csv",
            "PYTHONPATH=src ./.venv/bin/python run_system_health_check.py --parity-config configs/parity_test.yaml",
        ]
    elif failure_type == "parity_failure":
        commands = [
            "PYTHONPATH=src ./.venv/bin/python run_shadow_parity.py --config configs/parity_test.yaml",
            "PYTHONPATH=src ./.venv/bin/python scripts/migration_status.py",
        ]
    else:
        commands = [
            "PYTHONPATH=src ./.venv/bin/python scripts/demo/run_demo_package.sh fast --profile week1-demo --output-root outputs/demo-gate-ci",
            "PYTHONPATH=src ./.venv/bin/python scripts/check_metrics_integrity.py --csv outputs/demo-gate-ci/metrics_summary.csv --attack fgsm",
            "PYTHONPATH=src ./.venv/bin/python run_system_health_check.py --parity-config configs/parity_test.yaml --auto-fix",
        ]
    if artifact_path_raw:
        commands.append(f"python -c \"import pathlib; print(pathlib.Path(r'{artifact_path_raw}').read_text()[:4000])\"")

    confidence = 0.9 if issue_details else 0.7
    def _enrich_issue_payload(base: Mapping[str, Any]) -> dict[str, Any]:
        payload = dict(base)
        payload.update(
            {
                "file": file_path,
                "stage": stage,
                "fix": suggestions[0],
                "command": commands[0],
                "severity": severity,
                "confidence": confidence,
            }
        )
        return payload

    if issue_details:
        enriched_issues = [_enrich_issue_payload(item) for item in issue_details]
        issue_payload = enriched_issues[0]
    else:
        enriched_issues = [
            _enrich_issue_payload(
                {
                    "missing_field": "<unknown>",
                    "expected_type": "unknown",
                    "actual": None,
                    "likely_cause": likely_cause,
                }
            )
        ]
        issue_payload = enriched_issues[0]
    return {
        "failure_type": failure_type,
        "component": component,
        "file": file_path,
        "stage": stage,
        "severity": severity,
        "issue": issue_payload,
        "issues": enriched_issues,
        "likely_cause": likely_cause,
        "suggested_fixes": suggestions,
        "commands": commands,
        "fix_hint": suggestions[0],
        "primary_command": commands[0],
        "confidence": confidence,
        "debug_confidence_score": confidence,
    }


def write_health_failure_report(report_path: Path, diagnosis: Mapping[str, Any], summary: Mapping[str, Any]) -> None:
    lines = [
        "## ❌ SYSTEM HEALTH FAILURE",
        "",
        "### Component",
        str(diagnosis.get("component", "unknown")),
        "",
        "### Stage",
        str(diagnosis.get("stage", "unknown")),
        "",
        "### Issue",
        json.dumps(diagnosis.get("issue", {}), indent=2, sort_keys=True),
        "",
        "### Likely Cause",
        str(diagnosis.get("likely_cause", "unknown")),
        "",
        "### Suggested Fixes",
    ]
    for item in diagnosis.get("suggested_fixes", []):
        lines.append(f"- {item}")
    lines.extend(["", "### Commands"])
    for command in diagnosis.get("commands", []):
        lines.append(command)
    lines.extend(
        [
            "",
            "### Health Summary",
            json.dumps(summary, indent=2, sort_keys=True),
            "",
            f"Confidence: {diagnosis.get('debug_confidence_score', 0.0)}",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
