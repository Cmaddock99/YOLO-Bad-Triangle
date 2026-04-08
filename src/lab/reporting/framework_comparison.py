from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lab.config.contracts import (
    CURRENT_PIPELINE_TRANSFORM_ORDER,
    LEGACY_PIPELINE_TRANSFORM_ORDER,
    PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE,
    PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK,
    PIPELINE_SEMANTIC_LEGACY_UNKNOWN,
    REPORTING_AUTHORITIES,
    REPORTING_DATASET_SCOPES,
    REPORTING_RUN_ROLES,
    REPORTING_SOURCE_PHASES,
)
from lab.eval.derived_metrics import compute_normalized_defense_recovery

NONE_LIKE_NAMES = {"", "none", "identity"}


def normalize_name(value: object) -> str:
    return str(value or "").strip().lower()


def is_none_like(value: object) -> bool:
    return normalize_name(value) in NONE_LIKE_NAMES


@dataclass
class FrameworkRunRecord:
    run_name: str
    run_dir: Path
    model: str
    attack: str
    defense: str
    seed: int
    prediction_count: int
    images_with_detections: int
    total_detections: int
    avg_confidence: float | None
    validation_status: str
    precision: float | None
    recall: float | None
    map50: float | None
    map50_95: float | None
    objective_mode: str | None
    target_class: int | None
    attack_roi: str | None
    attack_signature: str
    defense_signature: str
    transform_order: tuple[str, ...]
    semantic_order: str
    run_role: str | None
    dataset_scope: str | None
    authority: str | None
    source_phase: str | None


def _stable_json_signature(payload: Any) -> str:
    try:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return "{}"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _as_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalized_optional_enum(value: object, allowed: tuple[str, ...]) -> str | None:
    normalized = normalize_name(value)
    if normalized in allowed:
        return normalized
    return None


def _reporting_context_from_summary(summary: dict[str, Any]) -> dict[str, str | None]:
    payload = (summary.get("reporting_context") or {})
    if not isinstance(payload, dict):
        payload = {}
    return {
        "run_role": _normalized_optional_enum(payload.get("run_role"), REPORTING_RUN_ROLES),
        "dataset_scope": _normalized_optional_enum(payload.get("dataset_scope"), REPORTING_DATASET_SCOPES),
        "authority": _normalized_optional_enum(payload.get("authority"), REPORTING_AUTHORITIES),
        "source_phase": _normalized_optional_enum(payload.get("source_phase"), REPORTING_SOURCE_PHASES),
    }


def _select_baseline_record(
    runs: list[FrameworkRunRecord],
    *,
    preferred_authority: str | None = None,
) -> FrameworkRunRecord | None:
    baselines = [r for r in runs if is_none_like(r.attack) and is_none_like(r.defense)]
    if not baselines:
        return None
    if preferred_authority:
        matched = [r for r in baselines if r.authority == preferred_authority]
        if matched:
            return matched[0]
    return baselines[0]


def _select_attack_only_record(
    runs: list[FrameworkRunRecord],
    *,
    attack_signature: str | None = None,
    attack_name: str | None = None,
    preferred_authority: str | None = None,
) -> FrameworkRunRecord | None:
    matched = [
        r
        for r in runs
        if not is_none_like(r.attack) and is_none_like(r.defense)
    ]
    if attack_signature:
        signature_matches = [r for r in matched if r.attack_signature == attack_signature]
        if signature_matches:
            matched = signature_matches
    elif attack_name is not None:
        matched = [r for r in matched if normalize_name(r.attack) == normalize_name(attack_name)]
    if not matched:
        return None
    if preferred_authority:
        authority_matches = [r for r in matched if r.authority == preferred_authority]
        if authority_matches:
            return authority_matches[0]
    return matched[0]


def infer_pipeline_semantic_order(
    *,
    semantic_order: object,
    transform_order: tuple[str, ...],
) -> str:
    normalized_semantic_order = normalize_name(semantic_order)
    if normalized_semantic_order in {
        PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE,
        PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK,
        PIPELINE_SEMANTIC_LEGACY_UNKNOWN,
    }:
        return normalized_semantic_order
    if transform_order == CURRENT_PIPELINE_TRANSFORM_ORDER:
        return PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE
    if transform_order == LEGACY_PIPELINE_TRANSFORM_ORDER:
        return PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK
    return PIPELINE_SEMANTIC_LEGACY_UNKNOWN


def _semantic_order_counts(records: list[FrameworkRunRecord]) -> dict[str, int]:
    counts = {
        PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE: 0,
        PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK: 0,
        PIPELINE_SEMANTIC_LEGACY_UNKNOWN: 0,
    }
    for record in records:
        counts[record.semantic_order] = counts.get(record.semantic_order, 0) + 1
    return counts


def discover_framework_runs(runs_root: Path) -> list[FrameworkRunRecord]:
    records: list[FrameworkRunRecord] = []
    if not runs_root.exists():
        return records

    for run_dir in sorted(path for path in runs_root.iterdir() if path.is_dir()):
        summary_path = run_dir / "run_summary.json"
        metrics_path = run_dir / "metrics.json"
        if not summary_path.is_file() or not metrics_path.is_file():
            continue

        summary = _read_json(summary_path)
        metrics = _read_json(metrics_path)
        predictions = metrics.get("predictions", {})
        validation = metrics.get("validation", {})
        attack_obj = (summary.get("attack") or {}).get("resolved_objective") or {}
        attack_params = (summary.get("attack") or {}).get("params") or {}
        defense_params = (summary.get("defense") or {}).get("params") or {}
        objective_mode = attack_obj.get("objective_mode") or attack_params.get("objective_mode")
        target_class_raw = attack_obj.get("target_class")
        if target_class_raw is None:
            target_class_raw = attack_params.get("target_class")
        try:
            target_class = int(target_class_raw) if target_class_raw is not None else None
        except (TypeError, ValueError):
            target_class = None
        attack_roi = attack_obj.get("attack_roi")
        if attack_roi is None:
            attack_roi = attack_params.get("attack_roi")
        attack_signature = _stable_json_signature(
            {
                "attack_name": normalize_name((summary.get("attack") or {}).get("name", "")),
                "objective_mode": objective_mode,
                "target_class": target_class,
                "attack_roi": attack_roi,
                "attack_params": attack_params,
            }
        )
        defense_signature = _stable_json_signature(
            {
                "defense_name": normalize_name((summary.get("defense") or {}).get("name", "")),
                "defense_params": defense_params,
            }
        )
        raw_transform_order = (
            ((summary.get("pipeline") or {}).get("transform_order"))
            or ((metrics.get("provenance") or {}).get("transform_order"))
            or []
        )
        transform_order = tuple(str(step) for step in raw_transform_order if str(step).strip())
        semantic_order = infer_pipeline_semantic_order(
            semantic_order=(
                ((summary.get("pipeline") or {}).get("semantic_order"))
                or ((metrics.get("provenance") or {}).get("semantic_order"))
            ),
            transform_order=transform_order,
        )
        reporting_context = _reporting_context_from_summary(summary)

        records.append(
            FrameworkRunRecord(
                run_name=run_dir.name,
                run_dir=run_dir,
                model=str((summary.get("model") or {}).get("name", "")),
                attack=str((summary.get("attack") or {}).get("name", "")),
                defense=str((summary.get("defense") or {}).get("name", "")),
                seed=int(summary.get("seed", 0)),
                prediction_count=int(summary.get("prediction_record_count", 0)),
                images_with_detections=int(predictions.get("images_with_detections", 0)),
                total_detections=int(predictions.get("total_detections", 0)),
                avg_confidence=_as_optional_float((predictions.get("confidence") or {}).get("mean")),
                validation_status=str(validation.get("status", "missing")),
                precision=_as_optional_float(validation.get("precision")),
                recall=_as_optional_float(validation.get("recall")),
                map50=_as_optional_float(validation.get("mAP50")),
                map50_95=_as_optional_float(validation.get("mAP50-95")),
                objective_mode=str(objective_mode) if objective_mode else None,
                target_class=target_class,
                attack_roi=str(attack_roi) if attack_roi is not None else None,
                attack_signature=attack_signature,
                defense_signature=defense_signature,
                transform_order=transform_order,
                semantic_order=semantic_order,
                run_role=reporting_context["run_role"],
                dataset_scope=reporting_context["dataset_scope"],
                authority=reporting_context["authority"],
                source_phase=reporting_context["source_phase"],
            )
        )

    return records


def _effectiveness(baseline: float | None, attacked: float | None) -> float | None:
    """attack_effectiveness = (baseline - attacked) / baseline"""
    if baseline is None or attacked is None or baseline == 0.0:
        return None
    return (baseline - attacked) / baseline


def _recovery(
    baseline: float | None,
    attacked: float | None,
    defended: float | None,
) -> float | None:
    """defense_recovery = (defended - attacked) / (baseline - attacked)

    Returns None when any input is None, or when the attack had no measurable
    effect (|degradation| < 1e-9) — recovery is undefined in that case.
    Callers must handle None explicitly; do not replace with 0.0 silently.
    """
    return compute_normalized_defense_recovery(baseline, attacked, defended)


def write_summary_csv(records: list[FrameworkRunRecord], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_name", "run_dir", "model", "attack", "defense", "seed",
        "semantic_order",
        "run_role", "dataset_scope", "authority", "source_phase",
        "objective_mode", "target_class", "attack_roi",
        "prediction_count", "images_with_detections", "total_detections",
        "avg_confidence", "validation_status", "precision", "recall",
        "mAP50", "mAP50-95",
    ]
    tmp_csv = output_csv.with_suffix(".csv.tmp")
    with tmp_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({
                "run_name": record.run_name,
                "run_dir": str(record.run_dir),
                "model": record.model,
                "attack": record.attack,
                "defense": record.defense,
                "seed": record.seed,
                "semantic_order": record.semantic_order,
                "run_role": record.run_role,
                "dataset_scope": record.dataset_scope,
                "authority": record.authority,
                "source_phase": record.source_phase,
                "objective_mode": record.objective_mode,
                "target_class": record.target_class,
                "attack_roi": record.attack_roi,
                "prediction_count": record.prediction_count,
                "images_with_detections": record.images_with_detections,
                "total_detections": record.total_detections,
                "avg_confidence": record.avg_confidence,
                "validation_status": record.validation_status,
                "precision": record.precision,
                "recall": record.recall,
                "mAP50": record.map50,
                "mAP50-95": record.map50_95,
            })
    os.replace(tmp_csv, output_csv)


def build_comparison_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    """Build attack-effectiveness rows: baseline vs each attack (no defense)."""
    # Group by (model, seed) — defense is handled separately
    grouped: dict[tuple[str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, seed), runs in grouped.items():
        for run in runs:
            if is_none_like(run.attack) or not is_none_like(run.defense):
                continue
            baseline = _select_baseline_record(runs, preferred_authority=run.authority)
            row = {
                "model": model,
                "seed": seed,
                "attack_run": run.run_name,
                "attack": normalize_name(run.attack),
                "objective_mode": run.objective_mode,
                "target_class": run.target_class,
                "attack_roi": run.attack_roi,
                "baseline_mAP50": baseline.map50 if baseline else None,
                "attack_mAP50": run.map50,
                "mAP50_drop": (
                    (baseline.map50 - run.map50)
                    if baseline and baseline.map50 is not None and run.map50 is not None
                    else None
                ),
                "mAP50_effectiveness": _effectiveness(
                    baseline.map50 if baseline else None,
                    run.map50,
                ),
                "baseline_avg_conf": baseline.avg_confidence if baseline else None,
                "attack_avg_conf": run.avg_confidence,
                "avg_conf_drop": (
                    (baseline.avg_confidence - run.avg_confidence)
                    if baseline
                    and baseline.avg_confidence is not None
                    and run.avg_confidence is not None
                    else None
                ),
                "avg_conf_effectiveness": _effectiveness(
                    baseline.avg_confidence if baseline else None,
                    run.avg_confidence,
                ),
                "run_role": run.run_role,
                "dataset_scope": run.dataset_scope,
                "authority": run.authority,
                "source_phase": run.source_phase,
            }
            rows.append(row)
    return rows


def build_defense_recovery_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    """Build defense-recovery rows: baseline → attack → attack+defense triples."""
    grouped: dict[tuple[str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, seed), runs in grouped.items():
        # Find defended runs (has attack AND has defense)
        defended_runs = [
            r
            for r in runs
            if (
                not is_none_like(r.attack)
                and not is_none_like(r.defense)
                and r.semantic_order == PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE
            )
        ]
        for defended in defended_runs:
            baseline = _select_baseline_record(runs, preferred_authority=defended.authority)
            # Find matching attack-only run
            attacked = _select_attack_only_record(
                runs,
                attack_signature=defended.attack_signature,
                preferred_authority=defended.authority,
            )
            b_map = baseline.map50 if baseline else None
            a_map = attacked.map50 if attacked else None
            d_map = defended.map50

            b_conf = baseline.avg_confidence if baseline else None
            a_conf = attacked.avg_confidence if attacked else None
            d_conf = defended.avg_confidence

            row = {
                "model": model,
                "seed": seed,
                "attack": normalize_name(defended.attack),
                "defense": normalize_name(defended.defense),
                "objective_mode": defended.objective_mode,
                "target_class": defended.target_class,
                "attack_roi": defended.attack_roi,
                "attack_signature": defended.attack_signature,
                "defended_run": defended.run_name,
                "baseline_mAP50": b_map,
                "attack_mAP50": a_map,
                "defended_mAP50": d_map,
                "mAP50_recovery": _recovery(b_map, a_map, d_map),
                "baseline_avg_conf": b_conf,
                "attack_avg_conf": a_conf,
                "defended_avg_conf": d_conf,
                "avg_conf_recovery": _recovery(b_conf, a_conf, d_conf),
                "run_role": defended.run_role,
                "dataset_scope": defended.dataset_scope,
                "authority": defended.authority,
                "source_phase": defended.source_phase,
            }
            rows.append(row)
    return rows


def _fmt(value: float | None, decimals: int = 4) -> str:
    return "" if value is None else f"{value:.{decimals}f}"


def _fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value * 100:.1f}%"


def build_per_class_rows(records: list[FrameworkRunRecord]) -> list[dict[str, Any]]:
    """Per-class detection drop: baseline vs each attack (no defense)."""
    from lab.eval.derived_metrics import compute_per_class_detection_drop

    grouped: dict[tuple[str, int], list[FrameworkRunRecord]] = {}
    for record in records:
        grouped.setdefault((record.model, record.seed), []).append(record)

    rows: list[dict[str, Any]] = []
    for (model, seed), runs in grouped.items():
        for run in runs:
            if is_none_like(run.attack) or not is_none_like(run.defense):
                continue
            baseline = _select_baseline_record(runs, preferred_authority=run.authority)
            if baseline is None:
                continue
            baseline_metrics = _read_json(baseline.run_dir / "metrics.json")
            baseline_pc: dict[int, dict] = {
                int(k): v
                for k, v in (baseline_metrics.get("predictions", {}).get("per_class") or {}).items()
            }
            if not baseline_pc:
                continue
            attack_metrics = _read_json(run.run_dir / "metrics.json")
            attack_pc: dict[int, dict] = {
                int(k): v
                for k, v in (attack_metrics.get("predictions", {}).get("per_class") or {}).items()
            }
            drops = compute_per_class_detection_drop(baseline_pc, attack_pc)
            for class_id, drop in sorted(drops.items()):
                b_count = baseline_pc.get(class_id, {}).get("count", 0)
                a_count = attack_pc.get(class_id, {}).get("count", 0)
                class_name = (baseline_pc.get(class_id) or attack_pc.get(class_id) or {}).get(
                    "class_name", f"class_{class_id}"
                )
                rows.append({
                    "model": model,
                    "seed": seed,
                    "attack": normalize_name(run.attack),
                    "attack_run": run.run_name,
                    "class_id": class_id,
                    "class_name": class_name,
                    "baseline_count": b_count,
                    "attack_count": a_count,
                    "detection_drop": drop,
                    "run_role": run.run_role,
                    "dataset_scope": run.dataset_scope,
                    "authority": run.authority,
                    "source_phase": run.source_phase,
                })
    return rows


def render_markdown_report(records: list[FrameworkRunRecord]) -> str:
    lines = [
        "# Framework Run Comparison Report",
        "",
        f"Total discovered framework runs: **{len(records)}**",
        "",
    ]
    if not records:
        lines.append("No framework runs found.")
        return "\n".join(lines)

    semantic_counts = _semantic_order_counts(records)
    discovered_semantics = {record.semantic_order for record in records}
    excluded_defended_runs = [
        record
        for record in records
        if not is_none_like(record.defense)
        and record.semantic_order != PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE
    ]
    if len(discovered_semantics) > 1 or PIPELINE_SEMANTIC_LEGACY_UNKNOWN in discovered_semantics:
        lines += [
            "## Comparability Warning",
            "",
            "Discovered runs span multiple pipeline semantics.",
            "Defense recovery rows below include only runs recorded with `attack_then_defense` semantics.",
            "Legacy or unknown-era defended runs remain in inventory but are excluded from recovery comparisons.",
            "",
            f"- `attack_then_defense` runs: **{semantic_counts.get(PIPELINE_SEMANTIC_ATTACK_THEN_DEFENSE, 0)}**",
            f"- `defense_then_attack` runs: **{semantic_counts.get(PIPELINE_SEMANTIC_DEFENSE_THEN_ATTACK, 0)}**",
            f"- `legacy_unknown` runs: **{semantic_counts.get(PIPELINE_SEMANTIC_LEGACY_UNKNOWN, 0)}**",
            "",
        ]

    # Run inventory
    lines += [
        "## Run Inventory",
        "",
        "| Run | Model | Attack | Defense | Semantics | Validation | mAP50 | Avg conf |",
        "|---|---|---|---|---|---|---:|---:|",
    ]
    for record in records:
        lines.append(
            f"| `{record.run_name}` | `{record.model}` | `{record.attack}` | `{record.defense}` | "
            f"`{record.semantic_order}` | `{record.validation_status}` | {_fmt(record.map50)} | "
            f"{_fmt(record.avg_confidence)} |"
        )

    # Attack effectiveness
    comparison_rows = build_comparison_rows(records)
    lines += ["", "## Attack Effectiveness", ""]
    if not comparison_rows:
        lines.append("No baseline/attack pairs found.")
    else:
        lines += [
            "| Model | Seed | Attack | Objective | Target class | ROI | mAP50 baseline | mAP50 attacked | mAP50 drop | Effectiveness |",
            "|---|---:|---|---|---:|---|---:|---:|---:|---:|",
        ]
        for row in comparison_rows:
            lines.append(
                f"| `{row['model']}` | {row['seed']} | `{row['attack']}` | "
                f"`{row['objective_mode'] or ''}` | {'' if row['target_class'] is None else row['target_class']} | "
                f"`{row['attack_roi'] or ''}` | "
                f"{_fmt(row['baseline_mAP50'])} | {_fmt(row['attack_mAP50'])} | "
                f"{_fmt(row['mAP50_drop'])} | {_fmt_pct(row['mAP50_effectiveness'])} |"
            )

    # Defense recovery
    recovery_rows = build_defense_recovery_rows(records)
    lines += ["", "## Defense Recovery", ""]
    if excluded_defended_runs:
        lines.append(
            "Defended runs from legacy or unknown pipeline eras are excluded from this table to avoid "
            "mixing incomparable recovery semantics."
        )
        lines.append("")
    if not recovery_rows:
        lines.append("No defended runs found. Run with `--defenses` to enable defense sweep.")
    else:
        lines += [
            "| Model | Attack | Defense | Objective | Target class | ROI | mAP50 attacked | mAP50 defended | Recovery |",
            "|---|---|---|---|---:|---|---:|---:|---:|",
        ]
        for row in recovery_rows:
            lines.append(
                f"| `{row['model']}` | `{row['attack']}` | `{row['defense']}` | "
                f"`{row['objective_mode'] or ''}` | {'' if row['target_class'] is None else row['target_class']} | "
                f"`{row['attack_roi'] or ''}` | "
                f"{_fmt(row['attack_mAP50'])} | {_fmt(row['defended_mAP50'])} | "
                f"{_fmt_pct(row['mAP50_recovery'])} |"
            )

    # Per-class detection drop
    per_class_rows = build_per_class_rows(records)
    lines += ["", "## Per-Class Detection Drop", ""]
    if not per_class_rows:
        lines.append("No per-class data available (run with validation or inspect predictions.jsonl).")
    else:
        lines += [
            "| Model | Seed | Attack | Class ID | Class | Baseline count | Attack count | Drop |",
            "|---|---:|---|---:|---|---:|---:|---:|",
        ]
        for row in per_class_rows:
            lines.append(
                f"| `{row['model']}` | {row['seed']} | `{row['attack']}` | "
                f"{row['class_id']} | {row['class_name']} | "
                f"{row['baseline_count']} | {row['attack_count']} | "
                f"{_fmt_pct(row['detection_drop'])} |"
            )

    return "\n".join(lines)
