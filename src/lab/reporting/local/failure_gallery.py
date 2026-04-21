from __future__ import annotations

import html
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from lab.config.contracts import PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE
from lab.eval.framework_metrics import is_validation_success
from lab.reporting.framework import (
    FrameworkRunRecord,
    discover_framework_runs,
    is_none_like,
    normalize_name,
)

_AUTHORITY_AUTHORITATIVE = "authoritative"
_AUTHORITY_DIAGNOSTIC = "diagnostic"
_PHASE_PRIORITY = {
    "phase4": 0,
    "phase2": 1,
    "phase1": 2,
    "phase3": 3,
    "manual": 4,
}


def _read_json_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _load_detection_counts(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not path.is_file():
        return counts
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            image_id = str(payload.get("image_id") or "").strip()
            boxes = payload.get("boxes")
            if not image_id or not isinstance(boxes, list):
                continue
            counts[image_id] = len(boxes)
    return counts


def _authority_priority(value: object) -> int:
    normalized = normalize_name(value)
    if normalized == _AUTHORITY_AUTHORITATIVE:
        return 0
    if normalized == _AUTHORITY_DIAGNOSTIC:
        return 1
    return 2


def _phase_priority(value: object) -> int:
    return _PHASE_PRIORITY.get(normalize_name(value), len(_PHASE_PRIORITY))


def _selection_key(record: FrameworkRunRecord) -> tuple[int, int, int, str]:
    return (
        _authority_priority(record.authority),
        0 if is_validation_success(record.validation_status) else 1,
        _phase_priority(record.source_phase),
        record.run_name,
    )


def _select_best(records: list[FrameworkRunRecord]) -> FrameworkRunRecord | None:
    if not records:
        return None
    return min(records, key=_selection_key)


def _normalized_semantic_order(record: FrameworkRunRecord) -> str:
    normalized = normalize_name(record.semantic_order)
    return normalized or "missing"


def _preferred_attack_record(
    records: list[FrameworkRunRecord],
    *,
    attack_signature: str | None,
    attack_name: str,
    preferred_authority: str | None,
) -> FrameworkRunRecord | None:
    attack_only_records = [
        record
        for record in records
        if not is_none_like(record.attack) and is_none_like(record.defense)
    ]
    signature = str(attack_signature or "").strip()
    if signature:
        signature_matches = [
            record
            for record in attack_only_records
            if str(record.attack_signature or "").strip() and record.attack_signature == signature
        ]
        if signature_matches:
            authority_matches = [
                record for record in signature_matches if record.authority == preferred_authority
            ]
            return _select_best(authority_matches or signature_matches)

    name_matches = [
        record
        for record in attack_only_records
        if normalize_name(record.attack) == normalize_name(attack_name)
    ]
    if not name_matches:
        return None
    authority_matches = [
        record for record in name_matches if record.authority == preferred_authority
    ]
    return _select_best(authority_matches or name_matches)


def _select_records(
    runs_root: Path,
) -> tuple[
    FrameworkRunRecord | None,
    dict[str, FrameworkRunRecord],
    list[tuple[FrameworkRunRecord, FrameworkRunRecord]],
    dict[str, int],
]:
    records = discover_framework_runs(runs_root)
    baseline = _select_best(
        [record for record in records if is_none_like(record.attack) and is_none_like(record.defense)]
    )

    attack_groups: dict[str, list[FrameworkRunRecord]] = defaultdict(list)
    defended_groups: dict[tuple[str, str, str], list[FrameworkRunRecord]] = defaultdict(list)
    excluded_defended_counts: dict[str, int] = defaultdict(int)
    for record in records:
        attack_name = normalize_name(record.attack)
        defense_name = normalize_name(record.defense)
        if is_none_like(attack_name):
            continue
        if is_none_like(defense_name):
            attack_groups[attack_name].append(record)
            continue
        semantic_order = _normalized_semantic_order(record)
        if semantic_order != PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE:
            excluded_defended_counts[semantic_order] += 1
            continue
        attack_key = str(record.attack_signature or "").strip() or attack_name
        defended_groups[(attack_key, attack_name, defense_name)].append(record)

    selected_attacks = {
        attack_name: selected
        for attack_name, selected in (
            (attack_name, _select_best(group)) for attack_name, group in attack_groups.items()
        )
        if selected is not None
    }
    matched_defended: list[tuple[FrameworkRunRecord, FrameworkRunRecord]] = []
    for _, defended in sorted(
        ((key, _select_best(group)) for key, group in defended_groups.items()),
        key=lambda item: (
            normalize_name((item[1].attack if item[1] is not None else "")),
            normalize_name((item[1].defense if item[1] is not None else "")),
            (item[1].run_name if item[1] is not None else ""),
        ),
    ):
        if defended is None:
            continue
        attack_record = _preferred_attack_record(
            records,
            attack_signature=defended.attack_signature,
            attack_name=defended.attack,
            preferred_authority=defended.authority,
        )
        if attack_record is None:
            continue
        matched_defended.append((defended, attack_record))
    return baseline, selected_attacks, matched_defended, dict(sorted(excluded_defended_counts.items()))


def _has_prepared_images(record: FrameworkRunRecord | None) -> bool:
    if record is None:
        return False
    images_dir = record.run_dir / "images"
    if not images_dir.is_dir():
        return False
    return any(path.is_file() for path in images_dir.iterdir())


def _relative_href(output_path: Path, target: Path | None) -> str | None:
    if target is None or not target.is_file():
        return None
    return Path(os.path.relpath(target, output_path.parent)).as_posix()


def _baseline_source_dir(record: FrameworkRunRecord | None) -> Path | None:
    if record is None:
        return None
    summary = _read_json_mapping(record.run_dir / "run_summary.json")
    source_dir = str(summary.get("source_dir") or "").strip()
    if not source_dir:
        return None
    path = Path(source_dir).expanduser()
    if not path.is_absolute():
        path = (record.run_dir / path).resolve()
    return path if path.is_dir() else None


def _image_cell(label: str, href: str | None) -> str:
    if href is None:
        return (
            '<div class="image-cell placeholder">'
            f"<div class=\"label\">{html.escape(label)}</div>"
            "<div class=\"missing\">missing</div>"
            "</div>"
        )
    return (
        '<div class="image-cell">'
        f"<div class=\"label\">{html.escape(label)}</div>"
        f"<img src=\"{html.escape(href)}\" alt=\"{html.escape(label)}\">"
        "</div>"
    )


def _metric_line(label: str, value: object) -> str:
    return (
        '<div class="metric">'
        f"<span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong>"
        "</div>"
    )


def _comparability_warning_html(excluded_counts: dict[str, int]) -> str:
    if not excluded_counts:
        return ""
    parts = [
        f"{html.escape(category)}={count}"
        for category, count in excluded_counts.items()
    ]
    return (
        '<div class="warning">'
        "Defended comparisons exclude legacy or unknown semantics: "
        f"{', '.join(parts)}."
        "</div>"
    )


def _rank_rows(
    baseline_counts: dict[str, int],
    primary_counts: dict[str, int],
    *,
    secondary_counts: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    image_ids = sorted(set(baseline_counts) | set(primary_counts) | set(secondary_counts or {}))
    ranked_rows: list[dict[str, Any]] = []
    for image_id in image_ids:
        baseline_count = baseline_counts.get(image_id, 0)
        primary_count = primary_counts.get(image_id, 0)
        secondary_count = secondary_counts.get(image_id, 0) if secondary_counts is not None else None
        if secondary_counts is not None:
            if secondary_count is None:
                raise TypeError(f"Missing defended count for ranked image: {image_id}")
            target_count = secondary_count
        else:
            target_count = primary_count
        ranked_rows.append(
            {
                "image_id": image_id,
                "baseline_count": baseline_count,
                "attack_count": primary_count,
                "defended_count": secondary_count,
                "rank_gap": baseline_count - target_count,
            }
        )
    ranked_rows.sort(key=lambda row: (-int(row["rank_gap"]), row["image_id"]))
    return ranked_rows


def _render_visual_section(
    *,
    title: str,
    rows: list[dict[str, Any]],
    output_path: Path,
    clean_dir: Path | None,
    attack_dir: Path,
    defended_dir: Path | None = None,
) -> str:
    cards: list[str] = [f"<h2>{html.escape(title)}</h2>"]
    for row in rows:
        clean_href = _relative_href(output_path, clean_dir / row["image_id"] if clean_dir is not None else None)
        attack_href = _relative_href(output_path, attack_dir / row["image_id"])
        defended_href = (
            _relative_href(output_path, defended_dir / row["image_id"])
            if defended_dir is not None
            else None
        )
        metrics = [
            _metric_line("Image", row["image_id"]),
            _metric_line("Baseline", row["baseline_count"]),
            _metric_line("Attack", row["attack_count"]),
        ]
        if row["defended_count"] is not None:
            metrics.append(_metric_line("Defended", row["defended_count"]))
        metrics.append(_metric_line("Gap", row["rank_gap"]))

        cells = [
            _image_cell("Clean", clean_href),
            _image_cell("Attacked", attack_href),
        ]
        if defended_dir is not None:
            cells.append(_image_cell("Defended", defended_href))

        cards.append(
            '<article class="card">'
            '<div class="images">'
            f"{''.join(cells)}"
            "</div>"
            '<div class="metrics">'
            f"{''.join(metrics)}"
            "</div>"
            "</article>"
        )
    return "\n".join(cards)


def _render_text_section(title: str, rows: list[dict[str, Any]], *, include_defended: bool) -> str:
    header = (
        "| image_id | baseline_count | attack_count | defended_count | gap |"
        if include_defended
        else "| image_id | baseline_count | attack_count | gap |"
    )
    separator = (
        "|---|---:|---:|---:|---:|"
        if include_defended
        else "|---|---:|---:|---:|"
    )
    lines = [f"<h2>{html.escape(title)}</h2>", "<pre>", header, separator]
    for row in rows:
        if include_defended:
            lines.append(
                f"| {row['image_id']} | {row['baseline_count']} | {row['attack_count']} | "
                f"{row['defended_count']} | {row['rank_gap']} |"
            )
        else:
            lines.append(
                f"| {row['image_id']} | {row['baseline_count']} | {row['attack_count']} | {row['rank_gap']} |"
            )
    lines.append("</pre>")
    return "\n".join(lines)


def generate_failure_gallery(
    *,
    runs_root: Path,
    output_path: Path,
    max_images: int = 20,
) -> Path:
    runs_root = runs_root.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    baseline, attack_runs, defended_runs, excluded_defended_counts = _select_records(runs_root)
    baseline_counts = _load_detection_counts(baseline.run_dir / "predictions.jsonl") if baseline else {}
    clean_dir = _baseline_source_dir(baseline)
    visual_enabled = any(
        _has_prepared_images(record)
        for record in [
            *attack_runs.values(),
            *(record for record, _ in defended_runs),
        ]
    )

    sections: list[str] = []
    for attack_name in sorted(attack_runs):
        record = attack_runs[attack_name]
        attack_counts = _load_detection_counts(record.run_dir / "predictions.jsonl")
        ranked_rows = _rank_rows(baseline_counts, attack_counts)[:max_images]
        if not ranked_rows:
            continue
        title = f"Attack Only: {attack_name} ({record.run_name})"
        if visual_enabled:
            sections.append(
                _render_visual_section(
                    title=title,
                    rows=ranked_rows,
                    output_path=output_path,
                    clean_dir=clean_dir,
                    attack_dir=record.run_dir / "images",
                )
            )
        else:
            sections.append(_render_text_section(title, ranked_rows, include_defended=False))

    for record, attack_record in defended_runs:
        attack_name = normalize_name(record.attack)
        defense_name = normalize_name(record.defense)
        attack_counts = _load_detection_counts(attack_record.run_dir / "predictions.jsonl")
        defended_counts = _load_detection_counts(record.run_dir / "predictions.jsonl")
        ranked_rows = _rank_rows(baseline_counts, attack_counts, secondary_counts=defended_counts)[:max_images]
        if not ranked_rows:
            continue
        title = f"Defended: {attack_name} + {defense_name} ({record.run_name})"
        if visual_enabled:
            sections.append(
                _render_visual_section(
                    title=title,
                    rows=ranked_rows,
                    output_path=output_path,
                    clean_dir=clean_dir,
                    attack_dir=(attack_record.run_dir / "images") if attack_record is not None else record.run_dir / "images",
                    defended_dir=record.run_dir / "images",
                )
            )
        else:
            sections.append(_render_text_section(title, ranked_rows, include_defended=True))

    if not sections:
        sections.append("<p>No comparable attack or defended runs were found.</p>")

    mode_note = (
        "Visual mode uses relative image paths from source and prepared image directories."
        if visual_enabled
        else "Prepared images were not available; showing text-only ranking tables."
    )
    baseline_note = f"<p>Baseline: <code>{html.escape(baseline.run_name)}</code></p>" if baseline else "<p>Baseline: unavailable</p>"
    warning_block = _comparability_warning_html(excluded_defended_counts)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Failure Gallery</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; background: #f6f7f9; color: #14171a; }}
    h1, h2 {{ margin: 0 0 12px; }}
    p {{ margin: 0 0 12px; }}
    .card {{ background: #fff; border: 1px solid #d9dde3; border-radius: 12px; padding: 16px; margin: 16px 0 24px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .images {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 12px; }}
    .image-cell {{ border: 1px solid #e1e5ea; border-radius: 10px; padding: 10px; background: #fbfcfd; }}
    .image-cell.placeholder {{ display: flex; flex-direction: column; justify-content: center; min-height: 180px; }}
    .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: #5f6b7a; margin-bottom: 8px; }}
    .missing {{ color: #8a94a3; font-size: 14px; }}
    img {{ width: 100%; max-height: 280px; object-fit: contain; display: block; background: #fff; border-radius: 8px; }}
    .metrics {{ display: flex; flex-wrap: wrap; gap: 10px 16px; }}
    .metric span {{ display: block; font-size: 12px; color: #5f6b7a; }}
    .metric strong {{ display: block; font-size: 15px; }}
    .warning {{ background: #fff7e6; border: 1px solid #f0c36d; border-radius: 10px; padding: 12px 14px; margin: 0 0 16px; color: #6b4e16; }}
    pre {{ white-space: pre-wrap; background: #fff; border: 1px solid #d9dde3; border-radius: 12px; padding: 16px; overflow-x: auto; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Failure Gallery</h1>
  <p>{html.escape(mode_note)}</p>
  {baseline_note}
  {warning_block}
  {''.join(sections)}
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")
    return output_path


generate_gallery = generate_failure_gallery


__all__ = [
    "generate_failure_gallery",
    "generate_gallery",
]
