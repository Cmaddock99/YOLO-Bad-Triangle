# Week1 Demo Baseline Freeze

This file freezes the fallback artifacts for team demo use.

If a live run fails or finishes with incomplete artifacts, present this known-good output root:

- `outputs/demo-reference`

## Required artifact checklist

Regenerate deterministic plots first (recommended):

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/demo-reference`

Then verify:

- `outputs/demo-reference/metrics_summary.csv`
- `outputs/demo-reference/experiment_table.md`
- `outputs/demo-reference/plots/map50-by-attack.png`
- `outputs/demo-reference/plots/precision-recall-by-attack.png`
- `outputs/demo-reference/plots/baseline-vs-fgsm-metrics.png`
- `outputs/demo-reference/plots/fgsm-epsilon-trend.png`
- `outputs/demo-reference/plots/robustness-report-card.png`
- `outputs/demo-reference/plots/robustness-report-card-by-epsilon.png`

## Frozen metrics summary (for speaking backup)

Reference run profile:

- Model: `yolo26n.pt` (YOLO26)
- Confidence: `0.25`
- Epsilons: `0.0005`, `0.006`, `0.01`

Validation summary from the latest frozen reference:

- Baseline demo run: `precision=0.7474`, `recall=0.5087`, `mAP50=0.6490`, `mAP50-95=0.5088`
- FGSM `epsilon=0.0005`: `precision=0.7390`, `recall=0.5057`, `mAP50=0.6452`, `mAP50-95=0.5067`
- FGSM `epsilon=0.006`: `precision=0.7328`, `recall=0.4487`, `mAP50=0.6109`, `mAP50-95=0.4704`
- FGSM `epsilon=0.01`: `precision=0.7239`, `recall=0.4268`, `mAP50=0.5965`, `mAP50-95=0.4588`

## Fallback narrative

Use this wording if switching to frozen artifacts:

"The pipeline completed on this reference run and produced all outputs. Under YOLO26, FGSM now shows a graded degradation curve across epsilon instead of full collapse, which gives us a stronger demo story for robustness trend analysis."
