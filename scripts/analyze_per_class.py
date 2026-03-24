"""Per-class vulnerability analysis.

Scans outputs/framework_runs/ for completed runs, extracts per-class
detection data from metrics.json, and reports which COCO classes suffer
the most detection drop under each attack.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/analyze_per_class.py
    PYTHONPATH=src ./.venv/bin/python scripts/analyze_per_class.py \
        --runs-root outputs/framework_runs \
        --baseline-attack none \
        --top-n 20 \
        --output per_class_report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.eval.derived_metrics import compute_per_class_detection_drop

# COCO 80-class names (index 0–79).
COCO_CLASSES: dict[int, str] = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
    5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
    10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
    14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow",
    20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack",
    25: "umbrella", 26: "handbag", 27: "tie", 28: "suitcase", 29: "frisbee",
    30: "skis", 31: "snowboard", 32: "sports ball", 33: "kite",
    34: "baseball bat", 35: "baseball glove", 36: "skateboard",
    37: "surfboard", 38: "tennis racket", 39: "bottle", 40: "wine glass",
    41: "cup", 42: "fork", 43: "knife", 44: "spoon", 45: "bowl",
    46: "banana", 47: "apple", 48: "sandwich", 49: "orange", 50: "broccoli",
    51: "carrot", 52: "hot dog", 53: "pizza", 54: "donut", 55: "cake",
    56: "chair", 57: "couch", 58: "potted plant", 59: "bed",
    60: "dining table", 61: "toilet", 62: "tv", 63: "laptop", 64: "mouse",
    65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave",
    69: "oven", 70: "toaster", 71: "sink", 72: "refrigerator", 73: "book",
    74: "clock", 75: "vase", 76: "scissors", 77: "teddy bear",
    78: "hair drier", 79: "toothbrush",
}


def _load_run(run_dir: Path) -> dict | None:
    """Load run_summary + metrics from a framework run directory."""
    summary_path = run_dir / "run_summary.json"
    metrics_path = run_dir / "metrics.json"
    if not summary_path.exists() or not metrics_path.exists():
        return None
    try:
        summary = json.loads(summary_path.read_text())
        metrics = json.loads(metrics_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return {"summary": summary, "metrics": metrics, "run_dir": str(run_dir)}


def _extract_per_class(metrics: dict) -> dict[int, dict]:
    """Return per_class dict keyed by int class_id."""
    raw = metrics.get("predictions", {}).get("per_class", {})
    return {int(k): v for k, v in raw.items()}


def _gather_runs(runs_root: Path) -> list[dict]:
    runs = []
    for candidate in sorted(runs_root.iterdir()):
        if not candidate.is_dir():
            continue
        run = _load_run(candidate)
        if run is None:
            continue
        runs.append(run)
    return runs


def _attack_name(run: dict) -> str:
    return run["summary"].get("attack", {}).get("name", "unknown")


def _defense_name(run: dict) -> str:
    return run["summary"].get("defense", {}).get("name", "none")


def analyze(
    runs_root: Path,
    baseline_attack: str = "none",
    top_n: int = 20,
) -> dict:
    """Compute per-class drop for each attack relative to baseline runs."""
    runs = _gather_runs(runs_root)
    if not runs:
        print(f"No completed runs found in {runs_root}", file=sys.stderr)
        return {}

    # Separate baseline runs (no attack, no defense) from attack runs.
    baseline_runs = [
        r for r in runs
        if _attack_name(r) == baseline_attack and _defense_name(r) == "none"
    ]
    attack_runs = [
        r for r in runs
        if _attack_name(r) != baseline_attack and _defense_name(r) == "none"
    ]

    if not baseline_runs:
        print(
            f"No baseline runs found (attack={baseline_attack!r}, defense='none'). "
            "Cannot compute per-class drop.",
            file=sys.stderr,
        )
        return {}

    # Merge per-class counts across all baseline runs (sum counts).
    merged_baseline: dict[int, dict] = defaultdict(lambda: {"count": 0, "mean_confidence": None})
    for r in baseline_runs:
        for cid, data in _extract_per_class(r["metrics"]).items():
            merged_baseline[cid]["count"] += data.get("count", 0)
            merged_baseline[cid]["class_name"] = data.get("class_name", COCO_CLASSES.get(cid, str(cid)))

    # For each unique attack, merge per-class counts and compute drop.
    results: dict[str, list[dict]] = {}
    attacks_seen = sorted({_attack_name(r) for r in attack_runs})

    for attack in attacks_seen:
        atk_subset = [r for r in attack_runs if _attack_name(r) == attack]
        merged_attacked: dict[int, dict] = defaultdict(lambda: {"count": 0})
        for r in atk_subset:
            for cid, data in _extract_per_class(r["metrics"]).items():
                merged_attacked[cid]["count"] += data.get("count", 0)

        drops = compute_per_class_detection_drop(
            dict(merged_baseline), dict(merged_attacked)
        )

        rows = []
        for cid, drop in drops.items():
            base_count = merged_baseline.get(cid, {}).get("count", 0)
            atk_count = merged_attacked.get(cid, {}).get("count", 0)
            class_name = merged_baseline.get(cid, {}).get(
                "class_name", COCO_CLASSES.get(cid, str(cid))
            )
            rows.append({
                "class_id": cid,
                "class_name": class_name,
                "baseline_count": base_count,
                "attacked_count": atk_count,
                "detection_drop": round(drop, 4) if drop is not None else None,
            })

        # Sort by detection_drop descending (most affected first), None last.
        rows.sort(
            key=lambda x: (x["detection_drop"] is None, -(x["detection_drop"] or 0))
        )
        results[attack] = rows[:top_n]

    return results


def _print_table(attack: str, rows: list[dict]) -> None:
    print(f"\n{'='*60}")
    print(f"Attack: {attack}  (top {len(rows)} classes by detection drop)")
    print(f"{'='*60}")
    print(f"{'Class':20s} {'ID':>4}  {'Baseline':>8}  {'Attacked':>8}  {'Drop':>8}")
    print(f"{'-'*20}  {'-'*4}  {'-'*8}  {'-'*8}  {'-'*8}")
    for row in rows:
        drop_str = f"{row['detection_drop']:.2%}" if row["detection_drop"] is not None else "   N/A"
        print(
            f"{row['class_name']:20s}  {row['class_id']:4d}  "
            f"{row['baseline_count']:8d}  {row['attacked_count']:8d}  {drop_str:>8}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Per-class vulnerability analysis")
    parser.add_argument(
        "--runs-root",
        default=str(ROOT / "outputs/framework_runs"),
        help="Directory containing framework run subdirectories",
    )
    parser.add_argument(
        "--baseline-attack",
        default="none",
        help="Attack name to treat as baseline (default: none)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top classes to show per attack (default: 20)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write JSON results",
    )
    args = parser.parse_args()

    results = analyze(
        Path(args.runs_root),
        baseline_attack=args.baseline_attack,
        top_n=args.top_n,
    )

    if not results:
        sys.exit(1)

    for attack, rows in sorted(results.items()):
        _print_table(attack, rows)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(results, indent=2))
        print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
