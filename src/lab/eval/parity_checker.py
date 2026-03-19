from __future__ import annotations

from pathlib import Path
from typing import Any

from lab.migration.shadow_parity import compare_legacy_csv_to_framework_artifacts


def compare(
    legacy_csv: str | Path,
    framework_metrics_json: str | Path,
    predictions_jsonl: str | Path,
) -> dict[str, Any]:
    # Compatibility shim: parity implementation lives in migration/shadow_parity.py.
    return compare_legacy_csv_to_framework_artifacts(
        legacy_csv=legacy_csv,
        framework_metrics_json=framework_metrics_json,
        predictions_jsonl=predictions_jsonl,
    )
