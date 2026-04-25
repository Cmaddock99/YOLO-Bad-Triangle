from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from lab.eval.derived_metrics import compute_normalized_defense_recovery

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.32.0.min.js"
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

ATTACK_COLORS = {
    "fgsm": "#4C72B0",
    "pgd": "#DD8452",
    "deepfool": "#C44E52",
    "blur": "#55A868",
    "gaussian_blur": "#8172B3",
    "bim": "#937860",
    "ifgsm": "#DA8BC3",
    "pretrained_patch": "#CCB974",
}

DEFENSE_COLORS = {
    "blind_patch_recover": "#4CB391",
    "c_dog": "#E377C2",
    "median_preprocess": "#7F7F7F",
    "oracle_patch_recover": "#17BECF",
    "none": "#BCBD22",
}

DEFENSE_LABELS = {
    "blind_patch_recover": "Blind Patch Recover",
    "c_dog": "DPC-UNet (c_dog)",
    "median_preprocess": "Median Filter",
    "oracle_patch_recover": "Oracle Patch Recover (upper bound)",
    "none": "Undefended",
}
_PHASE_PRIORITY = {
    "phase4": 0,
    "phase2": 1,
    "phase1": 2,
    "phase3": 3,
    "manual": 4,
}


def _attack_color(attack: str) -> str:
    return ATTACK_COLORS.get(attack, "#999999")


def _defense_color(defense: str) -> str:
    return DEFENSE_COLORS.get(defense, "#999999")


def _defense_label(defense: str) -> str:
    return DEFENSE_LABELS.get(defense, defense)


def _sweep_label(sweep_dir: str) -> str:
    """Convert sweep_20260321T183700Z -> Mar 21 17:37."""
    match = re.search(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})", sweep_dir)
    if match:
        _, mo, day, hr, mn = match.groups()
        return f"{MONTHS[int(mo)]} {int(day)} {hr}:{mn}"
    match = re.search(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})", sweep_dir)
    if match:
        _, mo, day, hr, mn = match.groups()
        return f"{MONTHS[int(mo)]} {int(day)} {hr}:{mn}"
    return sweep_dir


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


def _parse_generated_at(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _shared_value(values: list[object]) -> str:
    normalized = [str(value).strip() for value in values if str(value).strip()]
    if not normalized:
        return "unknown"
    if len(set(normalized)) == 1:
        return normalized[0]
    return "mixed"


def _shared_row_value(rows: list[dict[str, str]], key: str) -> str:
    return _shared_value([row.get(key) for row in rows])


def _manifest_for_report(report_dir: Path) -> dict[str, Any]:
    return _read_json_mapping(report_dir / "sweep_manifest.json")


def _report_sort_key(report_dir: Path) -> tuple[float, str]:
    manifest = _manifest_for_report(report_dir)
    generated_at = _parse_generated_at(manifest.get("generated_at"))
    timestamp = generated_at.timestamp() if generated_at is not None else report_dir.stat().st_mtime
    return (timestamp, report_dir.name)


def _label_for_identifier(raw_identifier: str, *, fallback: str) -> str:
    pretty = _sweep_label(raw_identifier)
    return pretty if pretty != raw_identifier else fallback


def _resolve_report_dirs(
    *,
    reports_root: Path | None,
    report_dirs: list[Path] | None = None,
) -> list[Path]:
    explicit_dirs = [path.expanduser().resolve() for path in (report_dirs or [])]
    if explicit_dirs:
        unique_dirs: dict[str, Path] = {}
        for report_dir in explicit_dirs:
            unique_dirs[str(report_dir)] = report_dir
        return sorted(unique_dirs.values(), key=_report_sort_key)

    if reports_root is None:
        return []
    root = reports_root.expanduser().resolve()
    if not root.exists():
        return []

    discovered = [
        child
        for child in root.iterdir()
        if child.is_dir() and (child / "framework_run_summary.csv").is_file()
    ]
    return sorted(discovered, key=_report_sort_key)


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _attack_instance_key(attack: object, attack_artifact: object, placement_mode: object) -> str:
    attack_name = _normalize_text(attack) or "unknown"
    artifact = str(attack_artifact or "").strip()
    placement = str(placement_mode or "").strip()
    if attack_name == "pretrained_patch" and (artifact or placement):
        return "|".join(part for part in (attack_name, artifact, placement) if part)
    return attack_name


def _attack_instance_label(attack: object, attack_artifact: object, placement_mode: object) -> str:
    attack_name = str(attack or "").strip() or "unknown"
    artifact = str(attack_artifact or "").strip()
    placement = str(placement_mode or "").strip()
    if _normalize_text(attack) == "pretrained_patch" and (artifact or placement):
        if artifact and placement:
            return f"{artifact} ({placement})"
        return artifact or placement or attack_name
    return attack_name


def _authority_priority(value: object) -> int:
    normalized = _normalize_text(value)
    if normalized == "authoritative":
        return 0
    if normalized == "diagnostic":
        return 1
    return 2


def _phase_priority(value: object) -> int:
    return _PHASE_PRIORITY.get(_normalize_text(value), len(_PHASE_PRIORITY))


def _validation_priority(row: dict[str, str]) -> int:
    status = _normalize_text(row.get("validation_status"))
    if status == "complete":
        return 0
    if str(row.get("mAP50") or "").strip():
        return 1
    return 2


def _row_selection_key(row: dict[str, str]) -> tuple[int, int, int, str]:
    return (
        _authority_priority(row.get("authority")),
        _validation_priority(row),
        _phase_priority(row.get("source_phase")),
        str(row.get("run_name") or ""),
    )


def _dedupe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (
            _normalize_text(row.get("model")),
            str(row.get("seed") or ""),
            _normalize_text(row.get("attack")),
            _normalize_text(row.get("defense")),
            str(row.get("attack_artifact") or "").strip(),
            str(row.get("placement_mode") or "").strip(),
        )
        grouped.setdefault(key, []).append(row)
    deduped: list[dict[str, str]] = []
    for key in sorted(grouped):
        deduped.append(min(grouped[key], key=_row_selection_key))
    return deduped


def _load_sweep(report_dir: Path) -> dict[str, Any] | None:
    """Load a single sweep's CSV into a list of row dicts. Returns None if unusable."""
    csv_path = report_dir / "framework_run_summary.csv"
    if not csv_path.is_file():
        return None
    rows = []
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append(row)
    if not rows:
        return None
    rows = _dedupe_rows(rows)

    baseline_candidates = [
        row
        for row in rows
        if _normalize_text(row.get("attack")) in {"", "none"} and _normalize_text(row.get("defense")) in {"", "none"}
    ]
    baseline = min(baseline_candidates, key=_row_selection_key) if baseline_candidates else None
    if not baseline or not baseline.get("total_detections"):
        return None
    baseline_det = float(baseline["total_detections"])
    manifest = _manifest_for_report(report_dir)
    raw_identifier = str(manifest.get("sweep_id") or report_dir.name).strip() or report_dir.name

    runs = []
    for row in rows:
        try:
            det = float(row["total_detections"])
        except (ValueError, TypeError):
            continue
        drop = (baseline_det - det) / baseline_det if baseline_det else 0
        source_phase = _normalize_text(row.get("source_phase"))
        map50_authoritative = source_phase == "phase4"
        attack_artifact = str(row.get("attack_artifact") or "").strip()
        placement_mode = str(row.get("placement_mode") or "").strip()
        runs.append({
            "run_name": row["run_name"],
            "attack": row["attack"],
            "attack_key": _attack_instance_key(row.get("attack"), attack_artifact, placement_mode),
            "attack_label": _attack_instance_label(row.get("attack"), attack_artifact, placement_mode),
            "attack_artifact": attack_artifact,
            "placement_mode": placement_mode,
            "defense": row["defense"],
            "total_detections": det,
            "avg_confidence": float(row["avg_confidence"]) if row.get("avg_confidence") else None,
            "detection_drop": round(drop * 100, 1),
            "mAP50": float(row["mAP50"]) if row.get("mAP50") and map50_authoritative else None,
            "source_phase": source_phase or "unknown",
        })

    return {
        "sweep": raw_identifier,
        "label": _label_for_identifier(raw_identifier, fallback=report_dir.name),
        "report_dir": str(report_dir),
        "pipeline_profile": (
            _shared_row_value(rows, "pipeline_profile")
            if _shared_row_value(rows, "pipeline_profile") != "unknown"
            else str(manifest.get("pipeline_profile") or "").strip() or "unknown"
        ),
        "model": _shared_row_value(rows, "model"),
        "baseline_detections": baseline_det,
        "runs": runs,
        "generated_at": _parse_generated_at(manifest.get("generated_at")),
    }


def _build_heatmap_data(
    sweep: dict[str, Any],
) -> tuple[list[str], list[str], list[list[float | None]], list[list[str]]]:
    """Return attacks, defenses, z-matrix, text-matrix for the heatmap."""
    defended = [row for row in sweep["runs"] if row["defense"] not in ("none", "")]
    if not defended:
        return [], [], [], []

    attack_labels_by_key: dict[str, str] = {}
    for row in defended:
        attack_labels_by_key[str(row["attack_key"])] = str(row["attack_label"])
    attack_keys = sorted(attack_labels_by_key, key=lambda key: attack_labels_by_key[key])
    attacks = [attack_labels_by_key[key] for key in attack_keys]
    defenses = sorted({str(row["defense"]) for row in defended})

    z: list[list[float | None]] = []
    text: list[list[str]] = []
    for defense in defenses:
        row_z: list[float | None] = []
        row_t: list[str] = []
        for attack_key in attack_keys:
            match = next(
                (
                    row
                    for row in defended
                    if str(row["attack_key"]) == attack_key and row["defense"] == defense
                ),
                None,
            )
            if match:
                row_z.append(cast(float | None, match.get("detection_drop")))
                row_t.append(
                    f"{match['detection_drop']}%<br>{int(match['total_detections'])} detections"
                )
            else:
                row_z.append(None)
                row_t.append("n/a")
        z.append(row_z)
        text.append(row_t)

    defense_labels = [_defense_label(defense) for defense in defenses]
    return attacks, defense_labels, z, text


def _build_trend_data(sweeps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build one trace per attack+defense combo showing detection drop over time."""
    combos: set[tuple[str, str, str, str]] = set()
    for sweep in sweeps:
        for row in sweep["runs"]:
            if row["defense"] not in ("none", ""):
                combos.add(
                    (
                        str(row["attack_key"]),
                        str(row["attack_label"]),
                        str(row["attack"]),
                        str(row["defense"]),
                    )
                )

    traces = []
    for attack_key, attack_label, attack_name, defense in sorted(combos):
        x, y = [], []
        for sweep in sweeps:
            match = next(
                (
                    row
                    for row in sweep["runs"]
                    if str(row["attack_key"]) == attack_key and row["defense"] == defense
                ),
                None,
            )
            if match:
                x.append(sweep["label"])
                y.append(match["detection_drop"])
        if len(x) < 1:
            continue
        traces.append({
            "x": x,
            "y": y,
            "name": f"{attack_label} + {_defense_label(defense)}",
            "mode": "lines+markers",
            "line": {"color": _attack_color(attack_name), "width": 2},
            "marker": {"size": 8, "symbol": "circle" if defense == "c_dog" else "square"},
        })
    return traces


def _build_attack_bar_data(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    """Bar chart of undefended attack detection drops."""
    attacked = [row for row in sweep["runs"] if row["attack"] != "none" and row["defense"] in ("none", "")]
    return [
        {
            "x": [row["attack_label"] for row in attacked],
            "y": [row["detection_drop"] for row in attacked],
            "type": "bar",
            "marker": {"color": [_attack_color(row["attack"]) for row in attacked]},
            "text": [f"{row['detection_drop']}%" for row in attacked],
            "textposition": "outside",
        }
    ]


def _summary_cards_html(sweeps: list[dict[str, Any]]) -> str:
    latest = sweeps[-1]
    defended = [row for row in latest["runs"] if row["defense"] not in ("none", "")]
    best = min(
        defended,
        key=lambda row: row["detection_drop"] if row["detection_drop"] is not None else float("inf"),
    ) if defended else None
    effective_attacks = [
        row
        for row in latest["runs"]
        if row["attack"] != "none" and row["defense"] in ("none", "")
        and row["detection_drop"] is not None and row["detection_drop"] > 0
    ]
    worst_attack = max(
        effective_attacks,
        key=lambda row: row["detection_drop"],
        default=None,
    )

    def card(title: str, value: str, sub: str = "", color: str = "#4C72B0") -> str:
        return f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value" style="color:{color}">{value}</div>
            <div class="card-sub">{sub}</div>
        </div>"""

    cards = [
        card("Total Sweeps", str(len(sweeps)), "runs recorded"),
        card("Baseline Detections", str(int(latest["baseline_detections"])),
             "clean images, no attack", "#2ca02c"),
        card("Strongest Attack", str(worst_attack.get("attack_label") or worst_attack.get("attack") or "unknown").upper() if worst_attack else "NO_EFFECTIVE_ATTACK",
             f"−{worst_attack['detection_drop']}% detections" if worst_attack else "all attacks had 0.0% drop",
             "#C44E52"),
        card("Best Defense (latest)", best["defense"] if best else "—",
             f"vs {best.get('attack_label') or best.get('attack')}: −{best['detection_drop']}%" if best else "",
             "#E377C2"),
    ]
    return '<div class="cards">' + "".join(cards) + "</div>"


def _fmt_count(value: object) -> str:
    if value is None:
        return "—"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "—"
    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:.1f}"


def _fmt_ratio_pct(value: object) -> str:
    if value is None:
        return "—"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{numeric * 100:.1f}%"


def _build_imported_patch_comparison_rows(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    defense_order = ("none", "blind_patch_recover", "oracle_patch_recover")
    groups: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for row in sweep["runs"]:
        if _normalize_text(row.get("attack")) != "pretrained_patch":
            continue
        artifact = str(row.get("attack_artifact") or "").strip()
        placement = str(row.get("placement_mode") or "").strip()
        if not (artifact or placement):
            continue
        groups.setdefault((artifact, placement), {})[_normalize_text(row.get("defense"))] = row

    rendered_rows: list[dict[str, Any]] = []
    baseline_det = sweep["baseline_detections"]
    for artifact, placement in sorted(groups):
        group = groups[(artifact, placement)]
        attack_row = group.get("none")
        if attack_row is None:
            continue
        attack_det = cast(float | None, attack_row.get("total_detections"))
        oracle_row = group.get("oracle_patch_recover")
        oracle_det = cast(float | None, oracle_row.get("total_detections")) if oracle_row else None
        oracle_recovery = compute_normalized_defense_recovery(baseline_det, attack_det, oracle_det)
        for defense_name in defense_order:
            row = group.get(defense_name)
            defended_det = (
                cast(float | None, row.get("total_detections"))
                if row is not None
                else (attack_det if defense_name == "none" else None)
            )
            recovery = compute_normalized_defense_recovery(baseline_det, attack_det, defended_det)
            gap_to_oracle = (
                oracle_recovery - recovery
                if oracle_recovery is not None and recovery is not None
                else None
            )
            rendered_rows.append(
                {
                    "artifact": artifact,
                    "placement_mode": placement,
                    "defense": defense_name,
                    "total_detections": defended_det,
                    "detection_drop": row.get("detection_drop") if row is not None else None,
                    "recovery_over_undefended": recovery,
                    "gap_to_oracle": gap_to_oracle,
                    "avg_confidence": row.get("avg_confidence") if row is not None else None,
                }
            )
    return rendered_rows


def _imported_patch_table_html(sweep: dict[str, Any]) -> str:
    rows = _build_imported_patch_comparison_rows(sweep)
    if not rows:
        return ""

    body = ""
    for row in rows:
        drop = row["detection_drop"]
        drop_text = "—" if drop is None else f"{float(drop):.1f}%"
        body += f"""
        <tr>
            <td>{row['artifact'] or '—'}</td>
            <td>{row['placement_mode'] or '—'}</td>
            <td><span class="badge defense">{_defense_label(str(row['defense']))}</span></td>
            <td>{_fmt_count(row['total_detections'])}</td>
            <td>{drop_text}</td>
            <td>{_fmt_ratio_pct(row['recovery_over_undefended'])}</td>
            <td>{_fmt_ratio_pct(row['gap_to_oracle'])}</td>
            <td>{round(cast(float, row['avg_confidence']), 4) if row['avg_confidence'] is not None else '—'}</td>
        </tr>"""
    return f"""
    <table>
        <thead>
            <tr>
                <th>Artifact</th><th>Placement</th><th>Defense</th>
                <th>Detections</th><th>Detection Drop</th>
                <th>Recovery Over Undefended</th><th>Gap To Oracle</th><th>Avg Confidence</th>
            </tr>
        </thead>
        <tbody>{body}</tbody>
    </table>"""


def _run_table_html(sweep: dict[str, Any]) -> str:
    rows_html = ""
    defended = sorted(
        [row for row in sweep["runs"] if row["defense"] not in ("none", "")],
        key=lambda row: row["detection_drop"],
    )
    for row in defended:
        drop = row["detection_drop"]
        color = "#c0392b" if drop > 60 else "#e67e22" if drop > 30 else "#27ae60"
        rows_html += f"""
        <tr>
            <td><span class="badge attack">{row['attack_label']}</span></td>
            <td><span class="badge defense">{_defense_label(row['defense'])}</span></td>
            <td style="color:{color}; font-weight:600">{drop}%</td>
            <td>{int(row['total_detections'])}</td>
            <td>{round(row['avg_confidence'], 4) if row['avg_confidence'] else '—'}</td>
        </tr>"""
    return f"""
    <table>
        <thead>
            <tr>
                <th>Attack</th><th>Defense</th>
                <th>Detection Drop</th><th>Detections</th><th>Avg Confidence</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>"""


def generate_dashboard(
    reports_root: Path | None,
    output: Path,
    *,
    report_dirs: list[Path] | None = None,
    compat_output: Path | None = None,
    no_pages: bool = False,
) -> None:
    """Render the local dashboard and optionally mirror it to a compat output."""
    sweep_dirs = _resolve_report_dirs(reports_root=reports_root, report_dirs=report_dirs)
    sweeps = []
    for report_dir in sweep_dirs:
        sweep = _load_sweep(report_dir)
        if sweep:
            sweeps.append(sweep)

    if not sweeps:
        raise RuntimeError(f"No usable sweep data found under {reports_root}")

    latest = sweeps[-1]
    attacks, defense_labels, z, text = _build_heatmap_data(latest)
    trend_traces = _build_trend_data(sweeps)
    attack_bars = _build_attack_bar_data(latest)
    latest_generated_at = latest.get("generated_at")
    if isinstance(latest_generated_at, datetime):
        if latest_generated_at.tzinfo is None:
            latest_generated_at = latest_generated_at.replace(tzinfo=timezone.utc)
        generated_at = latest_generated_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pipeline_profile = _shared_value([sweep.get("pipeline_profile") for sweep in sweeps])
    model_name = _shared_value([sweep.get("model") for sweep in sweeps])

    heatmap_json = json.dumps([{
        "type": "heatmap",
        "x": attacks,
        "y": defense_labels,
        "z": z,
        "text": text,
        "hovertemplate": "<b>%{x}</b> + <b>%{y}</b><br>Drop: %{z}%<extra></extra>",
        "colorscale": [[0, "#27ae60"], [0.5, "#f39c12"], [1, "#c0392b"]],
        "zmin": 0,
        "zmax": 100,
        "showscale": True,
        "colorbar": {"title": "Detection Drop %"},
        "texttemplate": "%{text}",
        "textfont": {"size": 12, "color": "white"},
    }])

    trend_json = json.dumps(trend_traces)
    attack_bar_json = json.dumps(attack_bars)
    imported_patch_section = ""
    imported_patch_table = _imported_patch_table_html(latest)
    if imported_patch_table:
        imported_patch_section = f"""
<h2>Imported Patch Comparisons — Latest Sweep</h2>
<div class="chart-box" style="overflow-x:auto">
  {imported_patch_table}
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YOLO Adversarial Robustness Dashboard</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e0e0e0; padding: 24px; }}
  h1 {{ font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; }}
  .subtitle {{ color: #888; font-size: 0.85rem; margin-bottom: 28px; }}
  h2 {{ font-size: 1.1rem; font-weight: 600; color: #ccc; margin: 32px 0 12px; }}
  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }}
  .card {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
           padding: 18px 24px; min-width: 180px; flex: 1; }}
  .card-title {{ font-size: 0.75rem; color: #888; text-transform: uppercase;
                 letter-spacing: 0.05em; margin-bottom: 6px; }}
  .card-value {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }}
  .card-sub {{ font-size: 0.78rem; color: #666; }}
  .chart-box {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
                padding: 20px; margin-bottom: 20px; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ text-align: left; padding: 10px 14px; color: #888; font-weight: 500;
        border-bottom: 1px solid #2a2d3a; text-transform: uppercase;
        font-size: 0.75rem; letter-spacing: 0.05em; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #1e2130; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #20243a; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 0.78rem; font-weight: 600; }}
  .badge.attack {{ background: #1e2a40; color: #7aabff; }}
  .badge.defense {{ background: #2a1e3a; color: #d4a6ff; }}
  @media (max-width: 800px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
  details {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
             padding: 18px 24px; margin-bottom: 28px; }}
  summary {{ font-size: 0.95rem; font-weight: 600; color: #aaa; cursor: pointer;
             letter-spacing: 0.02em; list-style: none; display: flex;
             align-items: center; gap: 8px; }}
  summary::before {{ content: "▶"; font-size: 0.7rem; color: #555;
                     transition: transform 0.2s; }}
  details[open] summary::before {{ transform: rotate(90deg); }}
  summary::-webkit-details-marker {{ display: none; }}
  .context p {{ color: #999; font-size: 0.88rem; line-height: 1.75;
                margin-bottom: 12px; max-width: 860px; }}
  .context p:last-child {{ margin-bottom: 0; }}
  .context strong {{ color: #ccc; font-weight: 600; }}
  .glossary {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 32px;
               margin-top: 14px; }}
  .glossary dt {{ color: #7aabff; font-size: 0.82rem; font-weight: 600;
                  margin-bottom: 2px; }}
  .glossary dd {{ color: #888; font-size: 0.82rem; line-height: 1.5;
                  margin-bottom: 8px; }}
  @media (max-width: 800px) {{
    .two-col {{ grid-template-columns: 1fr; }}
    .glossary {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<h1>YOLO Adversarial Robustness Dashboard</h1>
<div class="subtitle">Pipeline profile: {pipeline_profile} &nbsp;·&nbsp; Model: {model_name}
  &nbsp;·&nbsp; {len(sweeps)} report(s) &nbsp;·&nbsp; Generated: {generated_at}</div>

<details>
  <summary>About this research</summary>
  <div class="context" style="margin-top:16px">
    <p>
      This dashboard tracks an ongoing research programme testing the <strong>reliability of
      AI-based object detection</strong> under deliberate interference — and evaluating methods
      to restore that reliability.
    </p>
    <p>
      The AI system under study — a computer vision model called YOLO — is trained to identify
      objects in photographs: people, vehicles, animals, and hundreds of other categories. In
      normal conditions it performs with high accuracy. The question this research asks is:
      <strong>how easily can that accuracy be undermined, and can it be protected?</strong>
    </p>
    <p>
      The interference method is called an <strong>adversarial attack</strong>. An attacker
      makes mathematically precise, often imperceptible changes to the pixels of an image —
      changes invisible to the human eye — that cause the AI to miss objects it would otherwise
      detect with confidence. This is not a theoretical concern: the same class of models
      underpins real-world systems in autonomous vehicles, medical imaging, and security
      infrastructure.
    </p>
    <p>
      Each experiment runs 500 unmodified photographs through the model to establish a
      <strong>baseline</strong> (how many objects it finds under normal conditions), then repeats
      the process on versions of those same images that have been subjected to each attack. The
      percentage drop in detections is the primary measure of an attack's severity.
    </p>
    <p>
      The <strong>defenses</strong> are pre-processing steps applied to attacked images before
      the model sees them — essentially attempting to reverse or neutralise the interference.
      The central defense under development here (DPC-UNet) is a purpose-trained neural network
      that has been iteratively fine-tuned across multiple experimental rounds to better preserve
      the visual detail the model relies on for detection. The trend charts below reflect that
      improvement over time.
    </p>
    <dl class="glossary">
      <dt>Detection Drop</dt>
      <dd>The percentage reduction in objects identified compared to unmodified images.
          Lower is better. A 90% drop means the model missed 9 in 10 objects it would
          normally find.</dd>
      <dt>Baseline</dt>
      <dd>The model's performance on clean, unaltered photographs — the reference point
          against which all attacks and defenses are measured.</dd>
      <dt>FGSM / PGD / Blur</dt>
      <dd>Relatively mild attack methods that cause 12–17% detection loss. The model
          retains most of its capability under these conditions.</dd>
      <dt>DeepFool</dt>
      <dd>A precision attack that identifies the mathematically minimal pixel change
          sufficient to cause failure. Consistently the most damaging attack tested,
          causing up to 78% detection loss without a defense.</dd>
      <dt>DPC-UNet (c_dog)</dt>
      <dd>The primary defense under development — a neural network trained to reconstruct
          attacked images before the detector sees them. Performance improves with each
          fine-tuning iteration.</dd>
      <dt>Median Filter</dt>
      <dd>A classical signal-processing defense that smooths irregular pixel patterns.
          Simpler than the neural approach and currently more effective against mild
          attacks, though less adaptable.</dd>
    </dl>
  </div>
</details>

{_summary_cards_html(sweeps)}

<h2>Latest Sweep — Defense Heatmap ({latest['label']})</h2>
<div class="chart-box">
  <div id="heatmap" style="height:320px"></div>
</div>

<div class="two-col">
  <div>
    <h2>Attack Effectiveness (Undefended)</h2>
    <div class="chart-box">
      <div id="attack-bars" style="height:300px"></div>
    </div>
  </div>
  <div>
    <h2>Defense Recovery — Latest Sweep</h2>
    <div class="chart-box" style="overflow-x:auto">
      {_run_table_html(latest)}
    </div>
  </div>
</div>

{imported_patch_section}

<h2>Detection Drop Over Time — All Sweeps</h2>
<div class="chart-box">
  <div id="trend" style="height:380px"></div>
</div>

<script>
const dark = {{
  paper_bgcolor: "#1a1d27",
  plot_bgcolor: "#1a1d27",
  font: {{ color: "#cccccc", family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }},
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  margin: {{ t: 20, r: 20, b: 50, l: 140 }},
}};

Plotly.newPlot("heatmap", {heatmap_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 120, b: 60, l: 160 }},
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Attack" }}),
    yaxis: Object.assign({{}}, dark.yaxis, {{ title: "" }}),
  }}),
  {{responsive: true, displayModeBar: false}}
);

Plotly.newPlot("attack-bars", {attack_bar_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 20, b: 50, l: 60 }},
    yaxis: Object.assign({{}}, dark.yaxis, {{
      title: "Detection Drop %", range: [0, 100]
    }}),
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Attack" }}),
    showlegend: false,
  }}),
  {{responsive: true, displayModeBar: false}}
);

Plotly.newPlot("trend", {trend_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 20, b: 60, l: 60 }},
    yaxis: Object.assign({{}}, dark.yaxis, {{
      title: "Detection Drop %", range: [0, 105]
    }}),
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Sweep" }}),
    legend: {{ bgcolor: "#1a1d27", bordercolor: "#2a2d3a", borderwidth: 1 }},
    hovermode: "x unified",
  }}),
  {{responsive: true, displayModeBar: false}}
);
</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {output}")
    if compat_output is not None:
        compat_output = compat_output.expanduser().resolve()
        if compat_output != output:
            compat_output.parent.mkdir(parents=True, exist_ok=True)
            compat_output.write_text(html, encoding="utf-8")
            print(f"  Compatibility: {compat_output}")

    pages_out = Path("docs/index.html").resolve()
    if not no_pages and output != pages_out:
        pages_out.parent.mkdir(parents=True, exist_ok=True)
        pages_out.write_text(html, encoding="utf-8")
        print(f"  GitHub Pages:  {pages_out}")
    print(f"  Sweeps loaded: {len(sweeps)}")
    print(f"  Latest sweep:  {latest['label']} ({latest['sweep']})")


generate = generate_dashboard


__all__ = [
    "generate_dashboard",
    "generate",
]
