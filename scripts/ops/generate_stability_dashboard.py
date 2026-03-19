#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def _pass_rate(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    passed = sum(1 for row in rows if str(row.get("status", "")).upper() == "PASS")
    return round((passed / len(rows)) * 100.0, 2)


def _weekly_chunks(rows: list[dict[str, Any]], weeks: int = 4) -> list[list[dict[str, Any]]]:
    if not rows:
        return [[] for _ in range(weeks)]
    tail = rows[-(weeks * 7) :]
    chunks: list[list[dict[str, Any]]] = []
    for idx in range(weeks):
        start = max(len(tail) - ((weeks - idx) * 7), 0)
        end = max(len(tail) - ((weeks - idx - 1) * 7), 0)
        chunks.append(tail[start:end])
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly migration stability dashboard.")
    parser.add_argument("--nightly-log", default="outputs/migration_state/nightly_shadow_log.jsonl")
    parser.add_argument("--ci-log", default="outputs/migration_state/ci_gate_log.jsonl")
    parser.add_argument("--health-log", default="outputs/migration_state/system_health_log.jsonl")
    parser.add_argument("--output", default="outputs/stability_dashboard.md")
    args = parser.parse_args()

    nightly_rows = _read_jsonl(Path(args.nightly_log).expanduser().resolve())
    ci_rows = _read_jsonl(Path(args.ci_log).expanduser().resolve())
    health_rows = _read_jsonl(Path(args.health_log).expanduser().resolve())

    parity_trend = [row.get("status", "UNKNOWN") for row in nightly_rows[-28:]]
    parity_chunks = _weekly_chunks(nightly_rows, weeks=4)
    ci_chunks = _weekly_chunks(ci_rows, weeks=4)
    health_chunks = _weekly_chunks(health_rows, weeks=4)
    regression_count = sum(
        1
        for row in health_rows
        if bool(row.get("regression_detected", False))
        or ("regression" in " ".join(str(item) for item in row.get("issues", [])))
    )
    lines = [
        "# Stability Dashboard",
        "",
        f"- Nightly parity pass rate: **{_pass_rate(nightly_rows)}%**",
        f"- CI gate pass rate: **{_pass_rate(ci_rows)}%**",
        f"- System health pass rate: **{_pass_rate(health_rows)}%**",
        "",
        "## Parity Trend (last 28)",
        "",
        ", ".join(str(item) for item in parity_trend) if parity_trend else "No data",
        "",
        "## Four-Week Trends",
        "",
        f"- Nightly parity pass rates by week: {[ _pass_rate(chunk) for chunk in parity_chunks ]}",
        f"- CI gate pass rates by week: {[ _pass_rate(chunk) for chunk in ci_chunks ]}",
        f"- Health pass rates by week: {[ _pass_rate(chunk) for chunk in health_chunks ]}",
        f"- Regression incidents (rolling 4 weeks): {regression_count}",
        "",
        "## Recent Counts",
        "",
        f"- Nightly runs: {len(nightly_rows)}",
        f"- CI checks: {len(ci_rows)}",
        f"- Health checks: {len(health_rows)}",
    ]
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote stability dashboard: {output_path}")


if __name__ == "__main__":
    main()
