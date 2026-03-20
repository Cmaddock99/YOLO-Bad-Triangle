from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from .regression import resolve_runtime_profile

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _to_int(value: Any) -> int | None:
    try:
        if value in ("", None):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _count_images(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES)


def load_config_preflight_stats(*, config_path: Path, attack_name: str = "fgsm") -> dict[str, Any]:
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid config payload for preflight: {config_path}")

    data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
    runner = payload.get("runner", {}) if isinstance(payload.get("runner"), dict) else {}
    experiments = payload.get("experiments", [])

    source_dir_raw = data.get("source_dir") or data.get("image_dir")
    source_dir = None
    if isinstance(source_dir_raw, str) and source_dir_raw.strip():
        candidate = Path(source_dir_raw.strip())
        source_dir = candidate if candidate.is_absolute() else Path(__file__).resolve().parents[3] / candidate

    dataset_total_images = _count_images(source_dir) if source_dir else 0
    max_images = _to_int(runner.get("max_images"))
    selected_images = min(dataset_total_images, max_images) if max_images and max_images > 0 else dataset_total_images

    expected_attack_rows = None
    fgsm_present = None
    if isinstance(experiments, list) and experiments:
        attack_values = [str(item.get("attack", "")) for item in experiments if isinstance(item, dict)]
        expected_attack_rows = sum(1 for attack in attack_values if attack == attack_name)
        fgsm_present = attack_name in attack_values
    else:
        attack_cfg = payload.get("attack", {}) if isinstance(payload.get("attack"), dict) else {}
        attack_value = str(attack_cfg.get("name", ""))
        expected_attack_rows = 1 if attack_value == attack_name else 0
        fgsm_present = attack_value == attack_name

    return {
        "dataset_total_images": dataset_total_images,
        "selected_image_count": selected_images,
        "expected_attack_rows": expected_attack_rows,
        "fgsm_present": fgsm_present,
    }


def load_csv_preflight_stats(*, csv_path: Path, attack_name: str = "fgsm") -> dict[str, Any]:
    if not csv_path.is_file():
        return {"observed_attack_rows": 0, "fgsm_present": False}
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    observed_rows = [row for row in rows if row.get("attack") == attack_name]
    return {
        "observed_attack_rows": len(observed_rows),
        "fgsm_present": len(observed_rows) > 0,
    }


def validate_profile_expectations(profile: str, dataset_stats: dict[str, Any]) -> None:
    profile_policy = resolve_runtime_profile(profile)
    errors: list[str] = []

    dataset_total = _to_int(dataset_stats.get("dataset_total_images"))
    selected_count = _to_int(dataset_stats.get("selected_image_count"))
    expected_rows = _to_int(dataset_stats.get("expected_attack_rows"))
    observed_rows = _to_int(dataset_stats.get("observed_attack_rows"))

    if dataset_total is not None and dataset_total <= 0:
        errors.append("dataset is empty or missing expected image files")
    if selected_count is not None and selected_count <= 0:
        errors.append("selected image count is zero after max_images/source filtering")

    required_rows = _to_int(dataset_stats.get("required_attack_rows"))
    if required_rows is None:
        required_rows = 1 if profile_policy["allow_sparse_fgsm"] else 2

    if expected_rows is not None and expected_rows < required_rows:
        errors.append(
            f"expected FGSM attack rows ({expected_rows}) are below required minimum ({required_rows}) "
            f"for profile={profile_policy['name']}"
        )
    if observed_rows is not None and observed_rows < required_rows:
        errors.append(
            f"observed FGSM attack rows ({observed_rows}) are below required minimum ({required_rows}) "
            f"for profile={profile_policy['name']}"
        )

    fgsm_required = bool(dataset_stats.get("fgsm_required", True))
    fgsm_present = dataset_stats.get("fgsm_present")
    if fgsm_required and fgsm_present is False:
        errors.append("FGSM rows are missing but required by profile preflight")

    if errors:
        rendered = "\n".join(f"- {line}" for line in errors)
        raise ValueError(f"Profile preflight failed for profile={profile_policy['name']}:\n{rendered}")
