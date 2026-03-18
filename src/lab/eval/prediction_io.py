from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .prediction_schema import PredictionRecord


def write_predictions_jsonl(records: Iterable[PredictionRecord], output_path: Path) -> None:
    """Persist normalized prediction records as JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
