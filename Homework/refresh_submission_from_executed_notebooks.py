from __future__ import annotations

import argparse
import ast
import base64
import json
import re
import shutil
import subprocess
from pathlib import Path

import nbformat


ROOT = Path("/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework")
NOTEBOOK_OUT = ROOT / "output" / "notebooks"
EXTRACTED_OUT = ROOT / "output" / "notebook_assets"
SUMMARY_OUT = ROOT / "output" / "lab2_notebook_summary.json"
PDF_BUILDER = ROOT / "build_lab2_submission_pdf.py"

TASK1_CANONICAL = NOTEBOOK_OUT / "Lab2_Task1_Evasion_executed.ipynb"
TASK2_CANONICAL = NOTEBOOK_OUT / "Lab2_Task2_PromptInjection_executed.ipynb"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh the Lab 2 summary and PDF from already-executed notebooks."
    )
    parser.add_argument("task1", type=Path, help="Executed Task 1 notebook (.ipynb)")
    parser.add_argument("task2", type=Path, help="Executed Task 2 notebook (.ipynb)")
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Only rebuild the summary JSON and extracted assets.",
    )
    return parser.parse_args()


def read_notebook(path: Path) -> nbformat.NotebookNode:
    return nbformat.read(path.open(), as_version=4)


def stream_text(cell: nbformat.NotebookNode) -> str:
    parts: list[str] = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            parts.append(output.get("text", ""))
    return "".join(parts).strip()


def copy_if_needed(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == target.resolve():
        return
    shutil.copy2(source, target)


def first_stream_containing(nb: nbformat.NotebookNode, token: str) -> str:
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        text = stream_text(cell)
        if token in text:
            return text
    raise RuntimeError(f"Could not find notebook output containing: {token}")


def first_stream_matching(nb: nbformat.NotebookNode, pattern: str) -> str:
    regex = re.compile(pattern)
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        text = stream_text(cell)
        match = regex.search(text)
        if match:
            return match.group(0)
    raise RuntimeError(f"Could not find notebook output matching: {pattern}")


def extract_colab_proof(nb: nbformat.NotebookNode) -> str:
    for cell in nb.cells:
        if cell.cell_type == "code" and "# COLAB_PROOF_CELL" in cell.source:
            return stream_text(cell)
    return ""


def extract_custom_attack(nb: nbformat.NotebookNode) -> str:
    for cell in nb.cells:
        if cell.cell_type != "code" or "experimental_query" not in cell.source:
            continue

        parsed = ast.parse(cell.source)
        for node in parsed.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id != "experimental_query":
                continue
            return ast.literal_eval(node.value).strip()

    raise RuntimeError("Could not recover the sandbox payload from Task 2.")


def save_task1_images(nb: nbformat.NotebookNode) -> dict[str, str]:
    EXTRACTED_OUT.mkdir(parents=True, exist_ok=True)

    encoded_images: list[str] = []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            png = output.get("data", {}).get("image/png")
            if not png:
                continue
            encoded_images.append(str(png))

    if len(encoded_images) < 2:
        raise RuntimeError("Task 1 did not contain the expected image outputs.")

    original_path = EXTRACTED_OUT / "task1_cell5_output0.png"
    comparison_path = EXTRACTED_OUT / "task1_cell11_output0.png"
    original_path.write_bytes(base64.b64decode(encoded_images[0]))
    comparison_path.write_bytes(base64.b64decode(encoded_images[1]))

    return {
        "cell_5_output_0": str(original_path),
        "cell_11_output_0": str(comparison_path),
    }


def build_summary(task1: nbformat.NotebookNode, task2: nbformat.NotebookNode, images: dict[str, str]) -> None:
    summary = {
        "task1": {
            "initial_prediction": first_stream_matching(
                task1,
                r"Initial Prediction: .+",
            ),
            "adversarial_prediction": first_stream_matching(
                task1,
                r"Adversarial Prediction: .+",
            ),
            "images": images,
            "colab_proof": extract_colab_proof(task1),
        },
        "task2": {
            "normal_run": first_stream_containing(task2, "Sending normal query..."),
            "attack_run": first_stream_containing(task2, "Sending poisoned query..."),
            "sandbox_run": first_stream_containing(
                task2,
                "Sending experimental query to the Agent...",
            ),
            "custom_attack": extract_custom_attack(task2),
            "colab_proof": extract_colab_proof(task2),
        },
    }

    SUMMARY_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()

    task1_path = args.task1.expanduser().resolve()
    task2_path = args.task2.expanduser().resolve()

    task1 = read_notebook(task1_path)
    task2 = read_notebook(task2_path)

    copy_if_needed(task1_path, TASK1_CANONICAL)
    copy_if_needed(task2_path, TASK2_CANONICAL)

    images = save_task1_images(task1)
    build_summary(task1, task2, images)

    print(f"saved {TASK1_CANONICAL}")
    print(f"saved {TASK2_CANONICAL}")
    print(f"saved {SUMMARY_OUT}")

    if not args.skip_pdf:
        subprocess.run(["python3", str(PDF_BUILDER)], check=True)


if __name__ == "__main__":
    main()
