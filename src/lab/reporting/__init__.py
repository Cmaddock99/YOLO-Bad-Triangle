"""Compatibility-only facade for reporting helpers.

New code should prefer ``lab.reporting.framework``, ``lab.reporting.local``,
or ``lab.reporting.aggregate``. The public ``lab.reporting`` umbrella remains
supported for existing imports.
"""

from . import framework_comparison
from .framework import (
    FrameworkRunRecord,
    build_comparison_rows,
    discover_framework_runs,
    is_none_like,
    normalize_name,
    render_markdown_report,
    write_summary_csv,
)
from .local import (
    build_team_summary_payload,
    generate_summary,
    render_team_summary_markdown,
    write_team_summary,
)
from .aggregate import build_auto_summary_payload, evaluate_warnings, render_auto_summary_markdown, write_auto_summary

__all__ = [
    "FrameworkRunRecord",
    "discover_framework_runs",
    "write_summary_csv",
    "build_comparison_rows",
    "render_markdown_report",
    "generate_summary",
    "build_team_summary_payload",
    "render_team_summary_markdown",
    "write_team_summary",
    "normalize_name",
    "is_none_like",
    "build_auto_summary_payload",
    "render_auto_summary_markdown",
    "write_auto_summary",
    "evaluate_warnings",
    "framework_comparison",
]
