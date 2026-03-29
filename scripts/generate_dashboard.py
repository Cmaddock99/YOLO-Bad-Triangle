#!/usr/bin/env python3
"""Generate a static HTML dashboard from all sweep reports.

Usage:
    PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py
    PYTHONPATH=src ./.venv/bin/python scripts/generate_dashboard.py \
        --reports-root outputs/framework_reports \
        --output outputs/dashboard.html

Output:
    outputs/dashboard.html  — single self-contained file, open in any browser.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.32.0.min.js"

ATTACK_COLORS = {
    "fgsm": "#4C72B0",
    "pgd": "#DD8452",
    "deepfool": "#C44E52",
    "blur": "#55A868",
    "gaussian_blur": "#8172B3",
    "bim": "#937860",
    "ifgsm": "#DA8BC3",
}

DEFENSE_COLORS = {
    "c_dog": "#E377C2",
    "median_preprocess": "#7F7F7F",
    "none": "#BCBD22",
}

DEFENSE_LABELS = {
    "c_dog": "DPC-UNet (c_dog)",
    "median_preprocess": "Median Filter",
    "none": "Undefended",
}


def _attack_color(attack: str) -> str:
    return ATTACK_COLORS.get(attack, "#999999")


def _defense_color(defense: str) -> str:
    return DEFENSE_COLORS.get(defense, "#999999")


def _defense_label(defense: str) -> str:
    return DEFENSE_LABELS.get(defense, defense)


def _sweep_label(sweep_dir: str) -> str:
    """Convert sweep_20260321T183700Z → Mar 21 17:37."""
    m = re.search(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})", sweep_dir)
    if not m:
        return sweep_dir
    _, mo, day, hr, mn = m.groups()
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(mo)]} {int(day)} {hr}:{mn}"


def _load_sweep(report_dir: Path) -> dict | None:
    """Load a single sweep's CSV into a list of row dicts. Returns None if unusable."""
    csv_path = report_dir / "framework_run_summary.csv"
    if not csv_path.is_file():
        return None
    rows = []
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append(row)
    if not rows:
        return None

    # Prefer explicit full-validation baseline when present; fall back to generic none/none.
    baseline = next((r for r in rows if r.get("run_name") == "validate_baseline"), None)
    if baseline is None:
        baseline = next((r for r in rows if r["attack"] == "none" and r["defense"] == "none"), None)
    if not baseline or not baseline.get("total_detections"):
        return None
    baseline_det = float(baseline["total_detections"])

    runs = []
    for r in rows:
        try:
            det = float(r["total_detections"])
        except (ValueError, TypeError):
            continue
        drop = (baseline_det - det) / baseline_det if baseline_det else 0
        runs.append({
            "run_name": r["run_name"],
            "attack": r["attack"],
            "defense": r["defense"],
            "total_detections": det,
            "avg_confidence": float(r["avg_confidence"]) if r.get("avg_confidence") else None,
            "detection_drop": round(drop * 100, 1),
            "mAP50": float(r["mAP50"]) if r.get("mAP50") else None,
        })

    return {
        "sweep": report_dir.name,
        "label": _sweep_label(report_dir.name),
        "baseline_detections": baseline_det,
        "runs": runs,
    }


def _build_heatmap_data(sweep: dict) -> tuple[list, list, list, list]:
    """Return attacks, defenses, z-matrix, text-matrix for the heatmap."""
    defended = [r for r in sweep["runs"] if r["defense"] not in ("none", "")]
    if not defended:
        return [], [], [], []

    attacks = sorted({r["attack"] for r in defended})
    defenses = sorted({r["defense"] for r in defended})

    z = []
    text = []
    for defense in defenses:
        row_z = []
        row_t = []
        for attack in attacks:
            match = next(
                (r for r in defended if r["attack"] == attack and r["defense"] == defense),
                None,
            )
            if match:
                row_z.append(match["detection_drop"])
                row_t.append(
                    f"{match['detection_drop']}%<br>{int(match['total_detections'])} detections"
                )
            else:
                row_z.append(None)
                row_t.append("n/a")
        z.append(row_z)
        text.append(row_t)

    defense_labels = [_defense_label(d) for d in defenses]
    return attacks, defense_labels, z, text


def _build_trend_data(sweeps: list[dict]) -> list[dict]:
    """Build one trace per attack+defense combo showing detection drop over time."""
    # Collect all combos
    combos: set[tuple[str, str]] = set()
    for sw in sweeps:
        for r in sw["runs"]:
            if r["defense"] not in ("none", ""):
                combos.add((r["attack"], r["defense"]))

    traces = []
    for attack, defense in sorted(combos):
        x, y = [], []
        for sw in sweeps:
            match = next(
                (r for r in sw["runs"] if r["attack"] == attack and r["defense"] == defense),
                None,
            )
            if match:
                x.append(sw["label"])
                y.append(match["detection_drop"])
        if len(x) < 1:
            continue
        traces.append({
            "x": x,
            "y": y,
            "name": f"{attack} + {_defense_label(defense)}",
            "mode": "lines+markers",
            "line": {"color": _attack_color(attack), "width": 2},
            "marker": {"size": 8, "symbol": "circle" if defense == "c_dog" else "square"},
        })
    return traces


def _build_attack_bar_data(sweep: dict) -> list[dict]:
    """Bar chart of undefended attack detection drops."""
    attacked = [r for r in sweep["runs"] if r["attack"] != "none" and r["defense"] in ("none", "")]
    return [
        {
            "x": [r["attack"] for r in attacked],
            "y": [r["detection_drop"] for r in attacked],
            "type": "bar",
            "marker": {"color": [_attack_color(r["attack"]) for r in attacked]},
            "text": [f"{r['detection_drop']}%" for r in attacked],
            "textposition": "outside",
        }
    ]


def _summary_cards_html(sweeps: list[dict]) -> str:
    latest = sweeps[-1]
    defended = [r for r in latest["runs"] if r["defense"] not in ("none", "")]
    best = min(
        defended,
        key=lambda r: r["detection_drop"] if r["detection_drop"] is not None else float("inf"),
    ) if defended else None
    effective_attacks = [
        r
        for r in latest["runs"]
        if r["attack"] != "none" and r["defense"] in ("none", "")
        and r["detection_drop"] is not None and r["detection_drop"] > 0
    ]
    worst_attack = max(
        effective_attacks,
        key=lambda r: r["detection_drop"],
        default=None,
    )

    def card(title: str, value: str, sub: str = "", color: str = "#4C72B0") -> str:
        return f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value" style="color:{color}">{value}</div>
            <div class="card-sub">{sub}</div>
        </div>"""

    cards = [
        card("Total Sweeps", str(len(sweeps)), "runs recorded"),
        card("Baseline Detections", str(int(latest["baseline_detections"])),
             "clean images, no attack", "#2ca02c"),
        card("Strongest Attack", worst_attack["attack"].upper() if worst_attack else "NO_EFFECTIVE_ATTACK",
             f"−{worst_attack['detection_drop']}% detections" if worst_attack else "all attacks had 0.0% drop",
             "#C44E52"),
        card("Best Defense (latest)", best["defense"] if best else "—",
             f"vs {best['attack']}: −{best['detection_drop']}%" if best else "",
             "#E377C2"),
    ]
    return '<div class="cards">' + "".join(cards) + "</div>"


def _run_table_html(sweep: dict) -> str:
    rows_html = ""
    defended = sorted(
        [r for r in sweep["runs"] if r["defense"] not in ("none", "")],
        key=lambda r: r["detection_drop"],
    )
    for r in defended:
        drop = r["detection_drop"]
        color = "#c0392b" if drop > 60 else "#e67e22" if drop > 30 else "#27ae60"
        rows_html += f"""
        <tr>
            <td><span class="badge attack">{r['attack']}</span></td>
            <td><span class="badge defense">{_defense_label(r['defense'])}</span></td>
            <td style="color:{color}; font-weight:600">{drop}%</td>
            <td>{int(r['total_detections'])}</td>
            <td>{round(r['avg_confidence'], 4) if r['avg_confidence'] else '—'}</td>
        </tr>"""
    return f"""
    <table>
        <thead>
            <tr>
                <th>Attack</th><th>Defense</th>
                <th>Detection Drop</th><th>Detections</th><th>Avg Confidence</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>"""


def generate(reports_root: Path, output: Path) -> None:
    sweep_dirs = sorted(
        [d for d in reports_root.iterdir() if d.is_dir() and d.name.startswith("sweep_")],
        key=lambda d: d.name,
    )

    sweeps = []
    for d in sweep_dirs:
        sw = _load_sweep(d)
        if sw:
            sweeps.append(sw)

    if not sweeps:
        raise RuntimeError(f"No usable sweep data found under {reports_root}")

    latest = sweeps[-1]
    attacks, defense_labels, z, text = _build_heatmap_data(latest)
    trend_traces = _build_trend_data(sweeps)
    attack_bars = _build_attack_bar_data(latest)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    heatmap_json = json.dumps([{
        "type": "heatmap",
        "x": attacks,
        "y": defense_labels,
        "z": z,
        "text": text,
        "hovertemplate": "<b>%{x}</b> + <b>%{y}</b><br>Drop: %{z}%<extra></extra>",
        "colorscale": [[0, "#27ae60"], [0.5, "#f39c12"], [1, "#c0392b"]],
        "zmin": 0,
        "zmax": 100,
        "showscale": True,
        "colorbar": {"title": "Detection Drop %"},
        "texttemplate": "%{text}",
        "textfont": {"size": 12, "color": "white"},
    }])

    trend_json = json.dumps(trend_traces)

    attack_bar_json = json.dumps(attack_bars)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YOLO Adversarial Robustness Dashboard</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e0e0e0; padding: 24px; }}
  h1 {{ font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; }}
  .subtitle {{ color: #888; font-size: 0.85rem; margin-bottom: 28px; }}
  h2 {{ font-size: 1.1rem; font-weight: 600; color: #ccc; margin: 32px 0 12px; }}
  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }}
  .card {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
           padding: 18px 24px; min-width: 180px; flex: 1; }}
  .card-title {{ font-size: 0.75rem; color: #888; text-transform: uppercase;
                 letter-spacing: 0.05em; margin-bottom: 6px; }}
  .card-value {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }}
  .card-sub {{ font-size: 0.78rem; color: #666; }}
  .chart-box {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
                padding: 20px; margin-bottom: 20px; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ text-align: left; padding: 10px 14px; color: #888; font-weight: 500;
        border-bottom: 1px solid #2a2d3a; text-transform: uppercase;
        font-size: 0.75rem; letter-spacing: 0.05em; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #1e2130; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #20243a; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 0.78rem; font-weight: 600; }}
  .badge.attack {{ background: #1e2a40; color: #7aabff; }}
  .badge.defense {{ background: #2a1e3a; color: #d4a6ff; }}
  @media (max-width: 800px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
  details {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
             padding: 18px 24px; margin-bottom: 28px; }}
  summary {{ font-size: 0.95rem; font-weight: 600; color: #aaa; cursor: pointer;
             letter-spacing: 0.02em; list-style: none; display: flex;
             align-items: center; gap: 8px; }}
  summary::before {{ content: "▶"; font-size: 0.7rem; color: #555;
                     transition: transform 0.2s; }}
  details[open] summary::before {{ transform: rotate(90deg); }}
  summary::-webkit-details-marker {{ display: none; }}
  .context p {{ color: #999; font-size: 0.88rem; line-height: 1.75;
                margin-bottom: 12px; max-width: 860px; }}
  .context p:last-child {{ margin-bottom: 0; }}
  .context strong {{ color: #ccc; font-weight: 600; }}
  .glossary {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 32px;
               margin-top: 14px; }}
  .glossary dt {{ color: #7aabff; font-size: 0.82rem; font-weight: 600;
                  margin-bottom: 2px; }}
  .glossary dd {{ color: #888; font-size: 0.82rem; line-height: 1.5;
                  margin-bottom: 8px; }}
  @media (max-width: 800px) {{
    .two-col {{ grid-template-columns: 1fr; }}
    .glossary {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<h1>YOLO Adversarial Robustness Dashboard</h1>
<div class="subtitle">Model: yolo26n &nbsp;·&nbsp; Dataset: 500 COCO val images
  &nbsp;·&nbsp; {len(sweeps)} sweep(s) &nbsp;·&nbsp; Generated: {generated_at}</div>

<details>
  <summary>About this research</summary>
  <div class="context" style="margin-top:16px">
    <p>
      This dashboard tracks an ongoing research programme testing the <strong>reliability of
      AI-based object detection</strong> under deliberate interference — and evaluating methods
      to restore that reliability.
    </p>
    <p>
      The AI system under study — a computer vision model called YOLO — is trained to identify
      objects in photographs: people, vehicles, animals, and hundreds of other categories. In
      normal conditions it performs with high accuracy. The question this research asks is:
      <strong>how easily can that accuracy be undermined, and can it be protected?</strong>
    </p>
    <p>
      The interference method is called an <strong>adversarial attack</strong>. An attacker
      makes mathematically precise, often imperceptible changes to the pixels of an image —
      changes invisible to the human eye — that cause the AI to miss objects it would otherwise
      detect with confidence. This is not a theoretical concern: the same class of models
      underpins real-world systems in autonomous vehicles, medical imaging, and security
      infrastructure.
    </p>
    <p>
      Each experiment runs 500 unmodified photographs through the model to establish a
      <strong>baseline</strong> (how many objects it finds under normal conditions), then repeats
      the process on versions of those same images that have been subjected to each attack. The
      percentage drop in detections is the primary measure of an attack's severity.
    </p>
    <p>
      The <strong>defenses</strong> are pre-processing steps applied to attacked images before
      the model sees them — essentially attempting to reverse or neutralise the interference.
      The central defense under development here (DPC-UNet) is a purpose-trained neural network
      that has been iteratively fine-tuned across multiple experimental rounds to better preserve
      the visual detail the model relies on for detection. The trend charts below reflect that
      improvement over time.
    </p>
    <dl class="glossary">
      <dt>Detection Drop</dt>
      <dd>The percentage reduction in objects identified compared to unmodified images.
          Lower is better. A 90% drop means the model missed 9 in 10 objects it would
          normally find.</dd>
      <dt>Baseline</dt>
      <dd>The model's performance on clean, unaltered photographs — the reference point
          against which all attacks and defenses are measured.</dd>
      <dt>FGSM / PGD / Blur</dt>
      <dd>Relatively mild attack methods that cause 12–17% detection loss. The model
          retains most of its capability under these conditions.</dd>
      <dt>DeepFool</dt>
      <dd>A precision attack that identifies the mathematically minimal pixel change
          sufficient to cause failure. Consistently the most damaging attack tested,
          causing up to 78% detection loss without a defense.</dd>
      <dt>DPC-UNet (c_dog)</dt>
      <dd>The primary defense under development — a neural network trained to reconstruct
          attacked images before the detector sees them. Performance improves with each
          fine-tuning iteration.</dd>
      <dt>Median Filter</dt>
      <dd>A classical signal-processing defense that smooths irregular pixel patterns.
          Simpler than the neural approach and currently more effective against mild
          attacks, though less adaptable.</dd>
    </dl>
  </div>
</details>

{_summary_cards_html(sweeps)}

<h2>Latest Sweep — Defense Heatmap ({latest['label']})</h2>
<div class="chart-box">
  <div id="heatmap" style="height:320px"></div>
</div>

<div class="two-col">
  <div>
    <h2>Attack Effectiveness (Undefended)</h2>
    <div class="chart-box">
      <div id="attack-bars" style="height:300px"></div>
    </div>
  </div>
  <div>
    <h2>Defense Recovery — Latest Sweep</h2>
    <div class="chart-box" style="overflow-x:auto">
      {_run_table_html(latest)}
    </div>
  </div>
</div>

<h2>Detection Drop Over Time — All Sweeps</h2>
<div class="chart-box">
  <div id="trend" style="height:380px"></div>
</div>

<script>
const dark = {{
  paper_bgcolor: "#1a1d27",
  plot_bgcolor: "#1a1d27",
  font: {{ color: "#cccccc", family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }},
  xaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  yaxis: {{ gridcolor: "#2a2d3a", zerolinecolor: "#2a2d3a" }},
  margin: {{ t: 20, r: 20, b: 50, l: 140 }},
}};

Plotly.newPlot("heatmap", {heatmap_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 120, b: 60, l: 160 }},
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Attack" }}),
    yaxis: Object.assign({{}}, dark.yaxis, {{ title: "" }}),
  }}),
  {{responsive: true, displayModeBar: false}}
);

Plotly.newPlot("attack-bars", {attack_bar_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 20, b: 50, l: 60 }},
    yaxis: Object.assign({{}}, dark.yaxis, {{
      title: "Detection Drop %", range: [0, 100]
    }}),
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Attack" }}),
    showlegend: false,
  }}),
  {{responsive: true, displayModeBar: false}}
);

Plotly.newPlot("trend", {trend_json},
  Object.assign({{}}, dark, {{
    margin: {{ t: 20, r: 20, b: 60, l: 60 }},
    yaxis: Object.assign({{}}, dark.yaxis, {{
      title: "Detection Drop %", range: [0, 105]
    }}),
    xaxis: Object.assign({{}}, dark.xaxis, {{ title: "Sweep" }}),
    legend: {{ bgcolor: "#1a1d27", bordercolor: "#2a2d3a", borderwidth: 1 }},
    hovermode: "x unified",
  }}),
  {{responsive: true, displayModeBar: false}}
);
</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    # Also write to docs/index.html for GitHub Pages
    pages_out = Path("docs/index.html").resolve()
    pages_out.parent.mkdir(parents=True, exist_ok=True)
    pages_out.write_text(html, encoding="utf-8")

    print(f"Dashboard written to {output}")
    print(f"  GitHub Pages:  {pages_out}")
    print(f"  Sweeps loaded: {len(sweeps)}")
    print(f"  Latest sweep:  {latest['label']} ({latest['sweep']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate static HTML dashboard from sweep reports.")
    parser.add_argument(
        "--reports-root",
        default="outputs/framework_reports",
        help="Root directory containing sweep_* report folders.",
    )
    parser.add_argument(
        "--output",
        default="outputs/dashboard.html",
        help="Output HTML file path.",
    )
    args = parser.parse_args()
    generate(
        reports_root=Path(args.reports_root).expanduser().resolve(),
        output=Path(args.output).expanduser().resolve(),
    )


if __name__ == "__main__":
    main()
