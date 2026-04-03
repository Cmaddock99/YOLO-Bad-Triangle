from __future__ import annotations

from typing import Any

from lab.config.contracts import REPORTING_AUTHORITY_AUTHORITATIVE
from lab.eval.framework_metrics import is_validation_success

# Warning codes
WARN_NO_BASELINE = "NO_BASELINE"
WARN_MULTIPLE_BASELINES = "MULTIPLE_BASELINES"
WARN_NO_VALIDATION = "NO_VALIDATION"
WARN_LOW_ATTACK_COUNT = "LOW_ATTACK_COUNT"
WARN_HIGH_CONFIDENCE_FLOOR = "HIGH_CONFIDENCE_FLOOR"
WARN_DEFENSE_RECOVERY_UNDEFINED = "DEFENSE_RECOVERY_UNDEFINED"
WARN_DEFENSE_DEGRADES_PERFORMANCE = "DEFENSE_DEGRADES_PERFORMANCE"
WARN_ATTACK_BELOW_NOISE = "ATTACK_BELOW_NOISE"
WARN_MISSING_PER_CLASS = "MISSING_PER_CLASS"


def _warn(code: str, message: str, **extra: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"code": code, "message": message}
    entry.update(extra)
    return entry


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _has_authoritative_rows(rows: list[dict[str, Any]]) -> bool:
    return any(
        _normalize_text(row.get("authority")) == REPORTING_AUTHORITY_AUTHORITATIVE
        for row in rows
    )


def _prefer_authoritative_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    authoritative = [
        row for row in rows
        if _normalize_text(row.get("authority")) == REPORTING_AUTHORITY_AUTHORITATIVE
    ]
    return authoritative if authoritative else rows


def evaluate_warnings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Inspect a summary payload and return a list of warning dicts.

    Each warning has at minimum: {"code": str, "message": str}.
    """
    warnings: list[dict[str, Any]] = []

    baseline = payload.get("baseline")
    if baseline is None:
        warnings.append(_warn(WARN_NO_BASELINE, "No baseline run found in the runs root."))
        return warnings  # remaining checks depend on baseline

    candidate_count = int((baseline or {}).get("candidate_count", 1))
    if candidate_count > 1:
        warnings.append(
            _warn(
                WARN_MULTIPLE_BASELINES,
                f"{candidate_count} no-attack/no-defense runs found; "
                f"'{baseline.get('run_name')}' selected (first alphabetically). "
                "Runs with different image counts or validation status may produce misleading comparisons.",
                baseline_used=baseline.get("run_name"),
                candidate_count=candidate_count,
            )
        )

    attack_rows: list[dict[str, Any]] = _prefer_authoritative_rows(
        list(payload.get("attack_effectiveness_rows") or [])
    )
    has_validation = any(
        is_validation_success(r.get("validation_status"))
        for r in attack_rows
    )
    if not has_validation:
        warnings.append(
            _warn(
                WARN_NO_VALIDATION,
                "No run has a successful validation result; mAP50 metrics are unavailable. "
                "Re-run with --validation-enabled for complete results.",
            )
        )

    if len(attack_rows) < 2:
        warnings.append(
            _warn(
                WARN_LOW_ATTACK_COUNT,
                f"Only {len(attack_rows)} attack run(s) found; comparison results may be incomplete.",
                attack_count=len(attack_rows),
            )
        )

    baseline_conf = baseline.get("avg_confidence")
    if baseline_conf is not None and float(baseline_conf) < 0.5:
        warnings.append(
            _warn(
                WARN_HIGH_CONFIDENCE_FLOOR,
                f"Baseline avg_confidence ({baseline_conf:.4f}) is below 0.5; "
                "model may be under-confident on this dataset.",
                baseline_avg_confidence=baseline_conf,
            )
        )

    # Deduplicate ATTACK_BELOW_NOISE by attack name
    noisy_attacks_seen: set[str] = set()
    for row in attack_rows:
        attack_name = str(row.get("attack") or "")
        if attack_name in noisy_attacks_seen:
            continue
        eff = row.get("mAP50_effectiveness")
        conf_eff = row.get("avg_conf_effectiveness")
        if eff is None and conf_eff is not None and abs(float(conf_eff)) < 0.05:
            noisy_attacks_seen.add(attack_name)
            warnings.append(
                _warn(
                    WARN_ATTACK_BELOW_NOISE,
                    f"Attack '{attack_name}' shows < 5% confidence suppression — "
                    "may be within noise or misconfigured.",
                    attack=attack_name,
                    avg_conf_effectiveness=conf_eff,
                )
            )
        elif eff is not None and abs(float(eff)) < 0.05:
            noisy_attacks_seen.add(attack_name)
            warnings.append(
                _warn(
                    WARN_ATTACK_BELOW_NOISE,
                    f"Attack '{attack_name}' shows < 5% mAP50 drop — "
                    "may be within noise or misconfigured.",
                    attack=attack_name,
                    mAP50_effectiveness=eff,
                )
            )

    # Deduplicate DEFENSE_RECOVERY_UNDEFINED and DEFENSE_DEGRADES_PERFORMANCE by (attack, defense)
    defense_rows: list[dict[str, Any]] = _prefer_authoritative_rows(
        list(payload.get("defense_recovery_rows") or [])
    )
    recovery_undef_seen: set[tuple[str, str]] = set()
    recovery_degrades_seen: set[tuple[str, str]] = set()
    for row in defense_rows:
        key = (str(row.get("attack") or ""), str(row.get("defense") or ""))
        if key not in recovery_undef_seen:
            if row.get("mAP50_recovery_normalized") is None and row.get("avg_conf_recovery_normalized") is None:
                recovery_undef_seen.add(key)
                warnings.append(
                    _warn(
                        WARN_DEFENSE_RECOVERY_UNDEFINED,
                        f"Defense recovery undefined for attack='{row.get('attack')}' "
                        f"defense='{row.get('defense')}' — "
                        "attack may have had no measurable effect or metrics are missing.",
                        attack=row.get("attack"),
                        defense=row.get("defense"),
                    )
                )
        if key not in recovery_degrades_seen:
            # Use detection recovery if available, else mAP50 recovery
            recovery = row.get("detection_recovery_normalized")
            if recovery is None:
                recovery = row.get("mAP50_recovery_normalized")
            if recovery is not None and float(recovery) < -0.1:
                recovery_degrades_seen.add(key)
                warnings.append(
                    _warn(
                        WARN_DEFENSE_DEGRADES_PERFORMANCE,
                        f"Defense '{row.get('defense')}' against attack '{row.get('attack')}' "
                        f"degrades performance beyond the attack alone (recovery={float(recovery):.3f}). "
                        "Defense may be misconfigured or incompatible with this attack.",
                        attack=row.get("attack"),
                        defense=row.get("defense"),
                        recovery=recovery,
                    )
                )

    raw_per_class_rows: list[dict[str, Any]] = list(payload.get("per_class_vulnerability_rows") or [])
    per_class_rows: list[dict[str, Any]]
    if _has_authoritative_rows(attack_rows):
        per_class_rows = [
            row for row in raw_per_class_rows
            if _normalize_text(row.get("authority")) == REPORTING_AUTHORITY_AUTHORITATIVE
        ]
    else:
        per_class_rows = _prefer_authoritative_rows(raw_per_class_rows)
    if not per_class_rows and attack_rows:
        warnings.append(
            _warn(
                WARN_MISSING_PER_CLASS,
                "No per-class detection data found; per_class_vulnerability.csv will be empty. "
                "Ensure metrics.json includes predictions.per_class.",
            )
        )

    return warnings
