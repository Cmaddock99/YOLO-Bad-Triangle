#!/usr/bin/env python3
"""One-command YOLO-Bad-Triangle adversarial robustness demo.

Runs preflight → sweep (baseline + attack + defense) → validate artifacts
→ check reports → generate auto-summary → detect no-op behaviour → write
manifest.  All outputs land under --output-root/<timestamp>/.

Usage (defaults):
    PYTHONPATH=src ./.venv/bin/python scripts/run_demo.py

Dry-run (prints plan, no subprocesses):
    PYTHONPATH=src ./.venv/bin/python scripts/run_demo.py --dry-run

Exit codes (priority: 2 > 3 > 4 > 1 > 0):
    0 — full success
    1 — partial sweep failure
    2 — preflight failure (no runs started)
    3 — artifact / schema / report validation failure
    4 — no-op attack or defense detected
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

# Exit code constants — kept as module-level names for tests.
EXIT_SUCCESS = 0
EXIT_PARTIAL_FAILURE = 1
EXIT_PREFLIGHT = 2
EXIT_ARTIFACT = 3
EXIT_NOOP = 4

_EXIT_PRIORITY = [EXIT_PREFLIGHT, EXIT_ARTIFACT, EXIT_NOOP, EXIT_PARTIAL_FAILURE, EXIT_SUCCESS]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _config_fingerprint(config_dict: dict) -> str:
    serialized = json.dumps(config_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _find_images(directory: Path) -> list[Path]:
    images: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        images.extend(directory.glob(ext))
    return images


def _git_info() -> tuple[str, bool]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
            ).decode().strip()
        )
        return commit, dirty
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unavailable", False


def _run_subprocess(cmd: list[str], log_path: Path, env: dict | None = None) -> int:
    """Run *cmd*, capturing stdout + stderr to *log_path*. Returns exit code."""
    with log_path.open("w", encoding="utf-8") as fh:
        result = subprocess.run(
            cmd, stdout=fh, stderr=subprocess.STDOUT, env=env or os.environ.copy()
        )
    return result.returncode


# ---------------------------------------------------------------------------
# Expected-run computation  (mirrors sweep_and_report.py naming conventions)
# ---------------------------------------------------------------------------

def build_expected_runs(attacks: list[str], defenses: list[str]) -> list[dict]:
    """Return the ordered list of run dicts the sweep will produce.

    Run names match sweep_and_report.py:
      baseline_none, attack_<a>, defended_<a>_<d>
    """
    runs: list[dict] = [{"run_name": "baseline_none", "attack": "none", "defense": "none"}]
    for attack in attacks:
        runs.append({"run_name": f"attack_{attack}", "attack": attack, "defense": "none"})
    for attack in attacks:
        for defense in defenses:
            runs.append({
                "run_name": f"defended_{attack}_{defense}",
                "attack": attack,
                "defense": defense,
            })
    return runs


# ---------------------------------------------------------------------------
# Stage 1 — Preflight
# ---------------------------------------------------------------------------

def stage_preflight(
    args: argparse.Namespace,
    attacks: list[str],
    defenses: list[str],
    output_root: Path,
) -> tuple[int, dict, Path, Path]:
    """Validate environment and config before launching any subprocess.

    Returns (exit_code, config_dict, config_path, source_dir).
    exit_code == 0 means all checks passed.
    """

    def _fail(msg: str) -> tuple[int, dict, Path, Path]:
        print(f"[PREFLIGHT] FAIL {msg}", file=sys.stderr)
        return EXIT_PREFLIGHT, {}, Path("."), Path(".")

    # 1. Environment check via check_environment.py
    env_result = subprocess.run(
        [args.python_bin, str(REPO_ROOT / "scripts" / "check_environment.py")],
        capture_output=True,
        text=True,
    )
    if env_result.returncode != 0:
        print("[PREFLIGHT] FAIL environment check failed:", file=sys.stderr)
        if env_result.stdout:
            print(env_result.stdout.rstrip(), file=sys.stderr)
        if env_result.stderr:
            print(env_result.stderr.rstrip(), file=sys.stderr)
        return EXIT_PREFLIGHT, {}, Path("."), Path(".")

    # 2+3. Config readable and valid YAML
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.is_file():
        return _fail(f"config not found: {config_path}")

    try:
        import yaml  # noqa: PLC0415
        with config_path.open() as fh:
            config_dict = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        return _fail(f"config parse error: {exc}")

    if not isinstance(config_dict, dict):
        return _fail("config YAML is not a mapping")

    # 4. Dataset directory + images
    source_dir_raw = (config_dict.get("data") or {}).get("source_dir", "")
    if not source_dir_raw:
        return _fail("config missing data.source_dir")
    source_dir = (REPO_ROOT / source_dir_raw).resolve()
    if not source_dir.is_dir():
        return _fail(f"data.source_dir not found: {source_dir}")
    image_files = _find_images(source_dir)
    if not image_files:
        return _fail(f"no images (*.jpg/jpeg/png) in: {source_dir}")

    # 6. Validation dataset
    val_dataset_raw = (config_dict.get("validation") or {}).get("dataset", "")
    if val_dataset_raw:
        val_dataset = (REPO_ROOT / val_dataset_raw).resolve()
        if not val_dataset.is_file():
            return _fail(f"validation.dataset not found: {val_dataset_raw}")

    # 7. DPC-UNet checkpoint for c_dog defenses
    if any(d in ("c_dog", "c_dog_ensemble") for d in defenses):
        if not os.environ.get("DPC_UNET_CHECKPOINT_PATH"):
            return _fail("DPC_UNET_CHECKPOINT_PATH required for c_dog/c_dog_ensemble defense")

    # 8. Disk space (≥ 500 MB)
    check_dir = output_root if output_root.exists() else output_root.parent
    if check_dir.exists():
        free_bytes = shutil.disk_usage(str(check_dir)).free
        if free_bytes < 500 * 1024 * 1024:
            return _fail(f"insufficient free disk space (<500 MB) at {check_dir}")

    # Expected run set non-empty
    expected_runs = build_expected_runs(attacks, defenses)
    if not expected_runs:
        return _fail("expected run set is empty (check --attacks / --defenses)")

    print(
        f"[PREFLIGHT] OK — images={len(image_files)}, "
        f"expected_runs={len(expected_runs)}, "
        f"config={config_path.name}"
    )
    return EXIT_SUCCESS, config_dict, config_path, source_dir


# ---------------------------------------------------------------------------
# Stage 4 — Per-run artifact validation
# ---------------------------------------------------------------------------

def stage_validate_runs(
    expected_runs: list[dict],
    runs_root: Path,
) -> tuple[int, dict[str, list[str]]]:
    """Check every expected run for required artifacts and valid JSON schemas.

    Returns (exit_code, validation_errors).
    validation_errors maps run_name → list of error strings (empty = passed).
    """
    from lab.health_checks.artifacts import assert_required_artifacts
    from lab.health_checks.schema import validate_framework_json_file, schema_root_for_repo

    schema_root = schema_root_for_repo(REPO_ROOT)
    metrics_schema = schema_root / "framework_metrics.schema.json"
    summary_schema = schema_root / "framework_run_summary.schema.json"

    # Diff expected vs. filesystem
    present_dirs: set[str] = set()
    if runs_root.exists():
        present_dirs = {p.name for p in runs_root.iterdir() if p.is_dir()}
    expected_names = {r["run_name"] for r in expected_runs}
    unexpected = present_dirs - expected_names
    if unexpected:
        print(f"[VALIDATE] WARNING unexpected dirs (not checked): {sorted(unexpected)}", file=sys.stderr)

    validation_errors: dict[str, list[str]] = {}
    for run_meta in expected_runs:
        run_name = run_meta["run_name"]
        errors: list[str] = []
        run_dir = runs_root / run_name

        if not run_dir.is_dir():
            errors.append(f"run directory missing: {run_dir}")
            validation_errors[run_name] = errors
            continue

        # Artifact presence
        try:
            assert_required_artifacts(output_root=run_dir, contract_name="demo_gate")
        except FileNotFoundError as exc:
            errors.append(str(exc))

        # JSON schema checks (run independently so we collect all errors)
        metrics_path = run_dir / "metrics.json"
        run_summary_path = run_dir / "run_summary.json"
        if metrics_path.is_file():
            try:
                validate_framework_json_file(path=metrics_path, schema_file=metrics_schema)
            except ValueError as exc:
                errors.append(f"metrics.json schema error: {exc}")

        if run_summary_path.is_file():
            try:
                validate_framework_json_file(path=run_summary_path, schema_file=summary_schema)
            except ValueError as exc:
                errors.append(f"run_summary.json schema error: {exc}")

        validation_errors[run_name] = errors

    passed = sum(1 for errs in validation_errors.values() if not errs)
    total = len(expected_runs)
    print(f"[VALIDATE] {passed}/{total} runs passed", file=sys.stderr)

    return (EXIT_SUCCESS if passed == total else EXIT_ARTIFACT), validation_errors


# ---------------------------------------------------------------------------
# Stage 5 — Framework report existence check
# ---------------------------------------------------------------------------

def stage_check_reports(reports_root: Path) -> int:
    """Assert three report files exist and are non-empty. Returns exit code."""
    required = [
        "framework_run_summary.csv",
        "framework_run_report.md",
        "team_summary.json",
    ]
    all_ok = True
    for fname in required:
        fpath = reports_root / fname
        if not fpath.is_file() or fpath.stat().st_size == 0:
            print(f"[REPORTS] FAIL missing or empty: {fname}", file=sys.stderr)
            all_ok = False
        else:
            print(f"[REPORTS] OK {fname}", file=sys.stderr)
    return EXIT_SUCCESS if all_ok else EXIT_ARTIFACT


# ---------------------------------------------------------------------------
# Stage 7 — No-op attack / defense detection
# ---------------------------------------------------------------------------

def stage_noop_check(
    expected_runs: list[dict],
    runs_root: Path,
) -> tuple[int, list[dict]]:
    """Detect attacks or defenses that produce no measurable perturbation.

    Returns (exit_code, noop_warnings).
    """
    noop_warnings: list[dict] = []

    def _image_hashes(run_dir: Path, max_files: int = 200) -> dict[str, str]:
        images_dir = run_dir / "images"
        if not images_dir.is_dir():
            return {}
        files = sorted(f for f in images_dir.iterdir() if f.is_file())[:max_files]
        return {f.name: _sha256_file(f) for f in files}

    def _total_detections(run_dir: Path) -> int | None:
        data = _load_json(run_dir / "metrics.json")
        if data is None:
            return None
        return (data.get("predictions") or {}).get("total_detections")

    def _all_identical(a: dict[str, str], b: dict[str, str]) -> bool:
        common = set(a) & set(b)
        return bool(common) and all(a[k] == b[k] for k in common)

    baseline_dir = runs_root / "baseline_none"
    baseline_hashes = _image_hashes(baseline_dir)
    baseline_det = _total_detections(baseline_dir)

    # Attack no-op check
    for run_meta in expected_runs:
        if run_meta["attack"] == "none" or run_meta["defense"] != "none":
            continue
        run_name = run_meta["run_name"]
        run_dir = runs_root / run_name
        attacked_hashes = _image_hashes(run_dir)

        if baseline_hashes and attacked_hashes:
            check_type = "sampled" if len(attacked_hashes) < len(list((run_dir / "images").iterdir())) else "byte_identity"
            if _all_identical(baseline_hashes, attacked_hashes):
                noop_warnings.append({
                    "run_name": run_name,
                    "check_type": check_type,
                    "detail": "All sampled images byte-identical to baseline — attack appears no-op",
                })
        else:
            # Fallback: metrics-only check
            attacked_det = _total_detections(run_dir)
            if baseline_det is not None and attacked_det is not None:
                change = abs(baseline_det - attacked_det) / max(baseline_det, 1)
                if change < 0.01:
                    noop_warnings.append({
                        "run_name": run_name,
                        "check_type": "metrics_only",
                        "detail": (
                            f"total_detections change <1%: "
                            f"baseline={baseline_det}, attacked={attacked_det}"
                        ),
                    })

        # Metrics divergence (always run if images check didn't fire)
        if not any(w["run_name"] == run_name for w in noop_warnings):
            attacked_det = _total_detections(run_dir)
            if baseline_det is not None and attacked_det is not None:
                change = abs(baseline_det - attacked_det) / max(baseline_det, 1)
                if change < 0.01:
                    noop_warnings.append({
                        "run_name": run_name,
                        "check_type": "metrics_divergence",
                        "detail": (
                            f"total_detections change <1%: "
                            f"baseline={baseline_det}, attacked={attacked_det}"
                        ),
                    })

    # Defense no-op check
    for run_meta in expected_runs:
        if run_meta["defense"] == "none":
            continue
        run_name = run_meta["run_name"]
        attack = run_meta["attack"]
        attack_run_dir = runs_root / f"attack_{attack}"
        defense_run_dir = runs_root / run_name

        attack_hashes = _image_hashes(attack_run_dir)
        defense_hashes = _image_hashes(defense_run_dir)

        if attack_hashes and defense_hashes:
            if _all_identical(attack_hashes, defense_hashes):
                noop_warnings.append({
                    "run_name": run_name,
                    "check_type": "byte_identity",
                    "detail": "All images byte-identical to attack-only run — defense appears no-op",
                })
        else:
            attacked_det = _total_detections(attack_run_dir)
            defended_det = _total_detections(defense_run_dir)
            if attacked_det is not None and defended_det is not None:
                change = abs(attacked_det - defended_det) / max(attacked_det, 1)
                if change < 0.01:
                    noop_warnings.append({
                        "run_name": run_name,
                        "check_type": "metrics_only",
                        "detail": (
                            f"total_detections change <1%: "
                            f"attacked={attacked_det}, defended={defended_det}"
                        ),
                    })

        if not any(w["run_name"] == run_name for w in noop_warnings):
            attacked_det = _total_detections(attack_run_dir)
            defended_det = _total_detections(defense_run_dir)
            if attacked_det is not None and defended_det is not None:
                change = abs(attacked_det - defended_det) / max(attacked_det, 1)
                if change < 0.01:
                    noop_warnings.append({
                        "run_name": run_name,
                        "check_type": "metrics_divergence",
                        "detail": (
                            f"total_detections change <1%: "
                            f"attacked={attacked_det}, defended={defended_det}"
                        ),
                    })

    for w in noop_warnings:
        print(f"[NOOP] {w['run_name']}: {w['check_type']} — {w['detail']}", file=sys.stderr)

    return (EXIT_NOOP if noop_warnings else EXIT_SUCCESS), noop_warnings


# ---------------------------------------------------------------------------
# Stage 8 — Manifest generation
# ---------------------------------------------------------------------------

def write_manifest(
    *,
    demo_root: Path,
    git_commit: str,
    git_dirty: bool,
    args: argparse.Namespace,
    config_path: Path,
    fingerprint: str,
    model_name: str,
    dataset_name: str,
    dataset_path: str,
    images_count: int,
    conf: float,
    iou: float,
    imgsz: int,
    expected_runs: list[dict],
    validation_errors: dict[str, list[str]],
    noop_warnings: list[dict],
    failed_runs: list[str],
    start_time_str: str,
    t0_wall: float,
    exit_code: int,
    exit_reason: str,
) -> None:
    end_time_str = _now_iso()
    duration = time.monotonic() - t0_wall
    runs_root = demo_root / "runs"

    # Build per-run manifest entries
    runs_list: list[dict] = []
    for run_meta in expected_runs:
        run_name = run_meta["run_name"]
        run_dir = runs_root / run_name
        epsilon = None
        norm_type = None
        attack_params: dict = {}
        defense_params: dict = {}
        summary_data = _load_json(run_dir / "run_summary.json")
        if summary_data:
            attack_block = summary_data.get("attack") or {}
            attack_params = dict(attack_block.get("params") or {})
            epsilon = attack_params.get("epsilon")
            norm_type = attack_params.get("norm") or attack_params.get("norm_type")
            defense_block = summary_data.get("defense") or {}
            defense_params = dict(defense_block.get("params") or {})
        run_noops = [w for w in noop_warnings if w.get("run_name") == run_name]
        runs_list.append({
            "run_name": run_name,
            "attack_name": run_meta["attack"],
            "attack_params": attack_params,
            "epsilon": epsilon,
            "norm_type": norm_type,
            "defense_name": run_meta["defense"],
            "defense_params": defense_params,
            "run_dir": str(run_dir.resolve()),
            "validation_passed": not bool(validation_errors.get(run_name)),
            "noop_warnings": run_noops,
        })

    # Compute checksums for all expected artifacts
    checksums: dict[str, str] = {}
    candidate_paths: list[Path] = []
    for run_meta in expected_runs:
        run_dir = runs_root / run_meta["run_name"]
        for fname in ("metrics.json", "run_summary.json", "predictions.jsonl", "resolved_config.yaml"):
            candidate_paths.append(run_dir / fname)
    reports_root = demo_root / "reports"
    for fname in ("framework_run_summary.csv", "framework_run_report.md", "team_summary.json"):
        candidate_paths.append(reports_root / fname)
    summary_root = demo_root / "summary"
    for fname in ("summary.json", "summary.md", "headline_metrics.csv", "per_class_vulnerability.csv", "warnings.json"):
        candidate_paths.append(summary_root / fname)

    for fpath in candidate_paths:
        if fpath.is_file():
            rel = fpath.relative_to(demo_root)
            checksums[str(rel)] = _sha256_file(fpath)

    try:
        import torch  # noqa: PLC0415
        torch_version = torch.__version__
    except ImportError:
        torch_version = "unavailable"

    source_files = [
        "scripts/run_demo.py",
        "scripts/sweep_and_report.py",
        "scripts/generate_framework_report.py",
        "scripts/generate_team_summary.py",
        "scripts/generate_auto_summary.py",
        "src/lab/runners/run_experiment.py",
    ]

    manifest: dict[str, Any] = {
        "schema_version": "demo_manifest/v1",
        "reproducibility": {
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "seed": args.seed,
            "torch_version": torch_version,
            "python_version": sys.version,
            "platform": platform.platform(),
        },
        "config": {
            "config_file": str(config_path),
            "config_fingerprint": fingerprint,
            "model_name": model_name,
            "dataset_name": dataset_name,
            "dataset_path": dataset_path,
            "images_count": images_count,
            "seed": args.seed,
            "conf": conf,
            "iou": iou,
            "imgsz": imgsz,
        },
        "source_files": source_files,
        "runs": runs_list,
        "artifacts": {"checksums": checksums},
        "timing": {
            "start_time": start_time_str,
            "end_time": end_time_str,
            "duration_seconds": round(duration, 2),
        },
        "outcome": {
            "exit_code": exit_code,
            "exit_reason": exit_reason,
            "failed_runs": failed_runs,
            "noop_warnings": noop_warnings,
            "validation_errors": validation_errors,
        },
        "bootstrap": {
            "n": 500,
            "seed": args.seed,
            "note": "Reduced from default 2000 for demo speed",
        },
    }

    manifest_path = demo_root / "demo_manifest.json"
    try:
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Demo manifest: {manifest_path}")
    except OSError as exc:
        print(f"[ERROR] Cannot write manifest: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="One-command YOLO-Bad-Triangle adversarial robustness demo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--config", default="configs/demo.yaml", help="Base YAML config (default: configs/demo.yaml).")
    p.add_argument("--attacks", default="fgsm", help="Comma-separated attack names (default: fgsm).")
    p.add_argument("--defenses", default="median_preprocess", help="Comma-separated defense names (default: median_preprocess).")
    p.add_argument("--seed", type=int, default=42, help="RNG seed (default: 42).")
    p.add_argument("--output-root", default="outputs/demo", help="Parent directory for demo outputs (default: outputs/demo).")
    p.add_argument("--python-bin", default="./.venv/bin/python", help="Python interpreter (default: ./.venv/bin/python).")
    p.add_argument("--max-images", type=int, default=None, help="Override runner.max_images.")
    p.add_argument("--dry-run", action="store_true", help="Print plan and exit 0 (no subprocesses).")
    p.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Bypass Stage 1 preflight checks (dev only; unsafe for production).",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:  # noqa: C901 (acceptable complexity for a pipeline orchestrator)
    args = _parse_args()
    attacks = [a.strip() for a in args.attacks.split(",") if a.strip()]
    defenses = [d.strip() for d in args.defenses.split(",") if d.strip()]

    # Stage 0 — Initialisation
    start_time_str = _now_iso()
    t0_wall = time.monotonic()
    demo_timestamp = _timestamp()
    output_root = Path(args.output_root).expanduser().resolve()
    demo_root = output_root / demo_timestamp
    runs_root = demo_root / "runs"
    reports_root = demo_root / "reports"
    summary_root = demo_root / "summary"

    git_commit, git_dirty = _git_info()

    try:
        for subdir in (runs_root, reports_root, summary_root):
            subdir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[ERROR] Cannot create demo directories: {exc}", file=sys.stderr)
        return EXIT_ARTIFACT

    # Accumulate exit codes — highest priority wins at the end
    staged_exits: list[int] = []
    exit_reason = "success"
    failed_runs: list[str] = []
    noop_warnings: list[dict] = []
    validation_errors: dict[str, list[str]] = {}

    # Stage 1 — Preflight (or bypass)
    if args.skip_preflight:
        print("[PREFLIGHT] BYPASSED — skip-preflight set; unsafe for production use", file=sys.stderr)
        config_path = Path(args.config).expanduser().resolve()
        try:
            import yaml  # noqa: PLC0415
            with config_path.open() as fh:
                config_dict = yaml.safe_load(fh) or {}
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Cannot load config even with --skip-preflight: {exc}", file=sys.stderr)
            return EXIT_PREFLIGHT
        source_dir_raw = (config_dict.get("data") or {}).get("source_dir", "")
        source_dir = (REPO_ROOT / source_dir_raw).resolve() if source_dir_raw else REPO_ROOT
    else:
        pf_code, config_dict, config_path, source_dir = stage_preflight(
            args, attacks, defenses, output_root
        )
        if pf_code != EXIT_SUCCESS:
            exit_reason = "preflight_failure"
            write_manifest(
                demo_root=demo_root, git_commit=git_commit, git_dirty=git_dirty, args=args,
                config_path=Path(args.config), fingerprint="", model_name="unknown",
                dataset_name="unknown", dataset_path="unknown", images_count=0,
                conf=0.0, iou=0.0, imgsz=0, expected_runs=[], validation_errors={},
                noop_warnings=[], failed_runs=[], start_time_str=start_time_str,
                t0_wall=t0_wall, exit_code=EXIT_PREFLIGHT, exit_reason=exit_reason,
            )
            return EXIT_PREFLIGHT

    # Stage 2 — Config fingerprint + expected run set
    fingerprint = _config_fingerprint(config_dict)
    model_raw = ((config_dict.get("model") or {}).get("params") or {}).get("model", "unknown")
    model_name = model_raw.removesuffix(".pt").lower()
    # Use the parent directory name when the last path component is a generic "images" leaf.
    # e.g. coco/val2017_subset500/images → "val2017_subset500", not "images".
    if source_dir.is_dir():
        dataset_name = source_dir.parent.name if source_dir.name == "images" else source_dir.name
    else:
        dataset_name = "unknown"
    dataset_path_str = str(source_dir)
    predict_cfg = config_dict.get("predict") or {}
    conf = float(predict_cfg.get("conf", 0.25))
    iou = float(predict_cfg.get("iou", 0.45))
    imgsz = int(predict_cfg.get("imgsz", 640))
    if args.max_images is not None:
        images_count = args.max_images
    else:
        images_count = int((config_dict.get("runner") or {}).get("max_images") or 0) or len(_find_images(source_dir))
    expected_runs = build_expected_runs(attacks, defenses)

    # Dry-run: print plan and exit
    if args.dry_run:
        print("[DRY RUN] Resolved demo plan:")
        print(f"  config:        {config_path}")
        print(f"  demo_root:     {demo_root}")
        print(f"  attacks:       {attacks}")
        print(f"  defenses:      {defenses}")
        print(f"  seed:          {args.seed}")
        print(f"  max_images:    {images_count}")
        print(f"  fingerprint:   {fingerprint}")
        print(f"  expected_runs: {len(expected_runs)}")
        for r in expected_runs:
            print(f"    {r['run_name']}  (attack={r['attack']}, defense={r['defense']})")
        return EXIT_SUCCESS

    # Coverage warnings
    if len(attacks) < 2:
        print(
            f"[WARNING] Only {len(attacks)} attack(s) specified — "
            "evaluation coverage may be too narrow for meaningful conclusions.",
            file=sys.stderr,
        )
    if not defenses:
        print("[WARNING] No defenses — defense recovery cannot be evaluated.", file=sys.stderr)

    # Subprocess environment: ensure PYTHONPATH=src
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")

    # Stage 3 — Sweep execution (phases 1-3: baseline + attacks + defenses).
    # Phase 4 (reports) is NOT delegated to the sweep because sweep_and_report.py Phase 4
    # also invokes generate_dashboard.py with a reports-root layout that is incompatible
    # with the demo's isolated output directory.  We invoke the report scripts directly
    # in Stage 3b so the demo controls exactly what gets called.
    sweep_log = demo_root / "sweep.log"
    sweep_cmd = [
        args.python_bin,
        str(REPO_ROOT / "scripts" / "sweep_and_report.py"),
        "--config", str(config_path),
        "--attacks", args.attacks,
        "--defenses", args.defenses,
        "--seed", str(args.seed),
        "--workers", "1",
        "--phases", "1,2,3",
        "--validation-enabled",
        "--runs-root", str(runs_root),
        "--no-team-summary",
    ]
    if args.max_images is not None:
        sweep_cmd.extend(["--max-images", str(args.max_images)])

    print(f"[SWEEP] Starting → log: {sweep_log}")
    print(
        "[SWEEP] NOTE: demo uses a split report path (phases 1-3 here, report scripts in Stage 3b). "
        "Treat demo outputs as non-comparable with full sweep-and-report phase-4 bundles unless aligned.",
        file=sys.stderr,
    )
    sweep_rc = _run_subprocess(sweep_cmd, sweep_log, env=env)
    if sweep_rc != 0:
        print(f"[SWEEP] FAILED (exit {sweep_rc}); see {sweep_log}", file=sys.stderr)
        staged_exits.append(EXIT_PARTIAL_FAILURE)
        exit_reason = "partial_run_failure"
    else:
        print("[SWEEP] Done")

    # Stage 3b — Framework report + team summary (Phase 4 equivalent, dashboard excluded).
    reports_log = demo_root / "reports.log"
    framework_report_cmd = [
        args.python_bin,
        str(REPO_ROOT / "scripts" / "generate_framework_report.py"),
        "--runs-root", str(runs_root),
        "--output-dir", str(reports_root),
    ]
    team_summary_cmd = [
        args.python_bin,
        str(REPO_ROOT / "scripts" / "generate_team_summary.py"),
        "--report-root", str(reports_root),
    ]
    print(f"[REPORTS] Generating → log: {reports_log}")
    report_gen_rc = _run_subprocess(framework_report_cmd, reports_log, env=env)
    if report_gen_rc != 0:
        print(f"[REPORTS] framework report FAILED (exit {report_gen_rc}); see {reports_log}", file=sys.stderr)
        staged_exits.append(EXIT_ARTIFACT)
        if exit_reason == "success":
            exit_reason = "artifact_validation_failure"
    else:
        # Append team summary to the same log
        with reports_log.open("a", encoding="utf-8") as fh:
            ts_result = subprocess.run(
                team_summary_cmd, stdout=fh, stderr=subprocess.STDOUT,
                env=env or os.environ.copy()
            )
        if ts_result.returncode != 0:
            print(f"[REPORTS] team summary FAILED (exit {ts_result.returncode}); see {reports_log}", file=sys.stderr)
            staged_exits.append(EXIT_ARTIFACT)
            if exit_reason == "success":
                exit_reason = "artifact_validation_failure"
        else:
            print("[REPORTS] Done")

    # Stage 4 — Per-run artifact validation
    val_code, validation_errors = stage_validate_runs(expected_runs, runs_root)
    if val_code != EXIT_SUCCESS:
        staged_exits.append(EXIT_ARTIFACT)
        if exit_reason == "success":
            exit_reason = "artifact_validation_failure"
        failed_runs = [rn for rn, errs in validation_errors.items() if errs]

    # Stage 5 — Framework report existence check
    report_code = stage_check_reports(reports_root)
    if report_code != EXIT_SUCCESS:
        staged_exits.append(EXIT_ARTIFACT)
        if exit_reason == "success":
            exit_reason = "artifact_validation_failure"

    # Stage 6 — Auto-summary generation
    auto_summary_log = demo_root / "auto_summary.log"
    summary_cmd = [
        args.python_bin,
        str(REPO_ROOT / "scripts" / "generate_auto_summary.py"),
        "--runs-root", str(runs_root),
        "--output-dir", str(summary_root),
        "--bootstrap-seed", str(args.seed),
        "--bootstrap-n", "500",
    ]
    print(f"[SUMMARY] Generating → log: {auto_summary_log}")
    summary_rc = _run_subprocess(summary_cmd, auto_summary_log, env=env)
    if summary_rc != 0:
        print(f"[SUMMARY] FAILED (exit {summary_rc}); see {auto_summary_log}", file=sys.stderr)
        staged_exits.append(EXIT_ARTIFACT)
        if exit_reason == "success":
            exit_reason = "artifact_validation_failure"
    else:
        summary_files_expected = [
            "summary.json", "summary.md", "headline_metrics.csv",
            "per_class_vulnerability.csv", "warnings.json",
        ]
        missing_summary = [f for f in summary_files_expected if not (summary_root / f).is_file()]
        if missing_summary:
            print(f"[SUMMARY] FAIL missing output files: {missing_summary}", file=sys.stderr)
            staged_exits.append(EXIT_ARTIFACT)
            if exit_reason == "success":
                exit_reason = "artifact_validation_failure"
        else:
            print("[SUMMARY] Done")

    # Stage 7 — No-op attack/defense detection (only when runs succeeded)
    if sweep_rc == 0 and val_code == EXIT_SUCCESS:
        noop_code, noop_warnings = stage_noop_check(expected_runs, runs_root)
        if noop_code != EXIT_SUCCESS:
            staged_exits.append(EXIT_NOOP)
            if exit_reason == "success":
                exit_reason = "noop_detected"

    # Stage 8 — Manifest + final exit
    final_exit = EXIT_SUCCESS
    for priority in _EXIT_PRIORITY:
        if priority in staged_exits:
            final_exit = priority
            break

    write_manifest(
        demo_root=demo_root, git_commit=git_commit, git_dirty=git_dirty, args=args,
        config_path=config_path, fingerprint=fingerprint,
        model_name=model_name, dataset_name=dataset_name, dataset_path=dataset_path_str,
        images_count=images_count, conf=conf, iou=iou, imgsz=imgsz,
        expected_runs=expected_runs, validation_errors=validation_errors,
        noop_warnings=noop_warnings, failed_runs=failed_runs,
        start_time_str=start_time_str, t0_wall=t0_wall,
        exit_code=final_exit, exit_reason=exit_reason,
    )

    elapsed = time.monotonic() - t0_wall
    print()
    print("=" * 60)
    if final_exit == EXIT_SUCCESS:
        print(f"Demo complete. All stages passed. ({_fmt_elapsed(elapsed)})")
    else:
        print(f"Demo finished with issues — exit {final_exit}: {exit_reason} ({_fmt_elapsed(elapsed)})")
    print(f"Output root:   {demo_root}")

    return final_exit


if __name__ == "__main__":
    sys.exit(main())
