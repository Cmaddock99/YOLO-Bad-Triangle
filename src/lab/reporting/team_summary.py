from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any

from lab.eval.framework_metrics import is_validation_success
from .framework_comparison import is_none_like, normalize_name


_AUTHORITY_AUTHORITATIVE = "authoritative"
_AUTHORITY_DIAGNOSTIC = "diagnostic"
_RUN_ROLE_ATTACK_ONLY = "attack_only"
_RUN_ROLE_BASELINE = "baseline"
_PHASE_PRIORITY = {
    "phase4": 0,
    "phase2": 1,
    "phase1": 2,
    "phase3": 3,
    "manual": 4,
}


def _to_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def _normalize_optional_text(value: object) -> str | None:
    normalized = normalize_name(value)
    return normalized or None


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _infer_run_role(*, attack: str, defense: str) -> str | None:
    if is_none_like(attack) and is_none_like(defense):
        return _RUN_ROLE_BASELINE
    if not is_none_like(attack) and is_none_like(defense):
        return _RUN_ROLE_ATTACK_ONLY
    if not is_none_like(attack) and not is_none_like(defense):
        return "defended"
    return None


def _load_row_context(row: dict[str, str]) -> dict[str, str | None]:
    attack_name = normalize_name(row.get("attack"))
    defense_name = normalize_name(row.get("defense"))
    inferred_run_role = _infer_run_role(attack=attack_name, defense=defense_name)

    run_dir_raw = str(row.get("run_dir") or "").strip()
    summary: dict[str, Any] = {}
    if run_dir_raw:
        summary = _read_json_mapping(Path(run_dir_raw).expanduser().resolve() / "run_summary.json")
    reporting_context = summary.get("reporting_context")
    if not isinstance(reporting_context, dict):
        reporting_context = {}

    run_role = (
        _normalize_optional_text(row.get("run_role"))
        or _normalize_optional_text(reporting_context.get("run_role"))
        or inferred_run_role
    )
    authority = _normalize_optional_text(row.get("authority")) or _normalize_optional_text(
        reporting_context.get("authority")
    )
    source_phase = _normalize_optional_text(row.get("source_phase")) or _normalize_optional_text(
        reporting_context.get("source_phase")
    )
    dataset_scope = _normalize_optional_text(row.get("dataset_scope")) or _normalize_optional_text(
        reporting_context.get("dataset_scope")
    )
    return {
        "run_role": run_role,
        "authority": authority,
        "source_phase": source_phase,
        "dataset_scope": dataset_scope,
        "pipeline_profile": _optional_text(row.get("pipeline_profile")) or _optional_text(summary.get("pipeline_profile")),
        "authoritative_metric": _optional_text(row.get("authoritative_metric")) or _optional_text(
            summary.get("authoritative_metric")
        ),
    }


def _enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        attack_name = normalize_name(row.get("attack"))
        defense_name = normalize_name(row.get("defense"))
        row_context = _load_row_context(row)
        enriched.append(
            {
                **row,
                "attack": attack_name,
                "defense": defense_name,
                "seed": _to_optional_float(row.get("seed")),
                "total_detections": _to_optional_float(row.get("total_detections")),
                "avg_confidence": _to_optional_float(row.get("avg_confidence")),
                "validation_status": str(row.get("validation_status") or ""),
                "map50": _to_optional_float(row.get("mAP50")),
                "_run_role": row_context["run_role"],
                "_authority": row_context["authority"],
                "_source_phase": row_context["source_phase"],
                "_dataset_scope": row_context["dataset_scope"],
                "_pipeline_profile": row_context["pipeline_profile"],
                "_authoritative_metric": row_context["authoritative_metric"],
            }
        )
    return enriched


def _authority_priority(value: object) -> int:
    normalized = normalize_name(value)
    if normalized == _AUTHORITY_AUTHORITATIVE:
        return 0
    if normalized == _AUTHORITY_DIAGNOSTIC:
        return 1
    return 2


def _phase_priority(value: object) -> int:
    normalized = normalize_name(value)
    return _PHASE_PRIORITY.get(normalized, len(_PHASE_PRIORITY))


def _selection_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        _authority_priority(row.get("_authority")),
        0 if is_validation_success(row.get("validation_status")) else 1,
        _phase_priority(row.get("_source_phase")),
        str(row.get("run_name") or ""),
    )


def _shared_value(values: list[object]) -> str | None:
    normalized: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text.lower() == "none":
            continue
        normalized.append(text)
    if not normalized:
        return None
    if len(set(normalized)) == 1:
        return normalized[0]
    return "mixed"


def _context_value(row: dict[str, Any], key: str) -> object:
    value = row.get(key)
    if value is not None:
        return value
    return row.get(f"_{key}")


def _is_ranked_row(row: dict[str, Any]) -> bool:
    return (
        normalize_name(_context_value(row, "authority")) == _AUTHORITY_AUTHORITATIVE
        and is_validation_success(row.get("validation_status"))
    )


def _derive_semantic_status(rows: list[dict[str, Any]]) -> str:
    if rows and all(_is_ranked_row(row) for row in rows):
        return "ranked_result"
    if any(_is_ranked_row(row) for row in rows):
        return "mixed"
    return "diagnostic"


def _build_local_context(rows: list[dict[str, Any]]) -> dict[str, str | None]:
    return {
        "input_scope": "local_report_root",
        "pipeline_profile": _shared_value([_context_value(row, "pipeline_profile") for row in rows]),
        "authority": _shared_value([_context_value(row, "authority") for row in rows]),
        "source_phase": _shared_value([_context_value(row, "source_phase") for row in rows]),
        "dataset_scope": _shared_value([_context_value(row, "dataset_scope") for row in rows]),
        "authoritative_metric": _shared_value([_context_value(row, "authoritative_metric") for row in rows]),
        "semantic_status": _derive_semantic_status(rows),
    }


def _select_best_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Expected at least one candidate row for selection.")
    authoritative = [row for row in rows if normalize_name(row.get("_authority")) == _AUTHORITY_AUTHORITATIVE]
    if authoritative:
        return min(authoritative, key=_selection_key)
    diagnostic = [row for row in rows if normalize_name(row.get("_authority")) == _AUTHORITY_DIAGNOSTIC]
    if diagnostic:
        return min(diagnostic, key=_selection_key)
    return min(rows, key=_selection_key)


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


def _build_attack_rows(rows: list[dict[str, str]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    enriched_rows = _enrich_rows(rows)
    baseline_candidates = [
        row
        for row in enriched_rows
        if is_none_like(row.get("attack")) and is_none_like(row.get("defense"))
    ]
    if not baseline_candidates:
        raise ValueError(
            "Baseline row is required in framework_run_summary.csv "
            "(attack and defense must be none-like values)."
        )
    baseline = _select_best_row(baseline_candidates)
    baseline_detections = _to_optional_float(baseline.get("total_detections"))

    grouped_attack_rows: dict[str, list[dict[str, Any]]] = {}
    for row in enriched_rows:
        attack_name = str(row.get("attack") or "")
        if is_none_like(attack_name) or not is_none_like(row.get("defense")):
            continue
        if normalize_name(row.get("_run_role")) != _RUN_ROLE_ATTACK_ONLY:
            continue
        grouped_attack_rows.setdefault(attack_name, []).append(row)

    attack_rows: list[dict[str, Any]] = []
    for attack_name, candidates in grouped_attack_rows.items():
        selected = _select_best_row(candidates)
        detections = _to_optional_float(selected.get("total_detections"))
        drop = None
        if baseline_detections is not None and baseline_detections != 0.0 and detections is not None:
            drop = (baseline_detections - detections) / baseline_detections
        attack_rows.append(
            {
                "run_name": selected.get("run_name"),
                "attack": attack_name,
                "seed": _to_optional_float(selected.get("seed")),
                "total_detections": detections,
                "avg_confidence": _to_optional_float(selected.get("avg_confidence")),
                "detection_drop": drop,
                "validation_status": selected.get("validation_status", ""),
                "map50": _to_optional_float(selected.get("map50")),
                "authority": selected.get("_authority"),
                "source_phase": selected.get("_source_phase"),
                "dataset_scope": selected.get("_dataset_scope"),
                "pipeline_profile": selected.get("_pipeline_profile"),
                "authoritative_metric": selected.get("_authoritative_metric"),
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
    local_context = _build_local_context([baseline_row, *attack_rows])
    payload = {
        "report_root": str(report_root),
        "local_context": local_context,
        "total_runs": len(rows),
        "total_attack_runs": len(attack_rows),
        "baseline": {
            "run_name": baseline_row.get("run_name"),
            "model": baseline_row.get("model"),
            "seed": _to_optional_float(baseline_row.get("seed")),
            "total_detections": _to_optional_float(baseline_row.get("total_detections")),
            "avg_confidence": _to_optional_float(baseline_row.get("avg_confidence")),
            "validation_status": baseline_row.get("validation_status", ""),
            "authority": baseline_row.get("_authority"),
            "source_phase": baseline_row.get("_source_phase"),
            "dataset_scope": baseline_row.get("_dataset_scope"),
            "pipeline_profile": baseline_row.get("_pipeline_profile"),
            "authoritative_metric": baseline_row.get("_authoritative_metric"),
        },
        "strongest_attack_by_detection_drop": strongest,
        "attacks_ranked": attack_rows,
    }
    return payload


def _build_markdown_provenance(report_root: Path, baseline_row: dict[str, Any]) -> dict[str, str]:
    run_dir_raw = str(baseline_row.get("run_dir") or "").strip()
    summary = _read_json_mapping(Path(run_dir_raw).expanduser().resolve() / "run_summary.json") if run_dir_raw else {}
    if run_dir_raw and not summary:
        print(
            f"WARNING: provenance: run_summary.json not found or unreadable at {run_dir_raw}",
            file=sys.stderr,
        )
    provenance = summary.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    checkpoint_sha = str(provenance.get("checkpoint_fingerprint_sha256") or "").strip()
    checkpoint_source = str(provenance.get("checkpoint_fingerprint_source") or "").strip()
    defense_checkpoints = provenance.get("defense_checkpoints")
    if not isinstance(defense_checkpoints, list):
        defense_checkpoints = []
    defense_checkpoint = next((item for item in defense_checkpoints if isinstance(item, dict)), {})
    defense_sha = str(defense_checkpoint.get("sha256") or "").strip()
    defense_source = str(defense_checkpoint.get("path") or "").strip()

    return {
        "model_checkpoint": (
            f"`{checkpoint_sha[:12]}` (`{checkpoint_source}`)"
            if checkpoint_sha and checkpoint_source
            else "unknown"
        ),
        "defense_checkpoint": (
            f"`{defense_sha[:12]}` (`{defense_source}`)"
            if defense_sha and defense_source
            else "none loaded"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _read_required_json_mapping(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def _build_external_provenance(*, clean_gate_path: Path | None = None) -> dict[str, str]:
    if clean_gate_path is None:
        return {}
    resolved = clean_gate_path.expanduser().resolve()
    clean_gate = _read_required_json_mapping(resolved, label="external clean-gate artifact")
    verdict = str(clean_gate.get("verdict") or "").strip() or "verdict missing"
    return {
        "clean_gate": f"{verdict} ({resolved})",
    }


def render_team_summary_markdown(
    payload: dict[str, Any],
    *,
    provenance: dict[str, str] | None = None,
    external_provenance: dict[str, str] | None = None,
) -> str:
    baseline = payload.get("baseline", {})
    strongest = payload.get("strongest_attack_by_detection_drop") or {}
    attack_rows: list[dict[str, Any]] = list(payload.get("attacks_ranked") or [])
    local_context = payload.get("local_context") or {}
    semantic_status = str(local_context.get("semantic_status") or "diagnostic")
    ranking_is_authoritative = semantic_status == "ranked_result"
    headline_label = "Strongest local attack" if ranking_is_authoritative else "Strongest local diagnostic attack"

    lines = [
        "# Team Summary",
        "",
        "- Summary scope: local report root only",
        f"- Report root: `{payload.get('report_root')}`",
        f"- Pipeline profile: `{local_context.get('pipeline_profile') or 'unknown'}`",
        f"- Authority: `{local_context.get('authority') or 'unknown'}`",
        f"- Source phase: `{local_context.get('source_phase') or 'unknown'}`",
        f"- Semantic status: `{semantic_status}`",
        f"- Dataset scope: `{local_context.get('dataset_scope') or 'unknown'}`",
        f"- Authoritative metric: `{local_context.get('authoritative_metric') or 'unknown'}`",
        f"- Total discovered runs: **{payload.get('total_runs', 0)}**",
        f"- Attack runs analyzed: **{payload.get('total_attack_runs', 0)}**",
        f"- Baseline run: `{baseline.get('run_name')}`",
        "",
    ]
    if not ranking_is_authoritative:
        lines.extend(
            [
                "- Status note: this local summary is diagnostic; mixed, proxy-only, or incomplete validation evidence prevents an authoritative ranked claim.",
                "",
            ]
        )
    if strongest:
        drop = strongest.get("detection_drop")
        drop_text = "n/a" if drop is None else f"{float(drop) * 100:.1f}%"
        lines.extend(
            [
                "## Headline",
                "",
                f"- {headline_label} (by detection drop): `{strongest.get('attack')}` ({drop_text})",
                f"- Interpretation: {strongest.get('interpretation') or 'n/a'}",
                "",
            ]
        )
    lines.extend(
        [
            "## Local Attack Ranking",
            "",
            "| Run | Attack | Det drop | Avg conf | mAP50 | Authority | Phase | Evidence | Interpretation |",
            "|---|---|---:|---:|---:|---|---|---|---|",
        ]
    )
    for row in attack_rows:
        drop = row.get("detection_drop")
        drop_text = "n/a" if drop is None else f"{float(drop) * 100:.1f}%"
        conf = row.get("avg_confidence")
        conf_text = "n/a" if conf is None else f"{float(conf):.4f}"
        map50 = row.get("map50")
        map50_text = "n/a" if map50 is None else f"{float(map50):.4f}"
        v_status = str(row.get("validation_status") or "")
        evidence = "mAP50" if is_validation_success(v_status) else "avg_conf proxy"
        lines.append(
            f"| `{row.get('run_name')}` | `{row.get('attack')}` | "
            f"{drop_text} | {conf_text} | {map50_text} | "
            f"`{row.get('authority') or 'unknown'}` | `{row.get('source_phase') or 'unknown'}` | "
            f"{evidence} | "
            f"{row.get('interpretation') or 'n/a'} |"
        )
    if provenance:
        lines.extend(
            [
                "",
                "## Local Provenance",
                "",
                f"- YOLO checkpoint: {provenance.get('model_checkpoint', 'unknown')}",
                f"- Defense checkpoint: {provenance.get('defense_checkpoint', 'none loaded')}",
                f"- Generated: {provenance.get('generated_at', 'unknown')}",
            ]
        )
    if external_provenance:
        lines.extend(
            [
                "",
                "## External Provenance",
                "",
            ]
        )
        if external_provenance.get("clean_gate"):
            lines.append(f"- Clean gate: {external_provenance['clean_gate']}")
    return "\n".join(lines)


def write_team_summary(
    report_root: Path,
    *,
    external_clean_gate_path: Path | None = None,
) -> tuple[Path, Path]:
    payload = build_team_summary_payload(report_root)
    report_root = report_root.expanduser().resolve()
    rows = _load_summary_csv(report_root / "framework_run_summary.csv")
    baseline_row, _ = _build_attack_rows(rows)
    provenance = _build_markdown_provenance(report_root, baseline_row)
    external_provenance = _build_external_provenance(clean_gate_path=external_clean_gate_path)
    json_path = report_root / "team_summary.json"
    md_path = report_root / "team_summary.md"
    json_tmp = json_path.with_suffix(".json.tmp")
    json_tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(json_tmp, json_path)
    md_tmp = md_path.with_suffix(".md.tmp")
    md_tmp.write_text(
        render_team_summary_markdown(
            payload,
            provenance=provenance,
            external_provenance=external_provenance or None,
        ),
        encoding="utf-8",
    )
    os.replace(md_tmp, md_path)
    return json_path, md_path
