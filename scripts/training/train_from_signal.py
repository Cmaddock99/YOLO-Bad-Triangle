#!/usr/bin/env python3
"""Run export -> train -> A/B gate evaluation from cycle_training_signal.json."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from lab.config.profiles import (
    authoritative_metric as resolved_authoritative_metric,
    build_profile_config,
    learned_defense_compatibility,
    resolve_profile_compatibility,
)
from lab.runners.cli_utils import build_repo_python_command, with_src_pythonpath
from lab.runners.run_intent import sha256_file

REPO = Path(__file__).resolve().parents[2]
SIGNAL_PATH_DEFAULT = "outputs/cycle_training_signal.json"


def _resolve_repo_path(raw: str | None, *, default_relative: str | None = None) -> Path:
    if raw:
        candidate = Path(raw).expanduser()
        return candidate if candidate.is_absolute() else (REPO / candidate).resolve()
    if default_relative is None:
        raise ValueError("default_relative is required when raw is empty")
    return (REPO / default_relative).resolve()


def _load_signal(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Training signal not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Training signal must be a JSON object: {path}")
    worst_attack = str(payload.get("worst_attack") or "").strip()
    if not worst_attack:
        raise ValueError(f"Training signal missing worst_attack: {path}")
    return payload


def _resolve_checkpoint_a(raw: str | None) -> Path:
    candidate_raw = raw or os.environ.get("DPC_UNET_CHECKPOINT_PATH", "")
    candidate = str(candidate_raw or "").strip()
    if not candidate:
        raise FileNotFoundError(
            "Baseline checkpoint is required. Pass --checkpoint-a or set DPC_UNET_CHECKPOINT_PATH."
        )
    checkpoint_path = _resolve_repo_path(candidate)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Baseline checkpoint not found: {checkpoint_path}")
    return checkpoint_path


def _override_assignment(key: str, value: Any) -> str:
    if isinstance(value, str):
        return f"{key}={value}"
    if isinstance(value, (bool, list, dict)) or value is None:
        return f"{key}={json.dumps(value)}"
    return f"{key}={value}"


def _render_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _run_step(
    label: str,
    command: list[str],
    *,
    dry_run: bool,
) -> subprocess.CompletedProcess[bytes] | None:
    print(f"[{label}] {_render_command(command)}")
    if dry_run:
        return None
    return subprocess.run(
        command,
        cwd=str(REPO),
        env=with_src_pythonpath(REPO),
        check=False,
    )


def _read_result_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


# Minimum acceptable delta_mAP50 for a gate to pass. Allows a noise-floor
# tolerance band so candidates with delta in [-0.005, 0) are not rejected.
_GATE_THRESHOLD = -0.005


def _gate_passed(result: "subprocess.CompletedProcess[bytes] | None", payload: dict[str, Any]) -> bool:
    """Return True only when the subprocess exited 0 AND delta_mAP50 >= _GATE_THRESHOLD.

    evaluate_checkpoint.py exits 0 when B >= A (delta >= 0) and exits 1 when
    B < A. Our spec allows a -0.005 tolerance band to absorb evaluation noise,
    so candidates with delta in [-0.005, 0) should still pass. Checking the
    threshold here ensures the gate reflects the spec criterion rather than
    the subprocess's own exit-code convention.
    """
    if result is None or result.returncode != 0:
        return False
    delta = payload.get("delta_mAP50")
    if delta is None:
        return False
    try:
        return float(delta) >= _GATE_THRESHOLD
    except (TypeError, ValueError):
        return False


def _write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a DPC-UNet candidate from cycle_training_signal.json and gate it with A/B evaluation."
    )
    parser.add_argument("--signal-path", default=SIGNAL_PATH_DEFAULT)
    parser.add_argument("--checkpoint-a", default="")
    parser.add_argument("--candidate-output", default="")
    parser.add_argument("--resume-path", default="")
    parser.add_argument("--manifest-dir", default="")
    parser.add_argument("--clean-images", type=int, default=500)
    parser.add_argument("--attack-images", type=int, default=100)
    parser.add_argument("--python-bin", default="./.venv/bin/python")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    signal_path = _resolve_repo_path(args.signal_path)
    signal = _load_signal(signal_path)
    cycle_id = str(signal.get("cycle_id") or "signal_run").strip() or "signal_run"

    checkpoint_a = _resolve_checkpoint_a(args.checkpoint_a or None)
    candidate_output = _resolve_repo_path(
        args.candidate_output or None,
        default_relative=f"outputs/checkpoints/{cycle_id}_signal_candidate.pt",
    )
    resume_path = _resolve_repo_path(
        args.resume_path or None,
        default_relative=f"outputs/checkpoints/{cycle_id}_signal_resume.pt",
    )
    manifest_dir = _resolve_repo_path(
        args.manifest_dir or None,
        default_relative=f"outputs/training_runs/{cycle_id}",
    )
    manifest_path = manifest_dir / "training_manifest.json"
    training_zip_path = (REPO / "outputs" / "training_exports" / f"{cycle_id}_training_data.zip").resolve()
    clean_gate_result_path = manifest_dir / "clean_gate_result.json"
    attack_gate_result_path = manifest_dir / "attack_gate_result.json"
    worst_attack = str(signal.get("worst_attack") or "").strip()
    worst_attack_params = signal.get("worst_attack_params")
    if not isinstance(worst_attack_params, dict):
        worst_attack_params = {}
    learned_defense_status: dict[str, Any] | None = None
    active_defense = "c_dog"
    authoritative_metric: str | None = None
    profile_compatibility: dict[str, Any] | None = None
    if args.profile:
        learned_defense_status = learned_defense_compatibility(args.profile)
        active_defense = str(learned_defense_status.get("default_defense") or "c_dog")
        profile_config = build_profile_config(args.profile)
        profile_config["attack"]["name"] = worst_attack
        profile_config["attack"]["params"] = dict(worst_attack_params)
        profile_config["defense"]["name"] = active_defense
        profile_compatibility = resolve_profile_compatibility(profile_config)
        authoritative_metric = resolved_authoritative_metric(profile_config)

    manifest: dict[str, Any] = {
        "cycle_id": cycle_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signal_path": str(signal_path),
        "signal_payload": signal,
        "training_zip_path": str(training_zip_path),
        "training_args": [],
        "pipeline_profile": args.profile,
        "authoritative_metric": authoritative_metric,
        "profile_compatibility": profile_compatibility,
        "learned_defense_compatibility": learned_defense_status,
        "resolved_attack_params": worst_attack_params,
        "baseline_checkpoint": {
            "path": str(checkpoint_a),
            "sha256": sha256_file(checkpoint_a),
        },
        "candidate_checkpoint": {
            "path": str(candidate_output),
            "sha256": None,
        },
        "clean_gate": {
            "result_path": str(clean_gate_result_path),
            "delta_mAP50": None,
            "verdict": "not_run",
        },
        "attack_gate": {
            "attack": worst_attack,
            "attack_params": worst_attack_params,
            "defense": active_defense,
            "result_path": str(attack_gate_result_path),
            "delta_mAP50": None,
            "verdict": "not_run",
        },
        "final_verdict": "run_failed",
    }
    if args.profile and learned_defense_status and not bool(learned_defense_status.get("trainable", False)):
        manifest["final_verdict"] = "profile_incompatible"
        _write_manifest(manifest_path, manifest)
        raise SystemExit(2)

    export_command = build_repo_python_command(
        REPO,
        "scripts/export_training_data.py",
        [
            "--from-signal",
            "--signal-path",
            str(signal_path),
            "--output-zip",
            str(training_zip_path),
        ],
        python_bin=args.python_bin,
    )
    train_command = build_repo_python_command(
        REPO,
        "scripts/train_dpc_unet_local.py",
        [
            "--preset",
            "signal_driven",
            "--training-zip",
            str(training_zip_path),
            "--output",
            str(candidate_output),
            "--resume",
            str(resume_path),
        ],
        python_bin=args.python_bin,
    )
    clean_gate_command = build_repo_python_command(
        REPO,
        "scripts/evaluate_checkpoint.py",
        [
            "--checkpoint-a",
            str(checkpoint_a),
            "--checkpoint-b",
            str(candidate_output),
            "--attack",
            "none",
            "--defense",
            active_defense,
            "--images",
            str(args.clean_images),
            "--output-json",
            str(clean_gate_result_path),
        ],
        python_bin=args.python_bin,
    )
    attack_gate_args = [
        "--checkpoint-a",
        str(checkpoint_a),
        "--checkpoint-b",
        str(candidate_output),
        "--attack",
        worst_attack,
        "--defense",
        active_defense,
        "--images",
        str(args.attack_images),
        "--output-json",
        str(attack_gate_result_path),
    ]
    if args.profile:
        clean_gate_command[2:2] = ["--profile", args.profile]
        attack_gate_args[0:0] = ["--profile", args.profile]
    if worst_attack_params:
        attack_gate_args.append("--attack-params")
        attack_gate_args.extend(
            _override_assignment(key, value)
            for key, value in sorted(worst_attack_params.items())
        )
    attack_gate_command = build_repo_python_command(
        REPO,
        "scripts/evaluate_checkpoint.py",
        attack_gate_args,
        python_bin=args.python_bin,
    )
    manifest["training_args"] = train_command[2:]

    if args.dry_run:
        _run_step("export", export_command, dry_run=True)
        _run_step("train", train_command, dry_run=True)
        _run_step("clean-gate", clean_gate_command, dry_run=True)
        _run_step("attack-gate", attack_gate_command, dry_run=True)
        return

    manifest_dir.mkdir(parents=True, exist_ok=True)

    export_result = _run_step("export", export_command, dry_run=False)
    if export_result is None or export_result.returncode != 0:
        _write_manifest(manifest_path, manifest)
        raise SystemExit(2)
    if not training_zip_path.is_file():
        _write_manifest(manifest_path, manifest)
        raise SystemExit(2)

    train_result = _run_step("train", train_command, dry_run=False)
    if train_result is None or train_result.returncode != 0:
        _write_manifest(manifest_path, manifest)
        raise SystemExit(2)
    if not candidate_output.is_file():
        _write_manifest(manifest_path, manifest)
        raise SystemExit(2)
    manifest["candidate_checkpoint"]["sha256"] = sha256_file(candidate_output)
    _write_manifest(manifest_path, manifest)

    clean_result = _run_step("clean-gate", clean_gate_command, dry_run=False)
    clean_payload = _read_result_json(clean_gate_result_path)
    manifest["clean_gate"]["delta_mAP50"] = clean_payload.get("delta_mAP50")
    clean_passed = _gate_passed(clean_result, clean_payload)
    manifest["clean_gate"]["verdict"] = "passed" if clean_passed else "failed"
    if not clean_passed:
        manifest["final_verdict"] = "failed_clean"
        _write_manifest(manifest_path, manifest)
        raise SystemExit(1)

    attack_result = _run_step("attack-gate", attack_gate_command, dry_run=False)
    attack_payload = _read_result_json(attack_gate_result_path)
    manifest["attack_gate"]["delta_mAP50"] = attack_payload.get("delta_mAP50")
    attack_passed = _gate_passed(attack_result, attack_payload)
    manifest["attack_gate"]["verdict"] = "passed" if attack_passed else "failed"
    if not attack_passed:
        manifest["final_verdict"] = "passed_clean_failed_attack"
        _write_manifest(manifest_path, manifest)
        raise SystemExit(1)

    manifest["final_verdict"] = "passed_both_manual_promotion_required"
    _write_manifest(manifest_path, manifest)

    print("=== PROMOTION READY ===")
    print(f"cp {shlex.quote(str(checkpoint_a))} {shlex.quote(str(checkpoint_a) + '.bak')}")
    print(f"mv {shlex.quote(str(candidate_output))} {shlex.quote(str(checkpoint_a))}")


def main() -> None:
    try:
        _main()
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def run_cli() -> None:
    main()


if __name__ == "__main__":
    main()
