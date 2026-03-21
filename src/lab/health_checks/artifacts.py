from __future__ import annotations

from pathlib import Path


_ARTIFACT_SETS: dict[str, tuple[str, ...]] = {
    "demo_gate": ("metrics.json", "run_summary.json", "predictions.jsonl"),
    "compat": ("metrics.json", "run_summary.json"),
}


def required_artifact_paths(*, output_root: Path, contract_name: str = "demo_gate") -> list[Path]:
    names = _ARTIFACT_SETS.get(contract_name)
    if names is None:
        raise ValueError(f"Unknown artifact contract '{contract_name}'.")
    return [output_root / name for name in names]


def assert_files_exist(*, paths: list[Path], context: str) -> None:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        missing_rendered = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"{context} missing required file(s): {missing_rendered}")


def assert_required_artifacts(*, output_root: Path, contract_name: str = "demo_gate") -> list[Path]:
    required = required_artifact_paths(output_root=output_root, contract_name=contract_name)
    assert_files_exist(paths=required, context=f"Artifact contract '{contract_name}'")
    return required
