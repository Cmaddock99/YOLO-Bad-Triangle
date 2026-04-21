from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..framework_comparison import (
    FrameworkRunRecord,
    discover_framework_runs,
    render_markdown_report,
    write_summary_csv,
)


def _assert_consistent_profile(records: Sequence[FrameworkRunRecord]) -> None:
    profile_pairs = {
        (record.pipeline_profile, record.authoritative_metric)
        for record in records
    }
    if len(profile_pairs) > 1:
        raise ValueError(
            "Mixed pipeline profiles or authoritative metrics detected under one runs-root. "
            "Generate reports from a single profile-consistent run set."
        )


def generate_framework_report(
    *,
    runs_root: Path,
    output_dir: Path,
) -> tuple[Path, Path, int]:
    runs_root = runs_root.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = discover_framework_runs(runs_root)
    _assert_consistent_profile(records)
    csv_path = output_dir / "framework_run_summary.csv"
    md_path = output_dir / "framework_run_report.md"

    write_summary_csv(records, csv_path)
    md_path.write_text(render_markdown_report(records), encoding="utf-8")
    return csv_path, md_path, len(records)


__all__ = [
    "_assert_consistent_profile",
    "generate_framework_report",
]
