from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


TABLE_COLUMNS = [
    "experiment_name",
    "model",
    "attack",
    "defense",
    "precision",
    "recall",
    "mAP50",
    "mAP50-95",
]


def _first_value(row: dict[str, Any], *candidates: str) -> str:
    for key in candidates:
        if key in row and row[key] not in (None, ""):
            return str(row[key])
    return "-"


def generate_experiment_table(
    csv_path: Path, markdown_path: Path
) -> tuple[int, Path]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"Metrics summary not found: {csv_path}")

    with csv_path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        markdown_path.write_text("# Experiment Results\n\nNo experiments found.\n")
        return 0, markdown_path

    header = f"| {' | '.join(TABLE_COLUMNS)} |"
    separator = f"| {' | '.join(['---'] * len(TABLE_COLUMNS))} |"
    lines = ["# Experiment Results", "", header, separator]
    for row in rows:
        table_row = [
            _first_value(row, "experiment_name", "run_name"),
            _first_value(row, "model", "MODEL"),
            _first_value(row, "attack"),
            _first_value(row, "defense"),
            _first_value(row, "precision"),
            _first_value(row, "recall"),
            _first_value(row, "mAP50", "map50"),
            _first_value(row, "mAP50-95", "map50_95", "map"),
        ]
        lines.append(f"| {' | '.join(table_row)} |")

    markdown_path.write_text("\n".join(lines) + "\n")
    return len(rows), markdown_path
