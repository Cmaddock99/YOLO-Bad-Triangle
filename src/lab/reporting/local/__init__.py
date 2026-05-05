"""Stable local-reporting namespace for new code."""

from .failure_gallery import generate_failure_gallery
from ..experiment_summary import generate_summary
from ..team_summary import (
    build_team_summary_payload,
    render_team_summary_markdown,
    write_team_summary,
)

__all__ = [
    "generate_summary",
    "generate_failure_gallery",
    "build_team_summary_payload",
    "render_team_summary_markdown",
    "write_team_summary",
]
