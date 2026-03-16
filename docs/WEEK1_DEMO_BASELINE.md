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

Note: this frozen reference run uses older run-name formatting.  
Future runs now use clearer names like `baseline-demo-confidence025`
and `fgsm-epsilon-0005-demo-confidence025`.

- Baseline demo run: `precision=0.6245`, `recall=0.5017`, `mAP50=0.5988`, `mAP50-95=0.4688`
- FGSM `epsilon=0.0005`: all validation metrics `0.0`
- FGSM `epsilon=0.001`: all validation metrics `0.0`
- FGSM `epsilon=0.002`: all validation metrics `0.0`

## Fallback narrative

Use this wording if switching to frozen artifacts:

"The pipeline completed on this reference run and produced all outputs. At current week1 epsilons, FGSM fully collapses validation metrics, so this serves as our baseline stress-test result before epsilon re-calibration."
