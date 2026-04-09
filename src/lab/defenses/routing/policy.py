from __future__ import annotations

import logging
from dataclasses import dataclass

from .attack_detector import AttackSignal

LOGGER = logging.getLogger(__name__)

_KNOWN_ATTACK_HINTS = frozenset({
    "", "none", "identity",
    "fgsm", "pgd", "ifgsm", "bim",
    "deepfool",
    "square", "cw",
})


@dataclass(frozen=True)
class RoutingThresholds:
    low_noise_hf: float = 0.03
    strong_hf: float = 0.08
    strong_laplacian: float = 0.02


def choose_route(
    *,
    signal: AttackSignal,
    attack_hint: str | None,
    thresholds: RoutingThresholds,
) -> str:
    hint = (attack_hint or "").strip().lower()
    if hint not in _KNOWN_ATTACK_HINTS:
        LOGGER.warning(
            "routing: unknown attack hint '%s', falling back to signal-based routing.", hint
        )
    if hint in {"none", "identity", ""} and signal.high_freq_energy < thresholds.low_noise_hf:
        return "passthrough"
    if hint in {"fgsm", "pgd", "ifgsm", "bim"}:
        return "median_cdog"
    if hint in {"deepfool"}:
        return "cdog_only"
    if signal.high_freq_energy >= thresholds.strong_hf:
        return "median_cdog"
    if signal.laplacian_var >= thresholds.strong_laplacian:
        return "cdog_only"
    return "median_only"
