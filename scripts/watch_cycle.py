#!/usr/bin/env python3
"""Live terminal watcher for auto_cycle.py progress.

Run on the NUC via SSH:
    ssh -t lurch@10.0.0.113 'cd /home/lurch/YOLO-Bad-Triangle && \
        .venv/bin/python scripts/watch_cycle.py'

Or locally if outputs/ is mounted:
    PYTHONPATH=src ./.venv/bin/python scripts/watch_cycle.py [--outputs-root /path/to/outputs]

Press Ctrl-C to exit.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys
import time

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
    """Extract attack name from a run directory name."""
    for atk in sorted(SECS_PER_IMAGE, key=len, reverse=True):
        if atk in run_name:
            return atk
    return None


def _phase_icon(complete: bool, current_phase: int, phase_num: int) -> str:
    if complete:
        return "[green]✓[/green]"
    if current_phase == phase_num:
        return "[yellow]●[/yellow]"
    return "[dim]○[/dim]"


def _run_table(run_dirs: list[pathlib.Path], phase: int) -> Table:
    """Build a compact run table for phases 1-3."""
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("icon", width=3)
    t.add_column("name")
    t.add_column("detail", justify="right", style="dim")

    for d in sorted(run_dirs):
        mf = d / "metrics.json"
        pj = d / "predictions.jsonl"
        if mf.exists():
            m = _read_json(mf)
            n = m["predictions"]["image_count"] if m else "?"
            t.add_row("[green]✓[/green]", d.name, f"{n} imgs")
        elif pj.exists():
            n_done = _count_lines(pj)
            t.add_row("[yellow]●[/yellow]", f"[yellow]{d.name}[/yellow]", f"{n_done} imgs…")
        else:
            t.add_row("[dim]○[/dim]", f"[dim]{d.name}[/dim]", "")
    return t


def _validate_table(run_dirs: list[pathlib.Path], state: dict) -> Table:
    """Build Phase 4 validation table with mAP50 and ETA."""
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    t.add_column("Run")
    t.add_column("Status", justify="center", width=14)
    t.add_column("mAP50", justify="right", width=7)
    t.add_column("n_imgs", justify="right", width=6)

    baseline_map50: float | None = None
    pending_secs = 0.0

    for d in sorted(run_dirs):
        mf = d / "metrics.json"
        pj = d / "predictions.jsonl"
        m = _read_json(mf) if mf.exists() else None

        if m:
            val = m.get("validation", {})
            map50 = val.get("mAP50")
            n = m.get("predictions", {}).get("image_count", "?")
            map_str = f"{map50:.4f}" if isinstance(map50, float) else "N/A"
            if d.name == "validate_baseline":
                baseline_map50 = map50
                t.add_row(d.name, "[green]done[/green]", f"[bold]{map_str}[/bold]", str(n))
            else:
                # Colour by recovery vs baseline
                if baseline_map50 and isinstance(map50, float):
                    drop = baseline_map50 - map50
                    colour = "red" if drop > 0.25 else "yellow" if drop > 0.1 else "green"
                    map_str = f"[{colour}]{map_str}[/{colour}]"
                t.add_row(d.name, "[green]done[/green]", map_str, str(n))
        elif pj.exists():
            n_done = _count_lines(pj)
            atk = _attack_from_name(d.name)
            cap = 50 if atk in SLOW_ATTACKS else 500
            t.add_row(d.name, f"[yellow]running {n_done}/{cap}[/yellow]", "…", f"/{cap}")
        else:
            atk = _attack_from_name(d.name)
            cap = 50 if (atk and atk in SLOW_ATTACKS) else 500
            secs = SECS_PER_IMAGE.get(atk or "", DEFAULT_SECS_PER_IMAGE) * cap
            pending_secs += secs
            t.add_row(d.name, "[dim]pending[/dim]", "—", f"/{cap}")

    if pending_secs > 0:
        eta = datetime.datetime.now() + datetime.timedelta(seconds=pending_secs)
        t.caption = f"ETA (rough): ~{eta.strftime('%H:%M')}  ·  {int(pending_secs/3600)}h {int((pending_secs%3600)/60)}m remaining"

    return t


def build_display(outputs: pathlib.Path) -> Panel:
    state_file = outputs / "cycle_state.json"
    state = _read_json(state_file)

    if state is None:
        return Panel(
            "[dim]Waiting for cycle_state.json…[/dim]",
            title="[bold]YOLO-Bad-Triangle Watcher[/bold]",
            border_style="dim",
        )

    cycle_id = state.get("cycle_id", "unknown")
    phase = state.get("current_phase", 0)
    started_at = state.get("started_at", "")
    runs_root = pathlib.Path(state.get("runs_root", ""))

    p1 = _phase_icon(state.get("phase1_complete", False), phase, 1)
    p2 = _phase_icon(state.get("phase2_complete", False), phase, 2)
    p3 = _phase_icon(state.get("phase3_complete", False), phase, 3)
    p4 = _phase_icon(state.get("phase4_complete", False), phase, 4)

    elapsed = _elapsed(started_at)
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    header = Text.from_markup(
        f"[bold]{cycle_id}[/bold]  ·  Phase {phase}/4  ·  {elapsed} elapsed  ·  {now_str}\n"
        f"  {p1} Characterize   {p2} Matrix   {p3} Tune   {p4} Validate"
    )

    top_attacks = state.get("top_attacks") or []
    top_defenses = state.get("top_defenses") or []
    if top_attacks:
        summary = Text.from_markup(
            f"\n[dim]Top attacks:[/dim]  {', '.join(top_attacks)}\n"
            f"[dim]Top defenses:[/dim] {', '.join(top_defenses)}"
        )
    else:
        summary = Text.from_markup("\n[dim]Top attacks/defenses not yet determined[/dim]")

    items: list = [header, summary]

    if runs_root.exists():
        all_dirs = [d for d in runs_root.iterdir() if d.is_dir()]
        validate_dirs = [d for d in all_dirs if d.name.startswith("validate")]
        other_dirs = [d for d in all_dirs if not d.name.startswith("validate")]

        if validate_dirs:
            items.append(Text(""))
            items.append(Text.from_markup("[bold cyan]Phase 4 — Validation Runs[/bold cyan]"))
            items.append(_validate_table(validate_dirs, state))
        elif other_dirs:
            phase_label = {1: "Phase 1 — Characterize", 2: "Phase 2 — Matrix", 3: "Phase 3 — Tune"}.get(phase, f"Phase {phase}")
            items.append(Text(""))
            items.append(Text.from_markup(f"[bold cyan]{phase_label}[/bold cyan]"))
            items.append(_run_table(other_dirs, phase))

    if state.get("complete"):
        items.append(Text(""))
        items.append(Text.from_markup("[bold green]✓ Cycle complete — rolling to next…[/bold green]"))

    return Panel(
        Group(*items),
        title="[bold]YOLO-Bad-Triangle[/bold]",
        border_style="blue",
        subtitle="[dim]Ctrl-C to exit[/dim]",
    )


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
    console = Console()

    try:
        with Live(console=console, refresh_per_second=1 / args.refresh, screen=True) as live:
            while True:
                live.update(build_display(outputs))
                time.sleep(args.refresh)
    except KeyboardInterrupt:
        console.print("\n[dim]Watcher stopped.[/dim]")


if __name__ == "__main__":
    main()
