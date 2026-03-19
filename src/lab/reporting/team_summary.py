from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .name_normalization import is_none_like, normalize_name


def _to_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_summary_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"framework summary CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_attack_interpretations(report_root: Path) -> dict[str, str]:
    interpretations: dict[str, str] = {}
    for txt_file in sorted(report_root.glob("summary_*.txt")):
        attack_name = txt_file.stem.removeprefix("summary_")
        text = txt_file.read_text(encoding="utf-8")
        marker = "Conclusion:"
        if marker not in text:
            continue
        tail = text.split(marker, 1)[1].strip()
        if not tail:
            continue
        first_line = tail.splitlines()[0].strip()
        if first_line and first_line != "----------------------------------":
            interpretations[attack_name] = first_line
    return interpretations


def _build_attack_rows(rows: list[dict[str, str]]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    baseline = next(
        (
            row
            for row in rows
            if is_none_like(row.get("attack")) and is_none_like(row.get("defense"))
        ),
        None,
    )
    if baseline is None:
        raise ValueError(
            "Baseline row is required in framework_run_summary.csv "
            "(attack and defense must be none-like values)."
        )
    baseline_detections = _to_optional_float(baseline.get("total_detections"))
    attack_rows: list[dict[str, Any]] = []
    for row in rows:
        attack_name = normalize_name(row.get("attack"))
        if is_none_like(attack_name):
            continue
        detections = _to_optional_float(row.get("total_detections"))
        drop = None
        if baseline_detections not in {None, 0.0} and detections is not None:
            drop = (baseline_detections - detections) / baseline_detections
        attack_rows.append(
            {
                "run_name": row.get("run_name"),
                "attack": attack_name,
                "seed": _to_optional_float(row.get("seed")),
                "total_detections": detections,
                "avg_confidence": _to_optional_float(row.get("avg_confidence")),
                "detection_drop": drop,
            }
        )
    attack_rows.sort(
        key=lambda item: (
            item["detection_drop"] is None,
            -(item["detection_drop"] or 0.0),
        )
    )
    return baseline, attack_rows


def build_team_summary_payload(report_root: Path) -> dict[str, Any]:
    report_root = report_root.expanduser().resolve()
    summary_csv = report_root / "framework_run_summary.csv"
    rows = _load_summary_csv(summary_csv)
    if not rows:
        raise ValueError(f"No run rows found in {summary_csv}")

    baseline_row, attack_rows = _build_attack_rows(rows)
    interpretations = _load_attack_interpretations(report_root)
    for row in attack_rows:
        attack_name = str(row["attack"])
        row["interpretation"] = interpretations.get(attack_name)

    strongest = attack_rows[0] if attack_rows else None
    payload = {
        "report_root": str(report_root),
        "total_runs": len(rows),
        "total_attack_runs": len(attack_rows),
        "baseline": {
            "run_name": baseline_row.get("run_name"),
            "model": baseline_row.get("model"),
            "seed": _to_optional_float(baseline_row.get("seed")),
            "total_detections": _to_optional_float(baseline_row.get("total_detections")),
            "avg_confidence": _to_optional_float(baseline_row.get("avg_confidence")),
        },
        "strongest_attack_by_detection_drop": strongest,
        "attacks_ranked": attack_rows,
    }
    return payload


def render_team_summary_markdown(payload: dict[str, Any]) -> str:
    baseline = payload.get("baseline", {})
    strongest = payload.get("strongest_attack_by_detection_drop") or {}
    attack_rows: list[dict[str, Any]] = list(payload.get("attacks_ranked") or [])

    lines = [
        "# Team Summary",
        "",
        f"- Total discovered runs: **{payload.get('total_runs', 0)}**",
        f"- Attack runs analyzed: **{payload.get('total_attack_runs', 0)}**",
        f"- Baseline run: `{baseline.get('run_name')}`",
        "",
    ]
    if strongest:
        drop = strongest.get("detection_drop")
        drop_text = "n/a" if drop is None else f"{float(drop) * 100:.1f}%"
        lines.extend(
            [
                "## Headline",
                "",
                f"- Strongest attack (by detection drop): `{strongest.get('attack')}` ({drop_text})",
                f"- Interpretation: {strongest.get('interpretation') or 'n/a'}",
                "",
            ]
        )
    lines.extend(
        [
            "## Attack Ranking",
            "",
            "| Attack | Detection drop | Avg confidence | Interpretation |",
            "|---|---:|---:|---|",
        ]
    )
    for row in attack_rows:
        drop = row.get("detection_drop")
        drop_text = "n/a" if drop is None else f"{float(drop) * 100:.1f}%"
        conf = row.get("avg_confidence")
        conf_text = "n/a" if conf is None else f"{float(conf):.4f}"
        lines.append(
            f"| `{row.get('attack')}` | {drop_text} | {conf_text} | {row.get('interpretation') or 'n/a'} |"
        )
    return "\n".join(lines)


def write_team_summary(report_root: Path) -> tuple[Path, Path]:
    payload = build_team_summary_payload(report_root)
    report_root = report_root.expanduser().resolve()
    json_path = report_root / "team_summary.json"
    md_path = report_root / "team_summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_team_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path
