# Colab Handoff

If you need the final packet to show real Google Colab execution, use the prepared notebook copies below instead of the originals:

- [Lab2_Task1_Evasion_colab.ipynb](/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework/output/colab_ready/Lab2_Task1_Evasion_colab.ipynb)
- [Lab2_Task2_PromptInjection_colab.ipynb](/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework/output/colab_ready/Lab2_Task2_PromptInjection_colab.ipynb)

## What to do in Colab

1. Upload both `_colab.ipynb` notebooks to [Google Colab](https://colab.research.google.com/).
2. Run all cells in each notebook.
3. Keep the `Google Colab Proof Cell` output near the top of each notebook.
4. Download each executed notebook as `.ipynb`.

## Regenerate the PDF locally

Run this command with the two executed notebook files you downloaded from Colab:

```bash
python3 /Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework/refresh_submission_from_executed_notebooks.py \
  /absolute/path/to/Lab2_Task1_Evasion_colab_executed.ipynb \
  /absolute/path/to/Lab2_Task2_PromptInjection_colab_executed.ipynb
```

That will:

- refresh `output/lab2_notebook_summary.json`
- copy the executed notebooks into `output/notebooks/`
- rebuild [lab2_submission_packet.pdf](/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework/output/pdf/lab2_submission_packet.pdf)

## Notes

- The final PDF will include a dedicated `Google Colab Runtime Proof` page if those proof cells were executed in Colab.
- Keep the real notebook outputs even if the Task 1 misclassification differs from the course example.
