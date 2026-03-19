from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifacts import assert_files_exist


def schema_root_for_repo(repo_root: Path) -> Path:
    return repo_root / "schemas" / "v1"


@dataclass(frozen=True)
class SchemaValidationInputs:
    metrics_json: Path
    run_summary_json: Path
    legacy_csv: Path


def resolve_schema_validation_inputs(*, framework_run_dir: Path, legacy_compat_csv: Path) -> SchemaValidationInputs:
    metrics_json = framework_run_dir / "metrics.json"
    run_summary_json = framework_run_dir / "run_summary.json"
    assert_files_exist(
        paths=[metrics_json, run_summary_json, legacy_compat_csv],
        context="Schema validation",
    )
    return SchemaValidationInputs(
        metrics_json=metrics_json,
        run_summary_json=run_summary_json,
        legacy_csv=legacy_compat_csv,
    )


def _read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Failed to parse JSON at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping JSON payload at {path}")
    return payload


def validate_framework_json_file(*, path: Path, schema_file: Path) -> None:
    schema = _read_json_mapping(schema_file)
    payload = _read_json_mapping(path)
    required = schema.get("required", [])
    if not isinstance(required, list):
        raise ValueError(f"Schema {schema_file} has invalid 'required'")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"{path} missing required keys: {missing}")
    schema_version_const = ((schema.get("properties") or {}).get("schema_version") or {}).get("const")
    if schema_version_const and payload.get("schema_version") != schema_version_const:
        raise ValueError(
            f"{path} schema_version mismatch: expected {schema_version_const}, got {payload.get('schema_version')}"
        )


def validate_legacy_csv_file(*, path: Path, schema_file: Path) -> None:
    schema = _read_json_mapping(schema_file)
    required_columns = schema.get("required_columns", [])
    if not isinstance(required_columns, list):
        raise ValueError(f"Schema {schema_file} has invalid 'required_columns'")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        missing_columns = [col for col in required_columns if col not in headers]
        if missing_columns:
            raise ValueError(f"{path} missing required CSV columns: {missing_columns}")
        version_info = schema.get("schema_version_column", {})
        version_name = version_info.get("name")
        version_const = version_info.get("const")
        for idx, row in enumerate(reader, start=2):
            if version_name and version_const and row.get(version_name) != version_const:
                raise ValueError(
                    f"{path} row {idx} schema_version mismatch: expected {version_const}, got {row.get(version_name)}"
                )


def validate_output_bundle(
    *,
    repo_root: Path,
    framework_run_dir: Path,
    legacy_compat_csv: Path,
) -> SchemaValidationInputs:
    inputs = resolve_schema_validation_inputs(
        framework_run_dir=framework_run_dir,
        legacy_compat_csv=legacy_compat_csv,
    )
    schema_root = schema_root_for_repo(repo_root)
    validate_framework_json_file(
        path=inputs.metrics_json,
        schema_file=schema_root / "framework_metrics.schema.json",
    )
    validate_framework_json_file(
        path=inputs.run_summary_json,
        schema_file=schema_root / "framework_run_summary.schema.json",
    )
    validate_legacy_csv_file(
        path=inputs.legacy_csv,
        schema_file=schema_root / "legacy_compat_csv.schema.json",
    )
    return inputs


def validate_system_health_summary_payload(*, repo_root: Path, summary: dict[str, Any]) -> None:
    schema_file = schema_root_for_repo(repo_root) / "system_health_summary.schema.json"
    schema = _read_json_mapping(schema_file)
    required = schema.get("required", [])
    if not isinstance(required, list):
        raise ValueError(f"Schema {schema_file} has invalid 'required'")
    missing = [key for key in required if key not in summary]
    if missing:
        raise ValueError(f"system_health_summary missing required keys: {missing}")
    schema_version_const = ((schema.get("properties") or {}).get("schema_version") or {}).get("const")
    if schema_version_const and summary.get("schema_version") != schema_version_const:
        raise ValueError(
            "system_health_summary schema_version mismatch: "
            f"expected {schema_version_const}, got {summary.get('schema_version')}"
        )
