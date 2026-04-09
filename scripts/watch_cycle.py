#!/usr/bin/env python3
"""Live terminal watcher for auto_cycle.py progress.

Run on the NUC via SSH:
    ssh -t lurch@10.0.0.113 'cd /home/lurch/YOLO-Bad-Triangle && \
        .venv/bin/python scripts/watch_cycle.py'

Or attach it to tmux:
    ssh -t lurch@10.0.0.113 'tmux new-session -A -s cycle-status \
        "cd /home/lurch/YOLO-Bad-Triangle && .venv/bin/python scripts/watch_cycle.py"'

Or locally if outputs/ is mounted:
    PYTHONPATH=src ./.venv/bin/python scripts/watch_cycle.py [--outputs-root /path/to/outputs]

Press Ctrl-C to exit.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import shutil
import subprocess
import time

SLOW_ATTACKS = {"square", "eot_pgd", "dispersion_reduction"}

# Rough seconds/image for ETA estimates (conservative)
SECS_PER_IMAGE: dict[str, float] = {
    "square": 130,
    "eot_pgd": 50,
    "dispersion_reduction": 65,
    "deepfool": 12,
    "cw": 25,
    "pgd": 5,
    "fgsm": 3,
    "blur": 2,
    "gaussian_blur": 2,
}
DEFAULT_SECS_PER_IMAGE = 10

_RUN_RE = re.compile(r"\brun:\s+([A-Za-z0-9_.-]+)")
_PROGRESS_RE = re.compile(
    r"Preparing images:.*?\|\s*(\d+)/(\d+)\s*\[([^\]<]+)<([^,\]]+),\s*([0-9.]+)s/img\]"
)
_TEMP_RE = re.compile(r"([+-]?\d+(?:\.\d+)?)°C")


def _elapsed(iso_ts: str) -> str:
    try:
        start = datetime.datetime.fromisoformat(iso_ts)
        secs = int((datetime.datetime.now() - start).total_seconds())
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h {m:02d}m"
        return f"{m}m {s:02d}s"
    except Exception:
        return "?"


def _read_json(path: pathlib.Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _count_lines(path: pathlib.Path) -> int:
    try:
        return sum(1 for _ in path.open())
    except Exception:
        return 0


def _attack_from_name(run_name: str) -> str | None:
    for atk in sorted(SECS_PER_IMAGE, key=len, reverse=True):
        if atk in run_name:
            return atk
    return None


def _phase_icon(complete: bool, current_phase: int, phase_num: int) -> str:
    if complete:
        return "[done]"
    if current_phase == phase_num:
        return "[live]"
    return "[wait]"


def _expected_validate_runs(state: dict) -> list[str]:
    runs = ["validate_baseline"]
    for attack in state.get("top_attacks") or []:
        runs.append(f"validate_atk_{attack}")
    for attack in state.get("top_attacks") or []:
        for defense in state.get("top_defenses") or []:
            runs.append(f"validate_{attack}_{defense}")
    return runs


def _infer_image_cap(run_name: str) -> int:
    attack = _attack_from_name(run_name)
    if attack in SLOW_ATTACKS:
        return 50
    return 500


def _run_table(run_dirs: list[pathlib.Path]) -> str:
    rows: list[list[str]] = []
    for d in sorted(run_dirs):
        mf = d / "metrics.json"
        pj = d / "predictions.jsonl"
        if mf.exists():
            m = _read_json(mf)
            n = m.get("predictions", {}).get("image_count", "?") if m else "?"
            rows.append(["done", d.name, f"{n} imgs"])
        elif pj.exists():
            n_done = _count_lines(pj)
            rows.append(["run", d.name, f"{n_done} imgs"])
        else:
            rows.append(["wait", d.name, ""])
    return _format_table(["State", "Run", "Detail"], rows)


def _parse_duration_seconds(text: str) -> int | None:
    parts = text.strip().split(":")
    try:
        values = [int(part) for part in parts]
    except ValueError:
        return None
    if len(values) == 3:
        return values[0] * 3600 + values[1] * 60 + values[2]
    if len(values) == 2:
        return values[0] * 60 + values[1]
    return None


def _tail_text(path: pathlib.Path, max_bytes: int = 200_000) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            return handle.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _parse_progress_snapshot(log_text: str) -> dict | None:
    if not log_text:
        return None

    normalized = log_text.replace("\r", "\n")
    run_names = _RUN_RE.findall(normalized)
    progress_matches = list(_PROGRESS_RE.finditer(normalized))
    if not progress_matches:
        return None

    last = progress_matches[-1]
    return {
        "run_name": run_names[-1] if run_names else None,
        "done": int(last.group(1)),
        "total": int(last.group(2)),
        "elapsed": last.group(3),
        "remaining": last.group(4),
        "secs_per_image": float(last.group(5)),
    }


def _extract_set_arg(args: str, key: str) -> str | None:
    match = re.search(rf"--set\s+{re.escape(key)}=([^\s]+)", args)
    return match.group(1) if match else None


def _parse_process_snapshot(ps_output: str, repo_root: pathlib.Path) -> dict | None:
    target_root = str(repo_root)
    lines = [line.strip() for line in ps_output.splitlines() if line.strip()]

    def _parse_line(line: str, kind: str) -> dict | None:
        parts = line.split(None, 4)
        if len(parts) < 5:
            return None
        pid, etime, cpu, mem, args = parts
        return {
            "pid": pid,
            "elapsed": etime,
            "cpu": cpu,
            "mem": mem,
            "args": args,
            "kind": kind,
            "run_name": _extract_set_arg(args, "runner.run_name"),
            "attack": _extract_set_arg(args, "attack.name"),
            "defense": _extract_set_arg(args, "defense.name"),
        }

    for needle, kind, require_root in (
        ("run_experiment.py", "run_experiment", True),
        ("scripts/run_unified.py run-one", "run_unified", True),
        ("scripts/auto_cycle.py --loop", "auto_cycle", False),
    ):
        for line in lines:
            if needle not in line:
                continue
            if require_root and target_root not in line:
                continue
            parsed = _parse_line(line, kind)
            if parsed is not None:
                return parsed
    return None


def _read_process_snapshot(repo_root: pathlib.Path) -> dict | None:
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid=,etime=,%cpu=,%mem=,args="],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return None
    return _parse_process_snapshot(result.stdout, repo_root)


def _parse_thermals(text: str) -> list[dict]:
    entries: list[dict] = []
    chip: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            chip = None
            continue
        if not line.startswith(" ") and ":" not in line:
            chip = line.strip()
            continue
        if "temp" not in line.lower():
            continue
        label, _, rest = line.partition(":")
        match = _TEMP_RE.search(rest)
        if not match:
            continue
        temp_c = float(match.group(1))
        if temp_c < -50 or temp_c > 200:
            continue
        entries.append(
            {
                "chip": chip or "sensor",
                "label": label.strip(),
                "temp_c": temp_c,
            }
        )

    entries.sort(key=lambda item: item["temp_c"], reverse=True)
    return entries


def _read_thermals() -> list[dict]:
    try:
        result = subprocess.run(["sensors"], capture_output=True, text=True, check=True)
    except Exception:
        return []
    return _parse_thermals(result.stdout)


def _terminal_width() -> int:
    return shutil.get_terminal_size((120, 40)).columns


def _rule(title: str = "", char: str = "=") -> str:
    width = max(60, _terminal_width())
    if not title:
        return char * width
    label = f" {title} "
    if len(label) >= width:
        return label
    left = (width - len(label)) // 2
    right = width - len(label) - left
    return f"{char * left}{label}{char * right}"


def _truncate(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["-", "-", "-"][: len(headers)]]

    widths = [len(header) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))

    total = sum(widths) + (3 * (len(headers) - 1))
    max_width = max(60, _terminal_width())
    if total > max_width:
        shrinkable = [idx for idx in range(len(widths) - 1)]
        while total > max_width and shrinkable:
            idx = max(shrinkable, key=lambda item: widths[item])
            if widths[idx] <= max(len(headers[idx]), 12):
                shrinkable.remove(idx)
                continue
            widths[idx] -= 1
            total -= 1

    def render(row: list[str]) -> str:
        cells = []
        for idx, cell in enumerate(row):
            value = _truncate(str(cell), widths[idx])
            cells.append(value.ljust(widths[idx]))
        return " | ".join(cells)

    lines = [render(headers), "-+-".join("-" * width for width in widths)]
    lines.extend(render(row) for row in rows)
    return "\n".join(lines)


def _format_key_values(rows: list[tuple[str, str]]) -> str:
    if not rows:
        return "  (none)"
    key_width = max(len(key) for key, _ in rows)
    return "\n".join(f"  {key.ljust(key_width)} : {value}" for key, value in rows)


def _live_status_text(process: dict | None, progress: dict | None, log_file: pathlib.Path) -> str:
    rows: list[tuple[str, str]] = []

    if process is None:
        rows.append(("State", "No active auto_cycle process detected"))
    elif process["kind"] == "auto_cycle":
        rows.extend(
            [
                ("Loop PID", process["pid"]),
                ("State", "Idle between runs"),
                ("Elapsed", process["elapsed"]),
                ("CPU", f'{process["cpu"]}%'),
            ]
        )
    else:
        rows.extend(
            [
                ("Worker PID", process["pid"]),
                ("Run", process.get("run_name") or "unknown"),
                ("Stage", f'{process.get("attack") or "?"} -> {process.get("defense") or "?"}'),
                ("Elapsed", process["elapsed"]),
                ("CPU / MEM", f'{process["cpu"]}% / {process["mem"]}%'),
            ]
        )
        if progress and progress.get("run_name") == process.get("run_name"):
            rows.append(
                ("Progress", f'{progress["done"]}/{progress["total"]} at {progress["secs_per_image"]:.1f}s/img')
            )
            rows.append(("ETA", f'~{progress["remaining"]} remaining'))

    try:
        updated = datetime.datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%H:%M:%S")
        rows.append(("Log", f"updated {updated}"))
    except Exception:
        pass

    return _format_key_values(rows)


def _thermals_text(thermals: list[dict]) -> str:
    if not thermals:
        return "  No sensor data"

    rows = []
    for entry in thermals[:5]:
        rows.append(
            [
                f'{entry["chip"]}/{entry["label"]}',
                f'{entry["temp_c"]:.1f}C',
            ]
        )
    return _format_table(["Sensor", "Temp"], rows)


def _validate_table(run_names: list[str], runs_root: pathlib.Path, progress: dict | None, process: dict | None) -> str:
    rows: list[list[str]] = []
    baseline_map50: float | None = None
    pending_secs = 0
    live_run = (progress or {}).get("run_name") or (process or {}).get("run_name")

    for run_name in run_names:
        run_dir = runs_root / run_name
        mf = run_dir / "metrics.json"
        pj = run_dir / "predictions.jsonl"
        m = _read_json(mf) if mf.exists() else None

        if m:
            val = m.get("validation", {})
            map50 = val.get("mAP50")
            n = m.get("predictions", {}).get("image_count", "?")
            map_str = f"{map50:.4f}" if isinstance(map50, float) else "N/A"
            if run_name == "validate_baseline":
                baseline_map50 = map50
            elif baseline_map50 and isinstance(map50, float):
                drop = baseline_map50 - map50
                if drop > 0.25:
                    map_str = f"{map_str} (-{drop:.3f})"
                elif drop > 0.1:
                    map_str = f"{map_str} (-{drop:.3f})"
            rows.append([run_name, "done", map_str, str(n)])
            continue

        cap = _infer_image_cap(run_name)

        if run_name == live_run:
            if progress and progress.get("run_name") == run_name:
                pending_secs += _parse_duration_seconds(progress["remaining"]) or 0
                rows.append([run_name, "running", "...", f'{progress["done"]}/{progress["total"]}'])
            elif pj.exists():
                n_done = _count_lines(pj)
                rows.append([run_name, "running", "...", f"{n_done}/{cap}"])
            else:
                secs = int(SECS_PER_IMAGE.get(_attack_from_name(run_name) or "", DEFAULT_SECS_PER_IMAGE) * cap)
                pending_secs += secs
                rows.append([run_name, "starting", "...", f"0/{cap}"])
            continue

        if pj.exists():
            n_done = _count_lines(pj)
            rows.append([run_name, "running", "...", f"{n_done}/{cap}"])
            remaining = max(0, cap - n_done)
            pending_secs += int(remaining * SECS_PER_IMAGE.get(_attack_from_name(run_name) or "", DEFAULT_SECS_PER_IMAGE))
            continue

        pending_secs += int(cap * SECS_PER_IMAGE.get(_attack_from_name(run_name) or "", DEFAULT_SECS_PER_IMAGE))
        rows.append([run_name, "pending", "-", f"0/{cap}"])

    table = _format_table(["Run", "Status", "mAP50", "Imgs"], rows)
    if pending_secs <= 0:
        return table

    eta = datetime.datetime.now() + datetime.timedelta(seconds=pending_secs)
    return (
        f"{table}\n"
        f"Rough remaining: {int(pending_secs / 3600)}h {int((pending_secs % 3600) / 60)}m"
        f"  |  ETA ~{eta.strftime('%H:%M')}"
    )


def build_display(outputs: pathlib.Path) -> str:
    state_file = outputs / "cycle_state.json"
    state = _read_json(state_file)

    if state is None:
        return "Waiting for cycle_state.json..."

    repo_root = outputs.parent
    log_file = repo_root / "logs" / "auto_cycle.log"
    progress = _parse_progress_snapshot(_tail_text(log_file))
    process = _read_process_snapshot(repo_root)
    thermals = _read_thermals()

    cycle_id = state.get("cycle_id", "unknown")
    phase = state.get("current_phase", 0)
    started_at = state.get("started_at", "")
    runs_root = pathlib.Path(state.get("runs_root", ""))

    header = [
        _rule("YOLO-Bad-Triangle Live Status"),
        f"Cycle: {cycle_id}",
        f"Phase: {phase}/4    Elapsed: {_elapsed(started_at)}    Now: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Phases: "
        + "  ".join(
            [
                f'{_phase_icon(state.get("phase1_complete", False), phase, 1)} characterize',
                f'{_phase_icon(state.get("phase2_complete", False), phase, 2)} matrix',
                f'{_phase_icon(state.get("phase3_complete", False), phase, 3)} tune',
                f'{_phase_icon(state.get("phase4_complete", False), phase, 4)} validate',
            ]
        ),
    ]

    top_attacks = state.get("top_attacks") or []
    top_defenses = state.get("top_defenses") or []
    header.extend(
        [
            f"Top attacks : {', '.join(top_attacks) if top_attacks else 'not decided yet'}",
            f"Top defenses: {', '.join(top_defenses) if top_defenses else 'not decided yet'}",
        ]
    )

    sections = ["\n".join(header)]
    sections.append(_rule("Live Runner", "-"))
    sections.append(_live_status_text(process, progress, log_file))
    sections.append(_rule("Thermals", "-"))
    sections.append(_thermals_text(thermals))

    if runs_root.exists():
        all_dirs = [d for d in runs_root.iterdir() if d.is_dir()]
        validate_dirs = [d for d in all_dirs if d.name.startswith("validate")]
        validate_names = _expected_validate_runs(state)
        other_dirs = [d for d in all_dirs if not d.name.startswith("validate")]

        if phase >= 4 or validate_dirs:
            sections.append(_rule("Phase 4 Validation", "-"))
            sections.append(_validate_table(validate_names, runs_root, progress, process))
        elif other_dirs:
            phase_label = {1: "Phase 1 Characterize", 2: "Phase 2 Matrix", 3: "Phase 3 Tune"}.get(phase, f"Phase {phase}")
            sections.append(_rule(phase_label, "-"))
            sections.append(_run_table(other_dirs))

    if state.get("complete"):
        sections.append(_rule("Cycle Complete", "-"))
        sections.append("Cycle complete; auto_cycle should roll to the next cycle on its next loop.")

    return "\n\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Live watcher for auto_cycle.py")
    parser.add_argument(
        "--outputs-root",
        type=pathlib.Path,
        default=pathlib.Path("outputs"),
        help="Path to the outputs/ directory (default: ./outputs)",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=5.0,
        help="Refresh interval in seconds (default: 5)",
    )
    args = parser.parse_args()

    outputs = args.outputs_root.expanduser().resolve()

    try:
        while True:
            print("\033[2J\033[H", end="")
            print(build_display(outputs), flush=True)
            time.sleep(args.refresh)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")


if __name__ == "__main__":
    main()
