#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lab.config.contracts import (
    DEFAULT_CONF,
    DEFAULT_IMGSZ,
    DEFAULT_IOU,
    DEFAULT_MAX_CONFIDENCE_DELTA_PCT,
    DEFAULT_MAX_DETECTION_DELTA_PCT,
)
from lab.migration import (
    ValidationGateConfig,
    build_shadow_artifacts,
    compare_shadow_runs,
    enforce_validation_gate,
    temporary_legacy_runtime_override,
    read_framework_metrics,
    read_last_legacy_row,
)
from lab.migration.shadow_views import SHADOW_PAIRED_METRICS_CSV_FIELDS, build_paired_metrics_row
from lab.models.model_utils import model_label_from_path
from lab.health_checks import log_event
from lab.runners.cli_utils import sanitize_segment
from lab.runners.experiment_runner import ExperimentRunner
from lab.runners.run_experiment import UnifiedExperimentRunner
from lab.attacks.utils import iter_images
from lab.models.yolo_model import YOLOModel


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping config in: {path}")
    return payload


def _as_mapping(parent: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping at '{key}'.")
    return dict(value)


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _build_run_name(shared: Mapping[str, Any]) -> str:
    model = sanitize_segment(shared.get("model_label", shared.get("model_path", "model")), "model")
    attack = sanitize_segment(shared.get("attack_name", "none"), "attack")
    defense = sanitize_segment(shared.get("defense_name", "none"), "defense")
    seed = int(shared.get("seed", 42))
    return f"shadow_{model}_{attack}_{defense}_seed{seed}"


def _prepare_paired_source_and_dataset(
    *,
    source_dir: Path,
    max_images: int,
    working_dir: Path,
    names_source_yaml: Path | None = None,
) -> tuple[Path, Path]:
    if not source_dir.is_dir():
        raise FileNotFoundError(f"source_dir not found: {source_dir}")
    labels_dir = source_dir.parent / "labels"
    if not labels_dir.is_dir():
        raise FileNotFoundError(f"labels directory not found beside source_dir: {labels_dir}")

    images = sorted(iter_images(source_dir))
    if not images:
        raise ValueError(f"No images found in source_dir: {source_dir}")
    if max_images > 0:
        images = images[:max_images]

    dataset_root = working_dir / "paired_dataset"
    if dataset_root.exists():
        shutil.rmtree(dataset_root)
    images_out = dataset_root / "images"
    labels_out = dataset_root / "labels"
    images_out.mkdir(parents=True, exist_ok=True)
    labels_out.mkdir(parents=True, exist_ok=True)

    copied_labels = 0
    for src_image in images:
        target_image = images_out / src_image.name
        shutil.copy2(src_image, target_image)
        label_src = labels_dir / f"{src_image.stem}.txt"
        if label_src.is_file():
            shutil.copy2(label_src, labels_out / label_src.name)
            copied_labels += 1

    names_payload: Any = {}
    if names_source_yaml is not None and names_source_yaml.is_file():
        try:
            loaded = yaml.safe_load(names_source_yaml.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, Mapping):
                names_payload = loaded.get("names", {})
        except Exception:
            names_payload = {}

    dataset_yaml = dataset_root / "data.yaml"
    dataset_yaml.write_text(
        yaml.safe_dump(
            {
                "path": str(dataset_root.resolve()),
                "train": "images",
                "val": "images",
                "names": names_payload,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    log_event(
        component="shadow-parity",
        severity="INFO",
        message=f"paired source prepared: images={len(images)} labels={copied_labels} root={dataset_root}",
    )
    return images_out, dataset_yaml


def _write_paired_metrics_csv(
    *,
    output_path: Path,
    pair_id: str,
    legacy_artifact: Mapping[str, Any],
    framework_artifact: Mapping[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SHADOW_PAIRED_METRICS_CSV_FIELDS))
        writer.writeheader()
        writer.writerow(build_paired_metrics_row(pair_id, "legacy", legacy_artifact))
        writer.writerow(build_paired_metrics_row(pair_id, "framework", framework_artifact))


def _build_framework_prepared_validation_dataset(
    *,
    prepared_images_dir: Path,
    labels_dir: Path,
    target_root: Path,
    names_source_yaml: Path | None = None,
) -> Path:
    if target_root.exists():
        shutil.rmtree(target_root)
    images_out = target_root / "images"
    labels_out = target_root / "labels"
    images_out.mkdir(parents=True, exist_ok=True)

    for image_path in sorted(iter_images(prepared_images_dir)):
        target_image = images_out / image_path.name
        try:
            target_image.symlink_to(image_path.resolve())
        except OSError:
            shutil.copy2(image_path, target_image)

    try:
        if labels_out.exists() or labels_out.is_symlink():
            if labels_out.is_dir() and not labels_out.is_symlink():
                shutil.rmtree(labels_out)
            else:
                labels_out.unlink()
        labels_out.symlink_to(labels_dir.resolve(), target_is_directory=True)
    except OSError:
        shutil.copytree(labels_dir, labels_out)

    names_payload: Any = {}
    if names_source_yaml is not None and names_source_yaml.is_file():
        try:
            loaded = yaml.safe_load(names_source_yaml.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, Mapping):
                names_payload = loaded.get("names", {})
        except Exception:
            names_payload = {}

    dataset_yaml = target_root / "data.yaml"
    dataset_yaml.write_text(
        yaml.safe_dump(
            {
                "path": str(target_root.resolve()),
                "train": "images",
                "val": "images",
                "names": names_payload,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return dataset_yaml


def _recompute_framework_validation_on_prepared_images(
    *,
    framework_run_dir: Path,
    model_path: str,
    conf: float,
    iou: float,
    imgsz: int,
    seed: int,
    labels_dir: Path,
    names_source_yaml: Path | None = None,
) -> dict[str, Any]:
    prepared_images = framework_run_dir / "prepared_images"
    if not prepared_images.is_dir():
        raise FileNotFoundError(f"prepared_images directory not found: {prepared_images}")
    if not labels_dir.is_dir():
        raise FileNotFoundError(f"labels directory not found: {labels_dir}")

    val_root = framework_run_dir / "_parity_val_dataset"
    val_yaml = _build_framework_prepared_validation_dataset(
        prepared_images_dir=prepared_images,
        labels_dir=labels_dir,
        target_root=val_root,
        names_source_yaml=names_source_yaml,
    )

    model = YOLOModel(model_path)
    validation = model.validate(
        data=str(val_yaml),
        conf=conf,
        iou=iou,
        imgsz=imgsz,
        seed=seed,
    )
    box = getattr(validation, "box", None)
    if box is None:
        return {
            "precision": None,
            "recall": None,
            "mAP50": None,
            "mAP50-95": None,
        }
    return {
        "precision": float(getattr(box, "mp", 0.0)),
        "recall": float(getattr(box, "mr", 0.0)),
        "mAP50": float(getattr(box, "map50", 0.0)),
        "mAP50-95": float(getattr(box, "map", 0.0)),
    }


def _run_stability_snapshot(*, output_md: Path) -> dict[str, Any]:
    checks = [
        {
            "name": "framework_output_contract",
            "command": [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_framework_output_contract.py",
            ],
        },
        {
            "name": "reporting_pipeline",
            "command": [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_framework_reporting.py",
            ],
        },
        {
            "name": "overnight_runner",
            "command": [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_overnight_stress_runner.py",
            ],
        },
    ]

    results: list[dict[str, Any]] = []
    for check in checks:
        proc = subprocess.run(
            check["command"],
            cwd=str(ROOT),
            env={"PYTHONPATH": "src", **dict(os.environ)},
            capture_output=True,
            text=True,
            check=False,
        )
        results.append(
            {
                "name": check["name"],
                "exit_code": proc.returncode,
                "command": " ".join(check["command"]),
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "status": "PASS" if proc.returncode == 0 else "FAIL",
            }
        )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stability Baseline Snapshot",
        "",
        f"- `generated_at_utc`: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "| Check | Status | Exit code |",
        "|---|---|---:|",
    ]
    for result in results:
        lines.append(f"| `{result['name']}` | {result['status']} | {result['exit_code']} |")
    lines.extend(["", "## Exact Commands", ""])
    for result in results:
        lines.append(f"- `{result['command']}`")
    lines.extend(["", "## Outputs", ""])
    for result in results:
        lines.append(f"### {result['name']}")
        lines.append("")
        if result["stdout"]:
            lines.append("```")
            lines.append(result["stdout"])
            lines.append("```")
        if result["stderr"]:
            lines.append("```")
            lines.append(result["stderr"])
            lines.append("```")
        if not result["stdout"] and not result["stderr"]:
            lines.append("_No output captured._")
        lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return {"checks": results, "all_pass": all(item["status"] == "PASS" for item in results)}


def _render_summary_markdown(
    *,
    output_path: Path,
    parity_report: Mapping[str, Any],
    validation_errors: list[str],
    paired_metrics_csv: Path,
    baseline_report_path: Path,
) -> None:
    delta_summary = parity_report.get("delta_summary", {})
    parity_pass = bool(parity_report.get("parity_pass", False)) and not validation_errors
    symbol = "✅" if parity_pass else "❌"
    lines = [
        "# Shadow Parity Summary",
        "",
        f"{symbol} **{'PARITY PASS' if parity_pass else 'PARITY FAIL'}**",
        "",
        f"- `parity_score`: `{parity_report.get('parity_score', 0)}`",
        f"- `Δ detection difference (worst relative %)`: `{delta_summary.get('detection_worst_relative_pct')}`",
        f"- `Δ confidence difference (worst relative %)`: `{delta_summary.get('confidence_worst_relative_pct')}`",
        "",
        "## Artifacts",
        "",
        f"- paired metrics CSV: `{paired_metrics_csv}`",
        f"- parity report JSON: `{output_path.parent / 'parity_report.json'}`",
        f"- baseline report: `{baseline_report_path}`",
    ]
    if validation_errors:
        lines.extend(["", "## Validation Gate Errors", ""])
        lines.extend([f"- {item}" for item in validation_errors])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_shadow_parity(config: Mapping[str, Any]) -> dict[str, Any]:
    shared = _as_mapping(config, "shared")
    control = _as_mapping(config, "shadow")
    output_root = Path(str(control.get("output_root", "outputs/shadow_parity"))).expanduser().resolve()
    configured_run_id = str(control.get("run_id", "")).strip()
    run_id = configured_run_id or _now_stamp()
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    legacy_dir = run_dir / "legacy"
    framework_dir = run_dir / "framework"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    framework_dir.mkdir(parents=True, exist_ok=True)

    model_path = str(shared.get("model_path", "yolo26n.pt"))
    model_label = str(shared.get("model_label", model_label_from_path(model_path)))
    framework_model_name = str(shared.get("framework_model_name", "yolo"))
    source_dir = str(shared.get("source_dir", "coco/val2017_subset500/images"))
    validation_dataset = str(shared.get("validation_dataset", "configs/coco_subset500.yaml"))
    seed = int(shared.get("seed", 42))
    conf = float(shared.get("conf", DEFAULT_CONF))
    iou = float(shared.get("iou", DEFAULT_IOU))
    imgsz = int(shared.get("imgsz", DEFAULT_IMGSZ))
    max_images = int(shared.get("max_images", 8))
    attack_name = str(shared.get("attack_name", "none"))
    attack_params = dict(_as_mapping(shared, "attack_params"))
    defense_name = str(shared.get("defense_name", "none"))
    defense_params = dict(_as_mapping(shared, "defense_params"))
    validation_enabled = bool(shared.get("validation_enabled", True))
    run_name = str(shared.get("run_name", _build_run_name(shared)))
    model_prefix = f"{sanitize_segment(model_label, 'model')}_"
    if not run_name.startswith(model_prefix):
        run_name = f"{model_prefix}{run_name}"

    paired_source_dir, paired_dataset_yaml = _prepare_paired_source_and_dataset(
        source_dir=Path(source_dir).expanduser().resolve(),
        max_images=max_images,
        working_dir=run_dir,
        names_source_yaml=Path(validation_dataset).expanduser().resolve(),
    )

    log_event(component="shadow-parity", severity="INFO", message=f"run_id={run_id}")
    log_event(component="shadow-parity", severity="INFO", message=f"run_name={run_name}")
    log_event(
        component="shadow-parity",
        severity="INFO",
        message=f"model={model_label} attack={attack_name} defense={defense_name} seed={seed}",
    )

    legacy_config = {
        "model": {"path": model_path, "label": model_label},
        "data": {"data_yaml": str(paired_dataset_yaml), "image_dir": str(paired_source_dir)},
        "runner": {
            "confs": [conf],
            "iou": iou,
            "imgsz": imgsz,
            "seed": seed,
            "output_root": str(legacy_dir),
            "metrics_csv": "metrics_summary.csv",
            "run_validation": validation_enabled,
            "clean_existing_runs": True,
        },
        "experiments": [
            {
                "name": "shadow_pair",
                "attack": attack_name,
                "attack_label": attack_name,
                "attack_params": attack_params,
                "defense": defense_name,
                "defense_label": defense_name,
                "defense_params": defense_params,
                "run_name_template": run_name,
                "run_validation": validation_enabled,
            }
        ],
    }

    framework_config = {
        "model": {"name": framework_model_name, "params": {"model": model_path}},
        "data": {"source_dir": str(paired_source_dir)},
        "attack": {"name": attack_name, "params": attack_params},
        "defense": {"name": defense_name, "params": defense_params},
        "predict": {"conf": conf, "iou": iou, "imgsz": imgsz},
        "validation": {
            "enabled": validation_enabled,
            "dataset": str(paired_dataset_yaml) if validation_enabled else validation_dataset,
            # Keep framework validation call aligned with legacy val settings.
            "params": {
                "conf": conf,
                "iou": iou,
                "imgsz": imgsz,
                "seed": seed,
            },
        },
        "runner": {
            "seed": seed,
            "max_images": max_images,
            "output_root": str(framework_dir),
            "run_name": run_name,
        },
        "parity": {"enabled": False},
        "summary": {"enabled": False},
    }

    log_event(component="shadow-parity", severity="INFO", message="executing legacy paired run")
    legacy_runner = ExperimentRunner.from_dict(legacy_config)
    # Shadow parity intentionally executes the legacy runner as a comparison oracle.
    with temporary_legacy_runtime_override(True):
        legacy_runner.run()
    legacy_csv = legacy_dir / "metrics_summary.csv"
    legacy_row = read_last_legacy_row(legacy_csv)

    log_event(component="shadow-parity", severity="INFO", message="executing framework paired run")
    framework_runner = UnifiedExperimentRunner(config=framework_config)
    framework_summary = framework_runner.run()
    framework_run_dir = framework_dir / run_name
    framework_metrics = read_framework_metrics(framework_run_dir)
    prepared_validation = _recompute_framework_validation_on_prepared_images(
        framework_run_dir=framework_run_dir,
        model_path=model_path,
        conf=conf,
        iou=iou,
        imgsz=imgsz,
        seed=seed,
        labels_dir=paired_source_dir.parent / "labels",
        names_source_yaml=Path(validation_dataset).expanduser().resolve(),
    )
    framework_validation_payload = framework_metrics.get("validation", {})
    if not isinstance(framework_validation_payload, dict):
        framework_validation_payload = {}
    framework_validation_payload.update(prepared_validation)
    framework_validation_payload["status"] = "complete" if validation_enabled else "missing"
    framework_validation_payload["enabled"] = bool(validation_enabled)
    framework_validation_payload["dataset"] = str(framework_run_dir / "_parity_val_dataset" / "data.yaml")
    framework_metrics["validation"] = framework_validation_payload
    (framework_run_dir / "metrics.json").write_text(
        json.dumps(framework_metrics, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    legacy_artifact, framework_artifact = build_shadow_artifacts(
        legacy_row=legacy_row,
        framework_metrics=framework_metrics,
        framework_run_summary=framework_summary,
    )
    validation_required_attacks = {
        str(item).strip().lower()
        for item in control.get("require_validation_for_attacks", ["fgsm", "ifgsm", "pgd", "bim", "deepfool"])
    }
    validation_errors = enforce_validation_gate(
        attack_name=attack_name,
        legacy_row=legacy_row,
        framework_metrics=framework_metrics,
        gate_config=ValidationGateConfig(required_attacks=validation_required_attacks),
    )
    parity_report = compare_shadow_runs(
        legacy_artifact,
        framework_artifact,
        max_detection_relative_delta_pct=float(
            control.get("max_detection_relative_delta_pct", DEFAULT_MAX_DETECTION_DELTA_PCT)
        ),
        max_conf_relative_delta_pct=float(
            control.get("max_conf_relative_delta_pct", DEFAULT_MAX_CONFIDENCE_DELTA_PCT)
        ),
    )
    parity_report["validation_gate_errors"] = validation_errors
    parity_report["parity_pass"] = bool(parity_report.get("parity_pass", False)) and not validation_errors

    paired_csv = run_dir / "metrics_summary.csv"
    _write_paired_metrics_csv(
        output_path=paired_csv,
        pair_id=run_id,
        legacy_artifact=legacy_artifact,
        framework_artifact=framework_artifact,
    )
    parity_json = run_dir / "parity_report.json"
    parity_json.write_text(json.dumps(parity_report, indent=2, sort_keys=True), encoding="utf-8")

    baseline_report = run_dir / f"baseline_report_{_now_stamp()}.md"
    baseline = _run_stability_snapshot(output_md=baseline_report)
    parity_report["stability_baseline_all_pass"] = bool(baseline.get("all_pass", False))
    parity_json.write_text(json.dumps(parity_report, indent=2, sort_keys=True), encoding="utf-8")

    summary_md = run_dir / "shadow_summary.md"
    _render_summary_markdown(
        output_path=summary_md,
        parity_report=parity_report,
        validation_errors=validation_errors,
        paired_metrics_csv=paired_csv,
        baseline_report_path=baseline_report,
    )

    status_symbol = "✅" if bool(parity_report.get("parity_pass", False)) else "❌"
    delta_summary = parity_report.get("delta_summary", {})
    log_event(
        component="shadow-parity",
        severity="INFO",
        message=f"{status_symbol} {'PARITY PASS' if parity_report.get('parity_pass') else 'PARITY FAIL'}",
    )
    log_event(
        component="shadow-parity",
        severity="INFO",
        message=f"delta detection difference: {delta_summary.get('detection_worst_relative_pct')}",
    )
    log_event(
        component="shadow-parity",
        severity="INFO",
        message=f"delta confidence difference: {delta_summary.get('confidence_worst_relative_pct')}",
    )
    log_event(component="shadow-parity", severity="INFO", message=f"evidence pack: {run_dir}")
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "parity_pass": bool(parity_report.get("parity_pass", False)),
        "parity_score": parity_report.get("parity_score"),
        "parity_report": str(parity_json),
        "paired_metrics_csv": str(paired_csv),
        "summary_md": str(summary_md),
        "baseline_report": str(baseline_report),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run fully paired legacy/framework shadow parity and generate evidence pack."
    )
    parser.add_argument(
        "--config",
        default="configs/parity_test.yaml",
        help="Path to parity runner YAML config.",
    )
    args = parser.parse_args()

    try:
        config = _load_yaml_mapping(Path(args.config).expanduser().resolve())
        result = run_shadow_parity(config)
        print(json.dumps(result, indent=2, sort_keys=True))
        if not result["parity_pass"]:
            raise SystemExit(2)
    except (ValueError, FileNotFoundError, RuntimeError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
