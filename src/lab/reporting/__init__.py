"""Compatibility-only facade for reporting helpers.

New code should prefer ``lab.reporting.framework``, ``lab.reporting.local``,
or ``lab.reporting.aggregate``. The public ``lab.reporting`` umbrella remains
supported for existing imports.
"""

from . import framework_comparison
from .aggregate import (
    build_auto_summary_payload,
    evaluate_warnings,
    render_auto_summary_markdown,
    write_auto_summary,
)
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

__all__ = [
    "FrameworkRunRecord",
    "build_auto_summary_payload",
    "build_comparison_rows",
    "build_team_summary_payload",
    "discover_framework_runs",
    "evaluate_warnings",
    "framework_comparison",
    "generate_summary",
    "is_none_like",
    "normalize_name",
    "render_auto_summary_markdown",
    "render_markdown_report",
    "render_team_summary_markdown",
    "write_auto_summary",
    "write_summary_csv",
    "write_team_summary",
]
