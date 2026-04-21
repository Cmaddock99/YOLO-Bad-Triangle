#!/usr/bin/env python3
"""Generate longitudinal cycle report from outputs/cycle_history/*.json.

Reads every cycle history file and produces two outputs:

  outputs/cycle_report.csv  — one row per (cycle × attack × defense)
  outputs/cycle_report.md   — executive summary + trend tables

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/generate_cycle_report.py
    PYTHONPATH=src ./.venv/bin/python scripts/generate_cycle_report.py --history-dir outputs/cycle_history
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HISTORY_DIR_DEFAULT = REPO / "outputs" / "cycle_history"
OUTPUTS = REPO / "outputs"
CURRENT_PIPELINE_SEMANTICS = "attack_then_defense"
LEGACY_PIPELINE_SEMANTICS = "defense_then_attack"
UNKNOWN_PIPELINE_SEMANTICS = "legacy_unknown"
MIXED_PIPELINE_SEMANTICS = "mixed"


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_cycles(history_dir: Path) -> list[dict]:
    cycles = []
    failures: list[tuple[str, str]] = []
    for f in sorted(history_dir.glob("*.json")):
        try:
            payload = json.loads(f.read_text())
            if not isinstance(payload, dict):
                raise ValueError("root JSON value must be an object")
            cycles.append(payload)
        except Exception as exc:
            failures.append((f.name, str(exc)))
    if failures:
        print(f"[warn] Skipped {len(failures)} invalid cycle history file(s) in {history_dir}")
        for name, reason in failures[:3]:
            print(f"[warn]   {name}: {reason}")
        if len(failures) > 3:
            print(f"[warn]   ... and {len(failures) - 3} more")
    cycles.sort(key=lambda c: c.get("started_at", ""))
    return cycles


def _is_baseline(v: dict) -> bool:
    atk = v.get("attack")
    dfn = v.get("defense")
    return atk in (None, "none", "") and dfn in (None, "none", "")


def _is_attack_only(v: dict) -> bool:
    atk = v.get("attack")
    dfn = v.get("defense")
    return bool(atk and atk not in ("none", "")) and dfn in (None, "none", "")


def _parse_validation(validation_results: dict) -> tuple[dict | None, dict, dict]:
    """Return (baseline_entry, attack_map, defended_map).

    attack_map:   attack_name → entry
    defended_map: (attack_name, defense_name) → entry
    """
    baseline: dict | None = None
    attack_map: dict[str, dict] = {}
    defended_map: dict[tuple[str, str], dict] = {}
    _defended_run_names: dict[tuple[str, str], str] = {}

    for _run_name, v in validation_results.items():
        if _is_baseline(v):
            baseline = v
        elif _is_attack_only(v):
            atk = str(v["attack"])
            # Keep the entry with more detections if duplicate (deduplication)
            if atk not in attack_map or (v.get("detections") or 0) > (attack_map[atk].get("detections") or 0):
                attack_map[atk] = v
        else:
            atk = v.get("attack")
            dfn = v.get("defense")
            if atk and dfn and atk not in ("none", "") and dfn not in ("none", ""):
                key = (str(atk), str(dfn))
                existing_name = _defended_run_names.get(key, "")
                is_validate = _run_name.startswith("validate_")
                existing_is_validate = existing_name.startswith("validate_")
                # prefer validate_ (Phase 4) rows over smoke (Phase 1) rows
                if key not in defended_map or (is_validate and not existing_is_validate):
                    defended_map[key] = v
                    _defended_run_names[key] = _run_name

    return baseline, attack_map, defended_map


def _cycle_pipeline_semantics(cycle: dict[str, Any]) -> str:
    normalized = str(cycle.get("pipeline_semantics") or "").strip().lower()
    if normalized in {
        CURRENT_PIPELINE_SEMANTICS,
        LEGACY_PIPELINE_SEMANTICS,
        UNKNOWN_PIPELINE_SEMANTICS,
        MIXED_PIPELINE_SEMANTICS,
    }:
        return normalized
    return UNKNOWN_PIPELINE_SEMANTICS


# ── CSV generation ────────────────────────────────────────────────────────────

CSV_FIELDS = [
    "cycle_num", "cycle_id", "finished_at",
    "pipeline_semantics",
    "attack", "defense",
    "baseline_mAP50", "attack_mAP50", "defended_mAP50",
    "detection_drop_pct", "recovery_pct",
    "best_attack_params", "best_defense_params",
]


def _pct(value: float | None) -> str:
    return f"{value * 100:.1f}" if value is not None else ""


def _build_csv_rows(cycles: list[dict]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, cycle in enumerate(cycles, 1):
        cycle_id = cycle.get("cycle_id", "")
        finished_at = cycle.get("finished_at", "")
        validation_results = cycle.get("validation_results", {})
        best_attack_params = cycle.get("best_attack_params", {})
        best_defense_params = cycle.get("best_defense_params", {})

        baseline, attack_map, defended_map = _parse_validation(validation_results)
        baseline_map50 = baseline.get("mAP50") if baseline else None
        baseline_dets = baseline.get("detections") if baseline else None

        # One row per attack (attack-only, no defense)
        for atk, atk_entry in attack_map.items():
            atk_map50 = atk_entry.get("mAP50")
            atk_dets = atk_entry.get("detections")
            drop_pct: float | None = None
            if baseline_dets is not None and baseline_dets != 0 and atk_dets is not None:
                drop_pct = (baseline_dets - atk_dets) / baseline_dets

            rows.append({
                "cycle_num": i,
                "cycle_id": cycle_id,
                "finished_at": finished_at,
                "pipeline_semantics": _cycle_pipeline_semantics(cycle),
                "attack": atk,
                "defense": "none",
                "baseline_mAP50": baseline_map50,
                "attack_mAP50": atk_map50,
                "defended_mAP50": "",
                "detection_drop_pct": _pct(drop_pct),
                "recovery_pct": "",
                "best_attack_params": json.dumps(best_attack_params.get(atk, {})),
                "best_defense_params": "",
            })

        # One row per (attack × defense) combination
        for (atk, dfn), def_entry in defended_map.items():
            def_map50 = def_entry.get("mAP50")
            def_dets = def_entry.get("detections")
            atk_dets = attack_map.get(atk, {}).get("detections")

            drop_pct = None
            recovery_pct = None
            if baseline_dets is not None and baseline_dets != 0 and atk_dets is not None and def_dets is not None:
                drop = baseline_dets - atk_dets
                if drop > 0:
                    recovery_pct = (def_dets - atk_dets) / drop

            rows.append({
                "cycle_num": i,
                "cycle_id": cycle_id,
                "finished_at": finished_at,
                "pipeline_semantics": _cycle_pipeline_semantics(cycle),
                "attack": atk,
                "defense": dfn,
                "baseline_mAP50": baseline_map50,
                "attack_mAP50": attack_map.get(atk, {}).get("mAP50"),
                "defended_mAP50": def_map50,
                "detection_drop_pct": "",
                "recovery_pct": _pct(recovery_pct),
                "best_attack_params": json.dumps(best_attack_params.get(atk, {})),
                "best_defense_params": json.dumps(best_defense_params.get(dfn, {})),
            })

    return rows


def write_csv(cycles: list[dict], output_path: Path) -> None:
    rows = _build_csv_rows(cycles)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


# ── Markdown generation ───────────────────────────────────────────────────────

def _fmt_map50(v: Any) -> str:
    if v is None or v == "":
        return "n/a"
    try:
        return f"{float(v):.4f}"
    except (TypeError, ValueError):
        return "n/a"


def _fmt_date(iso: str) -> str:
    if not iso:
        return "?"
    return iso[:10]  # YYYY-MM-DD


def _best_defended_map50(defended_map: dict, attack_map: dict) -> tuple[float | None, str]:
    """Return (best_mAP50, 'attack+defense') among defended runs."""
    best: float | None = None
    best_label = "n/a"
    for (atk, dfn), entry in defended_map.items():
        m = entry.get("mAP50")
        if m is not None and (best is None or m > best):
            best = m
            best_label = f"{atk}+{dfn}"
    return best, best_label


def _worst_attack(attack_map: dict, baseline: dict | None) -> str:
    """Return attack with highest detection drop."""
    if not attack_map or baseline is None:
        return "n/a"
    baseline_dets = baseline.get("detections") or 0
    if baseline_dets == 0:
        return "n/a"
    worst_atk = min(
        attack_map,
        key=lambda a: (attack_map[a].get("detections") or baseline_dets),
    )
    return worst_atk


def build_markdown(cycles: list[dict]) -> str:
    lines: list[str] = [
        "# Cycle Report",
        "",
        f"Generated from {len(cycles)} completed cycle(s) in `outputs/cycle_history/`.",
        "",
    ]

    # ── Executive summary table ──
    lines += [
        "## Executive Summary",
        "",
        "| Cycle | Date | Baseline mAP50 | Best defended mAP50 | Best config | Worst attack |",
        "|---|---|---:|---:|---|---|",
    ]
    for i, cycle in enumerate(cycles, 1):
        validation_results = cycle.get("validation_results", {})
        baseline, attack_map, defended_map = _parse_validation(validation_results)
        baseline_map50 = baseline.get("mAP50") if baseline else None
        best_def_map50, best_label = _best_defended_map50(defended_map, attack_map)
        worst_atk = _worst_attack(attack_map, baseline)
        date = _fmt_date(cycle.get("finished_at", ""))
        lines.append(
            f"| {i} | {date} | {_fmt_map50(baseline_map50)} | {_fmt_map50(best_def_map50)}"
            f" | {best_label} | {worst_atk} |"
        )

    lines += [""]

    latest_cycle = cycles[-1] if cycles else {}
    current_attacks = set(latest_cycle.get("top_attacks", []))
    current_defenses = set(latest_cycle.get("top_defenses", []))
    comparable_cycles = 0
    legacy_cycles = 0
    pipeline_semantics_counts = {
        CURRENT_PIPELINE_SEMANTICS: 0,
        LEGACY_PIPELINE_SEMANTICS: 0,
        UNKNOWN_PIPELINE_SEMANTICS: 0,
        MIXED_PIPELINE_SEMANTICS: 0,
    }
    for cycle in cycles:
        cat_attacks = set(cycle.get("top_attacks", []))
        if current_attacks and cat_attacks and cat_attacks.issubset(current_attacks):
            comparable_cycles += 1
        else:
            legacy_cycles += 1
        pipeline_semantics = _cycle_pipeline_semantics(cycle)
        pipeline_semantics_counts[pipeline_semantics] = (
            pipeline_semantics_counts.get(pipeline_semantics, 0) + 1
        )

    lines += [
        "## Comparability Notes",
        "",
        "Cycle history includes catalogue eras with different attack/defense sets.",
        "Current trends focus on the latest catalogue; legacy trends are shown separately.",
        "Pipeline semantics are also tracked so post-switch defended runs can be distinguished from older eras.",
        "",
        f"- Comparable cycles (latest-catalogue aligned): **{comparable_cycles}**",
        f"- Legacy/non-comparable cycles: **{legacy_cycles}**",
        f"- `attack_then_defense` cycles: **{pipeline_semantics_counts[CURRENT_PIPELINE_SEMANTICS]}**",
        f"- `defense_then_attack` cycles: **{pipeline_semantics_counts[LEGACY_PIPELINE_SEMANTICS]}**",
        f"- `legacy_unknown` cycles: **{pipeline_semantics_counts[UNKNOWN_PIPELINE_SEMANTICS]}**",
        f"- `mixed` cycles: **{pipeline_semantics_counts[MIXED_PIPELINE_SEMANTICS]}**",
        "",
    ]
    if (
        pipeline_semantics_counts[CURRENT_PIPELINE_SEMANTICS] > 0
        and (
            pipeline_semantics_counts[LEGACY_PIPELINE_SEMANTICS] > 0
            or pipeline_semantics_counts[UNKNOWN_PIPELINE_SEMANTICS] > 0
            or pipeline_semantics_counts[MIXED_PIPELINE_SEMANTICS] > 0
        )
    ):
        lines += [
            "Treat defended results from the `attack_then_defense` era as the canonical post-switch series.",
            "",
        ]

    # ── Baseline mAP50 trend ──
    baseline_map50s = []
    for cycle in cycles:
        baseline_entry, _, _ = _parse_validation(cycle.get("validation_results", {}))
        baseline_map50s.append(baseline_entry.get("mAP50") if baseline_entry else None)

    if any(v is not None for v in baseline_map50s):
        lines += [
            "## Baseline mAP50 Trend",
            "",
            "How the model's clean (unattacked) performance has changed across cycles.",
            "Upward trend = model fortification is working.",
            "",
            "| Cycle | Baseline mAP50 | Change vs prev |",
            "|---|---:|---:|",
        ]
        for i, m in enumerate(baseline_map50s, 1):
            if i > 1 and baseline_map50s[i - 2] is not None and m is not None:
                delta = m - baseline_map50s[i - 2]
                change = f"{delta:+.4f}"
            else:
                change = "—"
            lines.append(f"| {i} | {_fmt_map50(m)} | {change} |")
        lines += [""]

    # ── Attack × Defense trend tables ──
    # Collect all (attack, defense) pairs seen across cycles
    all_pairs: set[tuple[str, str]] = set()
    for cycle in cycles:
        _, _, defended_map = _parse_validation(cycle.get("validation_results", {}))
        all_pairs.update(defended_map.keys())

    if all_pairs:
        lines += ["## Current Catalogue Trends", ""]
        lines += [
            "Defended mAP50 for attack+defense pairs in the latest active catalogue.",
            "Higher = better defense. Baseline mAP50 shown for reference.",
            "",
        ]

        current_pairs = {
            (atk, dfn)
            for (atk, dfn) in all_pairs
            if (not current_attacks or atk in current_attacks)
            and (not current_defenses or dfn in current_defenses)
        }
        legacy_pairs = all_pairs - current_pairs

        attacks_seen = sorted({atk for atk, _ in current_pairs})
        for atk in attacks_seen:
            defenses_for_atk = sorted({dfn for a, dfn in current_pairs if a == atk})
            if not defenses_for_atk:
                continue

            lines.append(f"### Attack: {atk}")
            lines.append("")
            header = "| Cycle | Baseline mAP50 | Attack mAP50 |" + "".join(
                f" {dfn} |" for dfn in defenses_for_atk
            )
            sep = "|---|---:|---:|" + "---:|" * len(defenses_for_atk)
            lines += [header, sep]

            for i, cycle in enumerate(cycles, 1):
                validation_results = cycle.get("validation_results", {})
                baseline, attack_map, defended_map = _parse_validation(validation_results)
                base_m = baseline.get("mAP50") if baseline else None
                atk_entry = attack_map.get(atk, {})
                atk_m = atk_entry.get("mAP50")
                row = f"| {i} | {_fmt_map50(base_m)} | {_fmt_map50(atk_m)} |"
                for dfn in defenses_for_atk:
                    def_entry = defended_map.get((atk, dfn), {})
                    row += f" {_fmt_map50(def_entry.get('mAP50'))} |"
                lines.append(row)
            lines += [""]

        lines += ["## Legacy Catalogue Trends", ""]
        if not legacy_pairs:
            lines += ["No legacy-only attack/defense pairs detected.", ""]
        else:
            lines += [
                "Historical pairs from older catalogue configurations are listed separately.",
                "",
            ]
            legacy_attacks = sorted({atk for atk, _ in legacy_pairs})
            for atk in legacy_attacks:
                defenses_for_atk = sorted({dfn for a, dfn in legacy_pairs if a == atk})
                if not defenses_for_atk:
                    continue
                lines.append(f"### Attack: {atk}")
                lines.append("")
                header = "| Cycle | Baseline mAP50 | Attack mAP50 |" + "".join(
                    f" {dfn} |" for dfn in defenses_for_atk
                )
                sep = "|---|---:|---:|" + "---:|" * len(defenses_for_atk)
                lines += [header, sep]
                for i, cycle in enumerate(cycles, 1):
                    validation_results = cycle.get("validation_results", {})
                    baseline, attack_map, defended_map = _parse_validation(validation_results)
                    base_m = baseline.get("mAP50") if baseline else None
                    atk_entry = attack_map.get(atk, {})
                    atk_m = atk_entry.get("mAP50")
                    row = f"| {i} | {_fmt_map50(base_m)} | {_fmt_map50(atk_m)} |"
                    for dfn in defenses_for_atk:
                        def_entry = defended_map.get((atk, dfn), {})
                        row += f" {_fmt_map50(def_entry.get('mAP50'))} |"
                    lines.append(row)
                lines += [""]

    # ── Training signal history ──
    lines += [
        "## Training Signal History",
        "",
        "The worst_attack identified after each cycle drives DPC-UNet retraining in Colab.",
        "",
        "| Cycle | Worst attack | Weakest defense | Recovery |",
        "|---|---|---|---:|",
    ]
    for i, cycle in enumerate(cycles, 1):
        # Re-derive from validation_results (mirrors _write_training_signal logic)
        validation_results = cycle.get("validation_results", {})
        baseline, attack_map, defended_map = _parse_validation(validation_results)
        baseline_dets = baseline.get("detections") if baseline else None

        if not baseline_dets:
            lines.append(f"| {i} | n/a | n/a | n/a |")
            continue

        defense_recovery: dict[str, dict[str, float]] = {}
        for (atk, dfn), def_entry in defended_map.items():
            atk_dets = attack_map.get(atk, {}).get("detections")
            def_dets = def_entry.get("detections")
            if atk_dets is None or def_dets is None:
                continue
            drop = baseline_dets - atk_dets
            if drop > 0:
                recovery = (def_dets - atk_dets) / drop
                defense_recovery.setdefault(atk, {})[dfn] = recovery

        if not defense_recovery:
            lines.append(f"| {i} | n/a | n/a | n/a |")
            continue

        atk_avg = sorted(
            ((sum(v.values()) / len(v), a) for a, v in defense_recovery.items()),
        )
        worst_atk = atk_avg[0][1]
        rmap = defense_recovery[worst_atk]
        weakest_dfn = min(rmap, key=lambda d: rmap[d])
        weakest_rec = rmap[weakest_dfn]
        lines.append(f"| {i} | {worst_atk} | {weakest_dfn} | {weakest_rec:.3f} |")

    lines += [""]
    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def generate_reports(
    history_dir: Path | None = None,
    csv_out: Path | None = None,
    md_out: Path | None = None,
) -> tuple[Path, Path]:
    """Read cycle history and write cycle_report.csv + cycle_report.md.

    Returns paths to (csv_out, md_out).
    """
    history_dir = history_dir or HISTORY_DIR_DEFAULT
    csv_out = csv_out or OUTPUTS / "cycle_report.csv"
    md_out = md_out or OUTPUTS / "cycle_report.md"

    cycles = _load_cycles(history_dir)
    write_csv(cycles, csv_out)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(build_markdown(cycles), encoding="utf-8")
    return csv_out, md_out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate longitudinal cycle report.")
    parser.add_argument(
        "--history-dir",
        default=str(HISTORY_DIR_DEFAULT),
        help="Directory containing cycle_*.json files.",
    )
    parser.add_argument(
        "--csv-out",
        default=str(OUTPUTS / "cycle_report.csv"),
        help="Output CSV path.",
    )
    parser.add_argument(
        "--md-out",
        default=str(OUTPUTS / "cycle_report.md"),
        help="Output markdown path.",
    )
    args = parser.parse_args()

    csv_path, md_path = generate_reports(
        history_dir=Path(args.history_dir),
        csv_out=Path(args.csv_out),
        md_out=Path(args.md_out),
    )
    print(f"CSV:      {csv_path}")
    print(f"Markdown: {md_path}")


if __name__ == "__main__":
    main()
