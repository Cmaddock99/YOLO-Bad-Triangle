from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def _load_predictions(jsonl_path: Path) -> dict[str, dict[str, Any]]:
    """Load predictions.jsonl → {image_id: record}."""
    records: dict[str, dict[str, Any]] = {}
    if not jsonl_path.is_file():
        return records
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            image_id = str(rec.get("image_id", ""))
            if image_id:
                records[image_id] = rec
    return records


def _count_detections(record: dict[str, Any]) -> int:
    scores = record.get("scores")
    if scores is None:
        return 0
    return len(scores)


def _avg_confidence(record: dict[str, Any]) -> float | None:
    scores = record.get("scores")
    if not scores:
        return None
    return float(np.mean(scores))


def _paired_detection_drop(
    baseline_counts: np.ndarray,
    attack_counts: np.ndarray,
) -> float | None:
    total_baseline = float(baseline_counts.sum())
    if total_baseline < 1e-9:
        return None
    return float((total_baseline - attack_counts.sum()) / total_baseline)


def _paired_conf_drop(
    baseline_confs: np.ndarray,
    attack_confs: np.ndarray,
) -> float | None:
    mean_baseline = float(baseline_confs.mean())
    if abs(mean_baseline) < 1e-9:
        return None
    return float((mean_baseline - float(attack_confs.mean())) / mean_baseline)


def bootstrap_paired_ci(
    baseline_jsonl: Path,
    attack_jsonl: Path,
    *,
    n_bootstrap: int = 2000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, Any]:
    """Paired bootstrap CI for detection_drop and avg_conf_drop.

    Pairs predictions by image_id. mAP50 is NOT bootstrappable from predictions.jsonl
    alone (requires per-image ground truth), so only detection and confidence CIs
    are computed.

    Returns a dict with keys:
      detection_drop_point, detection_drop_lower, detection_drop_upper,
      detection_drop_ci_computed,
      conf_drop_point, conf_drop_lower, conf_drop_upper,
      conf_drop_ci_computed,
      n_images, n_bootstrap, alpha
    """
    result: dict[str, Any] = {
        "detection_drop_point": None,
        "detection_drop_lower": None,
        "detection_drop_upper": None,
        "detection_drop_ci_computed": False,
        "conf_drop_point": None,
        "conf_drop_lower": None,
        "conf_drop_upper": None,
        "conf_drop_ci_computed": False,
        "n_images": 0,
        "n_bootstrap": n_bootstrap,
        "alpha": alpha,
        "note": "mAP50 CI not computed — requires per-image ground truth",
    }

    baseline_records = _load_predictions(baseline_jsonl)
    attack_records = _load_predictions(attack_jsonl)
    common_ids = sorted(set(baseline_records) & set(attack_records))
    result["n_images"] = len(common_ids)
    if len(common_ids) < 4:
        result["note"] = (
            f"mAP50 CI not computed — requires per-image ground truth; "
            f"detection/conf CI not computed — only {len(common_ids)} paired images"
        )
        return result

    baseline_det = np.array([_count_detections(baseline_records[i]) for i in common_ids], dtype=float)
    attack_det = np.array([_count_detections(attack_records[i]) for i in common_ids], dtype=float)

    baseline_conf_raw = [_avg_confidence(baseline_records[i]) for i in common_ids]
    attack_conf_raw = [_avg_confidence(attack_records[i]) for i in common_ids]
    conf_valid_mask = [b is not None and a is not None for b, a in zip(baseline_conf_raw, attack_conf_raw)]
    baseline_conf = np.array([v for v, ok in zip(baseline_conf_raw, conf_valid_mask) if ok], dtype=float)
    attack_conf = np.array([v for v, ok in zip(attack_conf_raw, conf_valid_mask) if ok], dtype=float)

    rng = np.random.default_rng(seed)
    n = len(common_ids)

    # Detection drop bootstrap
    det_samples = np.empty(n_bootstrap)
    for k in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        val = _paired_detection_drop(baseline_det[idx], attack_det[idx])
        det_samples[k] = val if val is not None else float("nan")

    det_valid = det_samples[~np.isnan(det_samples)]
    if len(det_valid) >= n_bootstrap * 0.9:
        lo = float(np.percentile(det_valid, 100 * alpha / 2))
        hi = float(np.percentile(det_valid, 100 * (1 - alpha / 2)))
        point = _paired_detection_drop(baseline_det, attack_det)
        result["detection_drop_point"] = point
        result["detection_drop_lower"] = lo
        result["detection_drop_upper"] = hi
        result["detection_drop_ci_computed"] = True

    # Confidence drop bootstrap
    if len(baseline_conf) >= 4:
        nc = len(baseline_conf)
        conf_samples = np.empty(n_bootstrap)
        for k in range(n_bootstrap):
            idx = rng.integers(0, nc, size=nc)
            val = _paired_conf_drop(baseline_conf[idx], attack_conf[idx])
            conf_samples[k] = val if val is not None else float("nan")

        conf_valid = conf_samples[~np.isnan(conf_samples)]
        if len(conf_valid) >= n_bootstrap * 0.9:
            lo = float(np.percentile(conf_valid, 100 * alpha / 2))
            hi = float(np.percentile(conf_valid, 100 * (1 - alpha / 2)))
            point = _paired_conf_drop(baseline_conf, attack_conf)
            result["conf_drop_point"] = point
            result["conf_drop_lower"] = lo
            result["conf_drop_upper"] = hi
            result["conf_drop_ci_computed"] = True

    return result
