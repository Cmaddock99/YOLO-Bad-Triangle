from __future__ import annotations

import json
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path("/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework")
OUT_PDF = ROOT / "output" / "pdf" / "lab2_submission_packet.pdf"
SUMMARY = json.loads((ROOT / "output" / "lab2_notebook_summary.json").read_text())


def clean_task2_output(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        if line.startswith("Passing `generation_config`"):
            continue
        if line.startswith("Both `max_new_tokens`"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def wrap_code_block(text: str, width: int = 82) -> str:
    wrapped_lines = []

    for line in text.splitlines():
        if not line:
            wrapped_lines.append("")
            continue

        wrapped = textwrap.wrap(
            line,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
            drop_whitespace=False,
            replace_whitespace=False,
        )
        wrapped_lines.extend(wrapped or [""])

    return "\n".join(wrapped_lines)


def scaled_image(path: str | Path, max_width: float, max_height: float) -> Image:
    img = Image(str(path))
    width = img.drawWidth
    height = img.drawHeight
    scale = min(max_width / width, max_height / height)
    img.drawWidth = width * scale
    img.drawHeight = height * scale
    return img


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SmallBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            fontName="Courier",
            fontSize=9,
            leading=11,
            leftIndent=8,
            rightIndent=8,
            borderColor=colors.HexColor("#D0D7DE"),
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#F6F8FA"),
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontSize=7,
            leading=9,
            spaceAfter=0,
        )
    )
    return styles


def build_cdm_table(styles):
    data = [
        ["Scenario", "Asset Class", "Operational Function", "Rationale"],
        [
            "A",
            "Data",
            "Protect",
            "Scanning `.pkl` artifacts protects model files before unsafe payloads execute.",
        ],
        [
            "B",
            "Applications",
            "Detect",
            "The API gateway watches the LLM application interface and alerts on prompt-abuse patterns.",
        ],
        [
            "C",
            "Devices",
            "Respond",
            "Server isolation and key revocation are containment actions after compromise.",
        ],
        [
            "D",
            "Data",
            "Identify",
            "An AI BOM inventories and tracks training-data provenance and versions.",
        ],
    ]
    table = Table(data, colWidths=[0.7 * inch, 1.1 * inch, 1.2 * inch, 3.7 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7F0FA")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C0CC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_atlas_table(styles):
    cell = styles["TableCell"]
    data = [
        ["Case Study", "Tactics", "Technique IDs", "Primary Impact"],
        [
            Paragraph("Sponge Attack", cell),
            Paragraph("AI Model Access; AI Attack Staging; Impact", cell),
            Paragraph("AML.T0040, AML.T0043, AML.T0034.001, AML.T0029", cell),
            Paragraph("AML.T0029 Denial of AI Service", cell),
        ],
        [
            Paragraph("Audio Adversarial Perturbation", cell),
            Paragraph("AI Attack Staging; Initial Access; Impact", cell),
            Paragraph("AML.T0043, AML.T0015, AML.T0052, AML.T0048.000", cell),
            Paragraph("AML.T0048.000 Financial Harm", cell),
        ],
        [
            Paragraph("Hugging Face Repository Hijack", cell),
            Paragraph("Initial Access; Execution; Collection; Exfiltration; Impact", cell),
            Paragraph(
                "AML.T0012, AML.T0010.001, AML.T0011.001, AML.T0037, AML.T0025, AML.T0048.004",
                cell,
            ),
            Paragraph("AML.T0048.004 AI Intellectual Property Theft", cell),
        ],
    ]
    table = Table(data, colWidths=[1.2 * inch, 1.7 * inch, 2.35 * inch, 1.95 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F5E9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("LEADING", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C0CC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def add_page_number(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(7.5 * inch, 0.45 * inch, f"Page {doc.page}")


def build_story():
    styles = build_styles()
    story = []

    task1_images = SUMMARY["task1"]["images"]
    task1_colab_proof = SUMMARY["task1"].get("colab_proof", "").strip()
    task2_colab_proof = SUMMARY["task2"].get("colab_proof", "").strip()
    task2_normal = wrap_code_block(clean_task2_output(SUMMARY["task2"]["normal_run"]))
    task2_attack = wrap_code_block(clean_task2_output(SUMMARY["task2"]["attack_run"]))
    task2_sandbox = wrap_code_block(clean_task2_output(SUMMARY["task2"]["sandbox_run"]))
    task2_custom_attack = wrap_code_block(SUMMARY["task2"]["custom_attack"])

    story.append(Paragraph("CYBR 472 Lab 2 Submission Packet", styles["Title"]))
    story.append(Paragraph("Prepared on April 15, 2026", styles["SmallBody"]))
    story.append(
        Paragraph(
            "This packet includes executed notebook outputs, Cyber Defense Matrix answers, MITRE ATLAS mappings, ATLAS Navigator renders, and knowledge-check responses.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    if task1_colab_proof or task2_colab_proof:
        story.append(PageBreak())
        story.append(Paragraph("Google Colab Runtime Proof", styles["Heading1"]))
        story.append(
            Paragraph(
                "These proof blocks were captured from the dedicated runtime-verification cell inserted near the top of each notebook before execution in Google Colab.",
                styles["BodyText"],
            )
        )
        if task1_colab_proof:
            story.append(Paragraph("Task 1 Colab proof:", styles["Heading3"]))
            story.append(Preformatted(wrap_code_block(task1_colab_proof), styles["CodeBlock"]))
        if task2_colab_proof:
            story.append(Paragraph("Task 2 Colab proof:", styles["Heading3"]))
            story.append(Preformatted(wrap_code_block(task2_colab_proof), styles["CodeBlock"]))
        story.append(PageBreak())

    story.append(Paragraph("Task 1: Adversarial Evasion Notebook Output", styles["Heading1"]))
    story.append(
        Paragraph(
            f"Initial prediction from the clean image: <b>{SUMMARY['task1']['initial_prediction']}</b><br/>"
            f"Prediction after FGSM perturbation: <b>{SUMMARY['task1']['adversarial_prediction']}</b>",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Original stop-sign image used by the notebook:", styles["Heading3"]))
    story.append(
        scaled_image(task1_images["cell_5_output_0"], max_width=6.8 * inch, max_height=3.4 * inch)
    )
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Notebook comparison output:", styles["Heading3"]))
    story.append(
        scaled_image(task1_images["cell_11_output_0"], max_width=6.8 * inch, max_height=4.3 * inch)
    )

    story.append(PageBreak())
    story.append(Paragraph("Task 2: Prompt Injection Notebook Output", styles["Heading1"]))
    story.append(
        Paragraph(
            "The notebook was executed with a custom sandbox payload designed to demonstrate a polite natural-language override.",
            styles["BodyText"],
        )
    )
    story.append(Paragraph("Benign scenario output:", styles["Heading3"]))
    story.append(Preformatted(task2_normal, styles["CodeBlock"]))
    story.append(PageBreak())
    story.append(Paragraph("Task 2: Prompt Injection Attack Output", styles["Heading1"]))
    story.append(Paragraph("Prompt injection attack output:", styles["Heading3"]))
    story.append(Preformatted(task2_attack, styles["CodeBlock"]))
    story.append(PageBreak())
    story.append(Paragraph("Task 2: Prompt Injection Sandbox Output", styles["Heading1"]))
    story.append(Paragraph("Sandbox payload used:", styles["Heading3"]))
    story.append(Preformatted(task2_custom_attack, styles["CodeBlock"]))
    story.append(Paragraph("Sandbox result:", styles["Heading3"]))
    story.append(Preformatted(task2_sandbox, styles["CodeBlock"]))

    story.append(PageBreak())
    story.append(Paragraph("Task 2: Cyber Defense Matrix Answers", styles["Heading1"]))
    story.append(build_cdm_table(styles))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Task 3: MITRE ATLAS Mapping Summary", styles["Heading1"]))
    story.append(build_atlas_table(styles))

    atlas_images = [
        ("ATLAS Render: Sponge Attack", ROOT / "output" / "playwright" / "sponge_attack_render.png"),
        (
            "ATLAS Render: Audio Adversarial Perturbation",
            ROOT / "output" / "playwright" / "audio_adversarial_perturbation_render.png",
        ),
        (
            "ATLAS Render: Hugging Face Repository Hijack",
            ROOT / "output" / "playwright" / "hugging_face_repository_hijack_render.png",
        ),
    ]
    for title, image_path in atlas_images:
        story.append(PageBreak())
        story.append(Paragraph(title, styles["Heading1"]))
        story.append(
            Paragraph(
                "Screenshot of the MITRE ATLAS Navigator SVG render for the mapped case study.",
                styles["SmallBody"],
            )
        )
        story.append(scaled_image(image_path, max_width=7.0 * inch, max_height=9.0 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Knowledge Check Responses", styles["Heading1"]))
    knowledge_checks = [
        (
            "1. The Nature of Evasion",
            "A human would probably miss the FGSM noise because the pixel changes are tiny and basically invisible. The image still looks like a stop sign to us, but it is enough to push the model into a different decision.",
        ),
        (
            "2. The Flaw in Chat Templates",
            "Tags like &lt;|im_start|&gt;system are not real security walls. The model still reads everything as one long sequence of tokens, so later malicious text can still compete with or override earlier instructions.",
        ),
        (
            "3. Semantic vs. Syntactic Analysis",
            "Traditional security tools usually look for stable patterns like known code signatures or suspicious syntax. Prompt injection is different because the same bad intent can be written in many normal-sounding ways, so simple pattern matching will miss a lot of cases.",
        ),
        (
            "4. The Navigator Export",
            "It matters because making the adversarial sample and using it are two different steps. One is the attacker building the sample, and the other is the attacker actually using it against the model. Defenders need to separate those steps because the controls and monitoring are different.",
        ),
        (
            "5. Detection vs. Protection",
            "An IDS belongs in Detect because it watches activity and sends alerts. It does not block the action by itself. In the Cyber Defense Matrix, Protect is for controls that actually stop or prevent something.",
        ),
    ]
    for title, body in knowledge_checks:
        story.append(Paragraph(title, styles["Heading3"]))
        story.append(Paragraph(body, styles["BodyText"]))

    return story


def main():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.6 * inch,
    )
    doc.build(build_story(), onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"saved {OUT_PDF}")


if __name__ == "__main__":
    main()
