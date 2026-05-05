"""Stable framework-reporting namespace for new code."""

from .report_bundle import generate_framework_report
from ..framework_comparison import (
    FrameworkRunRecord,
    build_comparison_rows,
    build_defense_recovery_rows,
    build_imported_patch_recovery_rows,
    build_per_class_rows,
    discover_framework_runs,
    is_none_like,
    normalize_name,
    render_markdown_report,
    write_summary_csv,
)

__all__ = [
    "FrameworkRunRecord",
    "generate_framework_report",
    "discover_framework_runs",
    "write_summary_csv",
    "render_markdown_report",
    "build_comparison_rows",
    "build_defense_recovery_rows",
    "build_imported_patch_recovery_rows",
    "build_per_class_rows",
    "normalize_name",
    "is_none_like",
]
