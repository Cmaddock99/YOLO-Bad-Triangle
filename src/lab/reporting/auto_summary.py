from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

from lab.config.contracts import (
    SCHEMA_ID_CYCLE_SUMMARY,
    SCHEMA_ID_WARNINGS,
)
from lab.eval.bootstrap import bootstrap_paired_ci
from lab.eval.derived_metrics import compute_normalized_defense_recovery
from lab.reporting.framework_comparison import (
    FrameworkRunRecord,
    _read_json,
    build_comparison_rows,
    build_defense_recovery_rows,
    build_per_class_rows,
    discover_framework_runs,
    is_none_like,
    normalize_name,
)
from lab.reporting.warnings import evaluate_warnings

# ---------------------------------------------------------------------------
# Headline metrics CSV — 34 columns
# ---------------------------------------------------------------------------
HEADLINE_COLUMNS = [
    "model",
    "seed",
    "attack",
    "objective_mode",
    "target_class",
    "attack_roi",
    "attack_run",
    "baseline_run",
    "validation_status",
    "baseline_mAP50",
    "attack_mAP50",
    "mAP50_drop",
    "mAP50_effectiveness",
    "baseline_avg_conf",
    "attack_avg_conf",
    "avg_conf_drop",
    "avg_conf_effectiveness",
    "baseline_total_detections",
    "attack_total_detections",
    "detection_drop",
    "defense",
    "defended_run",
    "defended_mAP50",
    "mAP50_recovery_normalized",
    "defended_avg_conf",
    "avg_conf_recovery_normalized",
    "defended_total_detections",
    "detection_recovery_normalized",
    "bootstrap_det_drop_lower",
    "bootstrap_det_drop_upper",
    "bootstrap_det_drop_ci_computed",
    "bootstrap_conf_drop_lower",
    "bootstrap_conf_drop_upper",
    "bootstrap_conf_drop_ci_computed",
]

# ---------------------------------------------------------------------------
# Per-class vulnerability CSV — 15 columns
# ---------------------------------------------------------------------------
PER_CLASS_COLUMNS = [
    "model",
    "seed",
    "attack",
    "objective_mode",
    "target_class",
    "attack_roi",
    "attack_run",
    "baseline_run",
    "class_id",
    "class_name",
    "baseline_count",
    "attack_count",
    "detection_drop",
    "defended_count",
    "detection_recovery_normalized",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_opt(value: float | None, decimals: int = 6) -> str:
    return "" if value is None else f"{value:.{decimals}f}"


def _to_opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _baseline_for(records: list[FrameworkRunRecord], model: str, seed: int) -> FrameworkRunRecord | None:
    return next(
        (r for r in records
         if r.model == model and r.seed == seed
         and is_none_like(r.attack) and is_none_like(r.defense)),
        None,
    )


def _attacked_for(
    records: list[FrameworkRunRecord],
    model: str,
    seed: int,
    attack: str,
    *,
    attack_signature: str | None = None,
) -> FrameworkRunRecord | None:
    if attack_signature:
        matched = next(
            (
                r
                for r in records
                if r.model == model
                and r.seed == seed
                and r.attack_signature == attack_signature
                and is_none_like(r.defense)
            ),
            None,
        )
        if matched is not None:
            return matched
    return next(
        (
            r
            for r in records
            if r.model == model and r.seed == seed
            and normalize_name(r.attack) == attack
            and is_none_like(r.defense)
        ),
        None,
    )


def _get_total_detections(run: FrameworkRunRecord) -> float | None:
    m = _read_json(run.run_dir / "metrics.json")
    return _to_opt_float(m.get("predictions", {}).get("total_detections"))


def _detection_drop(baseline_det: float | None, attack_det: float | None) -> float | None:
    if baseline_det is None or attack_det is None or baseline_det == 0.0:
        return None
    return (baseline_det - attack_det) / baseline_det


# ---------------------------------------------------------------------------
# Main payload builder
# ---------------------------------------------------------------------------

def build_auto_summary_payload(
    runs_root: Path,
    *,
    bootstrap: bool = True,
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 42,
) -> dict[str, Any]:
    """Discover framework runs under `runs_root` and build the full summary payload."""
    records = discover_framework_runs(runs_root)

    # ---------- baseline ----------
    baseline_candidates = [r for r in records if is_none_like(r.attack) and is_none_like(r.defense)]
    baseline_record: FrameworkRunRecord | None = baseline_candidates[0] if baseline_candidates else None
    baseline_info: dict[str, Any] | None = None
    if baseline_record:
        baseline_info = {
            "run_name": baseline_record.run_name,
            "model": baseline_record.model,
            "seed": baseline_record.seed,
            "total_detections": _get_total_detections(baseline_record),
            "avg_confidence": baseline_record.avg_confidence,
            "mAP50": baseline_record.map50,
            "validation_status": baseline_record.validation_status,
            "candidate_count": len(baseline_candidates),
        }

    # ---------- attack effectiveness rows ----------
    comparison_rows = build_comparison_rows(records)

    # Enrich with total_detections and bootstrap CI
    for row in comparison_rows:
        model, seed = row["model"], row["seed"]
        baseline_rec = _baseline_for(records, model, seed)
        # Look up the specific run this row was built from (set by build_comparison_rows)
        attacked_run_name = row.get("attack_run")
        attacked_rec = next((r for r in records if r.run_name == attacked_run_name), None)

        b_det = _get_total_detections(baseline_rec) if baseline_rec else None
        a_det = _get_total_detections(attacked_rec) if attacked_rec else None
        row["baseline_total_detections"] = b_det
        row["attack_total_detections"] = a_det
        row["detection_drop"] = _detection_drop(b_det, a_det)

        row["bootstrap_det_drop_lower"] = None
        row["bootstrap_det_drop_upper"] = None
        row["bootstrap_det_drop_ci_computed"] = False
        row["bootstrap_conf_drop_lower"] = None
        row["bootstrap_conf_drop_upper"] = None
        row["bootstrap_conf_drop_ci_computed"] = False

        if bootstrap and baseline_rec and attacked_rec:
            ci = bootstrap_paired_ci(
                baseline_rec.run_dir / "predictions.jsonl",
                attacked_rec.run_dir / "predictions.jsonl",
                n_bootstrap=bootstrap_n,
                seed=bootstrap_seed,
            )
            row["bootstrap_det_drop_lower"] = ci["detection_drop_lower"]
            row["bootstrap_det_drop_upper"] = ci["detection_drop_upper"]
            row["bootstrap_det_drop_ci_computed"] = ci["detection_drop_ci_computed"]
            row["bootstrap_conf_drop_lower"] = ci["conf_drop_lower"]
            row["bootstrap_conf_drop_upper"] = ci["conf_drop_upper"]
            row["bootstrap_conf_drop_ci_computed"] = ci["conf_drop_ci_computed"]

        # attack_run already set correctly by build_comparison_rows
        row["baseline_run"] = baseline_rec.run_name if baseline_rec else None
        row["validation_status"] = attacked_rec.validation_status if attacked_rec else None

    # ---------- defense recovery rows ----------
    recovery_rows = build_defense_recovery_rows(records)

    for row in recovery_rows:
        model, seed, attack = row["model"], row["seed"], row["attack"]
        baseline_rec = _baseline_for(records, model, seed)
        attacked_rec = _attacked_for(
            records,
            model,
            seed,
            attack,
            attack_signature=row.get("attack_signature"),
        )

        b_det = _get_total_detections(baseline_rec) if baseline_rec else None
        a_det = _get_total_detections(attacked_rec) if attacked_rec else None

        # Find defended record
        defended_rec = next(
            (r for r in records
             if r.model == model and r.seed == seed
             and normalize_name(r.attack) == attack
             and normalize_name(r.defense) == row["defense"]
             and r.run_name == row.get("defended_run")),
            None,
        )
        d_det = _get_total_detections(defended_rec) if defended_rec else None

        row["baseline_total_detections"] = b_det
        row["attack_total_detections"] = a_det
        row["defended_total_detections"] = d_det
        row["detection_recovery_normalized"] = compute_normalized_defense_recovery(b_det, a_det, d_det)

        # Rename keys for consistency; values were already computed by build_defense_recovery_rows
        row["mAP50_recovery_normalized"] = row.pop("mAP50_recovery", None)
        row["avg_conf_recovery_normalized"] = row.pop("avg_conf_recovery", None)

        row["baseline_run"] = baseline_rec.run_name if baseline_rec else None
        row["attack_run"] = attacked_rec.run_name if attacked_rec else None

    # ---------- per-class rows ----------
    per_class_rows = build_per_class_rows(records)

    # Enrich with defended_count and recovery
    for row in per_class_rows:
        model, seed, attack = row["model"], row["seed"], row["attack"]
        class_id = row["class_id"]
        baseline_rec = _baseline_for(records, model, seed)
        # attack_run was set per-run by build_per_class_rows; look up the exact record
        attacked_run_name = row.get("attack_run")
        attacked_rec = next((r for r in records if r.run_name == attacked_run_name), None) if attacked_run_name else None

        row["baseline_run"] = baseline_rec.run_name if baseline_rec else None
        # attack_run already carries the correct run name from build_per_class_rows

        # Try to find any defended run for this attack
        defended_rec = next(
            (
                r
                for r in records
                if r.model == model
                and r.seed == seed
                and not is_none_like(r.defense)
                and (
                    (attacked_rec is not None and r.attack_signature == attacked_rec.attack_signature)
                    or normalize_name(r.attack) == attack
                )
            ),
            None,
        )
        row["objective_mode"] = attacked_rec.objective_mode if attacked_rec else None
        row["target_class"] = attacked_rec.target_class if attacked_rec else None
        row["attack_roi"] = attacked_rec.attack_roi if attacked_rec else None

        defended_count: int | None = None
        detection_recovery: float | None = None
        if defended_rec:
            dm = _read_json(defended_rec.run_dir / "metrics.json")
            dpc = {
                int(k): v
                for k, v in (dm.get("predictions", {}).get("per_class") or {}).items()
            }
            defended_count = dpc.get(class_id, {}).get("count")
            b_count = row["baseline_count"]
            a_count = row["attack_count"]
            detection_recovery = compute_normalized_defense_recovery(b_count, a_count, defended_count)

        row["defended_count"] = defended_count
        row["detection_recovery_normalized"] = detection_recovery

    # ---------- assemble ----------
    return {
        "schema_version": SCHEMA_ID_CYCLE_SUMMARY,
        "runs_root": str(runs_root.expanduser().resolve()),
        "total_runs": len(records),
        "baseline": baseline_info,
        "attack_effectiveness_rows": comparison_rows,
        "defense_recovery_rows": recovery_rows,
        "per_class_vulnerability_rows": per_class_rows,
    }


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

def _pct(v: float | None) -> str:
    return "n/a" if v is None else f"{v * 100:.1f}%"


def _f4(v: float | None) -> str:
    return "n/a" if v is None else f"{v:.4f}"


def render_auto_summary_markdown(payload: dict[str, Any], warnings: list[dict[str, Any]]) -> str:
    lines: list[str] = ["# Auto Summary Report", ""]
    lines.append(f"**Runs root:** `{payload.get('runs_root', '')}`  ")
    lines.append(f"**Total runs discovered:** {payload.get('total_runs', 0)}")
    lines.append("")

    if warnings:
        lines += ["## Warnings", ""]
        for w in warnings:
            lines.append(f"- **{w['code']}**: {w['message']}")
        lines.append("")

    baseline = payload.get("baseline")
    if baseline:
        lines += [
            "## Baseline",
            "",
            "| Run | Model | Seed | Total det | Avg conf | mAP50 |",
            "|---|---|---:|---:|---:|---:|",
            f"| `{baseline.get('run_name')}` | `{baseline.get('model')}` | {baseline.get('seed')} "
            f"| {baseline.get('total_detections', 'n/a')} "
            f"| {_f4(baseline.get('avg_confidence'))} "
            f"| {_f4(baseline.get('mAP50'))} |",
            "",
        ]

    attack_rows: list[dict[str, Any]] = list(payload.get("attack_effectiveness_rows") or [])
    lines += ["## Attack Effectiveness", ""]
    if not attack_rows:
        lines.append("No baseline/attack pairs found.")
    else:
        lines += [
            "| Model | Attack | Objective | mAP50 drop | Effectiveness | Det drop | "
            "Det drop CI (95%) | Conf drop | Conf drop CI (95%) |",
            "|---|---|---|---:|---:|---:|---|---:|---|",
        ]
        for row in attack_rows:
            det_ci = (
                "not computed"
                if not row.get("bootstrap_det_drop_ci_computed")
                else f"[{_pct(row.get('bootstrap_det_drop_lower'))}, "
                     f"{_pct(row.get('bootstrap_det_drop_upper'))}]"
            )
            conf_ci = (
                "not computed"
                if not row.get("bootstrap_conf_drop_ci_computed")
                else f"[{_pct(row.get('bootstrap_conf_drop_lower'))}, "
                     f"{_pct(row.get('bootstrap_conf_drop_upper'))}]"
            )
            lines.append(
                f"| `{row.get('model')}` | `{row.get('attack')}` | "
                f"`{row.get('objective_mode') or ''}` | "
                f"{_pct(row.get('mAP50_drop') if row.get('mAP50_drop') is not None else None)} | "
                f"{_pct(row.get('mAP50_effectiveness'))} | "
                f"{_pct(row.get('detection_drop'))} | {det_ci} | "
                f"{_pct(row.get('avg_conf_drop'))} | {conf_ci} |"
            )
    lines.append("")

    recovery_rows: list[dict[str, Any]] = list(payload.get("defense_recovery_rows") or [])
    lines += ["## Defense Recovery", ""]
    if not recovery_rows:
        lines.append("No defended runs found.")
    else:
        lines += [
            "| Model | Attack | Defense | mAP50 (atk) | mAP50 (def) | mAP50 recovery | "
            "Det recovery |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for row in recovery_rows:
            lines.append(
                f"| `{row.get('model')}` | `{row.get('attack')}` | `{row.get('defense')}` | "
                f"{_f4(row.get('attack_mAP50'))} | {_f4(row.get('defended_mAP50'))} | "
                f"{_pct(row.get('mAP50_recovery_normalized'))} | "
                f"{_pct(row.get('detection_recovery_normalized'))} |"
            )
    lines.append("")

    per_class_rows: list[dict[str, Any]] = list(payload.get("per_class_vulnerability_rows") or [])
    lines += ["## Per-Class Vulnerability", ""]
    if not per_class_rows:
        lines.append("No per-class data available.")
    else:
        lines += [
            "| Model | Attack | Class | Baseline | Attacked | Drop | Defended | Recovery |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in per_class_rows:
            lines.append(
                f"| `{row.get('model')}` | `{row.get('attack')}` | "
                f"{row.get('class_name', row.get('class_id'))} | "
                f"{row.get('baseline_count', 'n/a')} | {row.get('attack_count', 'n/a')} | "
                f"{_pct(row.get('detection_drop'))} | "
                f"{row.get('defended_count', 'n/a')} | "
                f"{_pct(row.get('detection_recovery_normalized'))} |"
            )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CSV writers
# ---------------------------------------------------------------------------

def _row_to_headline_csv(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": row.get("model", ""),
        "seed": row.get("seed", ""),
        "attack": row.get("attack", ""),
        "objective_mode": row.get("objective_mode") or "",
        "target_class": "" if row.get("target_class") is None else row["target_class"],
        "attack_roi": row.get("attack_roi") or "",
        "attack_run": row.get("attack_run") or "",
        "baseline_run": row.get("baseline_run") or "",
        "validation_status": row.get("validation_status") or "",
        "baseline_mAP50": _fmt_opt(row.get("baseline_mAP50")),
        "attack_mAP50": _fmt_opt(row.get("attack_mAP50")),
        "mAP50_drop": _fmt_opt(row.get("mAP50_drop")),
        "mAP50_effectiveness": _fmt_opt(row.get("mAP50_effectiveness")),
        "baseline_avg_conf": _fmt_opt(row.get("baseline_avg_conf")),
        "attack_avg_conf": _fmt_opt(row.get("attack_avg_conf")),
        "avg_conf_drop": _fmt_opt(row.get("avg_conf_drop")),
        "avg_conf_effectiveness": _fmt_opt(row.get("avg_conf_effectiveness")),
        "baseline_total_detections": _fmt_opt(row.get("baseline_total_detections"), 0),
        "attack_total_detections": _fmt_opt(row.get("attack_total_detections"), 0),
        "detection_drop": _fmt_opt(row.get("detection_drop")),
        "defense": row.get("defense") or "",
        "defended_run": row.get("defended_run") or "",
        "defended_mAP50": _fmt_opt(row.get("defended_mAP50")),
        "mAP50_recovery_normalized": _fmt_opt(row.get("mAP50_recovery_normalized")),
        "defended_avg_conf": _fmt_opt(row.get("defended_avg_conf")),
        "avg_conf_recovery_normalized": _fmt_opt(row.get("avg_conf_recovery_normalized")),
        "defended_total_detections": _fmt_opt(row.get("defended_total_detections"), 0),
        "detection_recovery_normalized": _fmt_opt(row.get("detection_recovery_normalized")),
        "bootstrap_det_drop_lower": _fmt_opt(row.get("bootstrap_det_drop_lower")),
        "bootstrap_det_drop_upper": _fmt_opt(row.get("bootstrap_det_drop_upper")),
        "bootstrap_det_drop_ci_computed": str(row.get("bootstrap_det_drop_ci_computed", False)).lower(),
        "bootstrap_conf_drop_lower": _fmt_opt(row.get("bootstrap_conf_drop_lower")),
        "bootstrap_conf_drop_upper": _fmt_opt(row.get("bootstrap_conf_drop_upper")),
        "bootstrap_conf_drop_ci_computed": str(row.get("bootstrap_conf_drop_ci_computed", False)).lower(),
    }


def _merge_effectiveness_and_recovery(
    attack_rows: list[dict[str, Any]],
    recovery_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge attack rows with their defense recovery data (left join)."""
    # Build lookup: (model, seed, attack) → list of recovery rows
    recovery_lookup: dict[tuple, list[dict[str, Any]]] = {}
    for r in recovery_rows:
        key = (r.get("model"), r.get("seed"), r.get("attack"))
        recovery_lookup.setdefault(key, []).append(r)

    merged: list[dict[str, Any]] = []
    for arow in attack_rows:
        key = (arow.get("model"), arow.get("seed"), arow.get("attack"))
        defenses = recovery_lookup.get(key, [])
        if defenses:
            for drow in defenses:
                combined = dict(arow)
                combined["defense"] = drow.get("defense")
                combined["defended_run"] = drow.get("defended_run")
                combined["defended_mAP50"] = drow.get("defended_mAP50")
                combined["mAP50_recovery_normalized"] = drow.get("mAP50_recovery_normalized")
                combined["defended_avg_conf"] = drow.get("defended_avg_conf")
                combined["avg_conf_recovery_normalized"] = drow.get("avg_conf_recovery_normalized")
                combined["defended_total_detections"] = drow.get("defended_total_detections")
                combined["detection_recovery_normalized"] = drow.get("detection_recovery_normalized")
                merged.append(combined)
        else:
            merged.append(dict(arow))
    return merged


def write_headline_csv(
    payload: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    attack_rows = list(payload.get("attack_effectiveness_rows") or [])
    recovery_rows = list(payload.get("defense_recovery_rows") or [])
    merged = _merge_effectiveness_and_recovery(attack_rows, recovery_rows)

    tmp = output_path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADLINE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in merged:
            writer.writerow(_row_to_headline_csv(row))
    os.replace(tmp, output_path)


def write_per_class_csv(
    payload: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(payload.get("per_class_vulnerability_rows") or [])

    tmp = output_path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PER_CLASS_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "model": row.get("model", ""),
                "seed": row.get("seed", ""),
                "attack": row.get("attack", ""),
                "objective_mode": row.get("objective_mode") or "",
                "target_class": "" if row.get("target_class") is None else row["target_class"],
                "attack_roi": row.get("attack_roi") or "",
                "attack_run": row.get("attack_run") or "",
                "baseline_run": row.get("baseline_run") or "",
                "class_id": row.get("class_id", ""),
                "class_name": row.get("class_name", ""),
                "baseline_count": row.get("baseline_count", ""),
                "attack_count": row.get("attack_count", ""),
                "detection_drop": _fmt_opt(row.get("detection_drop")),
                "defended_count": "" if row.get("defended_count") is None else row["defended_count"],
                "detection_recovery_normalized": _fmt_opt(row.get("detection_recovery_normalized")),
            })
    os.replace(tmp, output_path)


# ---------------------------------------------------------------------------
# Top-level writer
# ---------------------------------------------------------------------------

def write_auto_summary(
    runs_root: Path,
    output_dir: Path,
    *,
    bootstrap: bool = True,
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 42,
) -> dict[str, Path]:
    """Build and write all 5 summary artifacts to output_dir.

    Returns a dict of {artifact_name: path}.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = build_auto_summary_payload(
        runs_root,
        bootstrap=bootstrap,
        bootstrap_n=bootstrap_n,
        bootstrap_seed=bootstrap_seed,
    )
    warnings = evaluate_warnings(payload)

    # 1. summary.json
    summary_json_path = output_dir / "summary.json"
    tmp = summary_json_path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({**payload, "warnings": warnings}, indent=2, default=str, sort_keys=True),
        encoding="utf-8",
    )
    os.replace(tmp, summary_json_path)

    # 2. summary.md
    summary_md_path = output_dir / "summary.md"
    tmp = summary_md_path.with_suffix(".tmp")
    tmp.write_text(render_auto_summary_markdown(payload, warnings), encoding="utf-8")
    os.replace(tmp, summary_md_path)

    # 3. headline_metrics.csv
    headline_csv_path = output_dir / "headline_metrics.csv"
    write_headline_csv(payload, headline_csv_path)

    # 4. per_class_vulnerability.csv
    per_class_csv_path = output_dir / "per_class_vulnerability.csv"
    write_per_class_csv(payload, per_class_csv_path)

    # 5. warnings.json
    warnings_json_path = output_dir / "warnings.json"
    warnings_payload = {
        "schema_version": SCHEMA_ID_WARNINGS,
        "runs_root": str(runs_root.expanduser().resolve()),
        "warning_count": len(warnings),
        "warnings": warnings,
    }
    tmp = warnings_json_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(warnings_payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, warnings_json_path)

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "headline_csv": headline_csv_path,
        "per_class_csv": per_class_csv_path,
        "warnings_json": warnings_json_path,
    }
