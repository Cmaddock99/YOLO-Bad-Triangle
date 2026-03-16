# Week1 Demo Rehearsal Log

This file tracks full end-to-end rehearsal outcomes for demo readiness.

## Latest canonical rehearsal root

- Date (UTC): 2026-03-15
- Command:
  - `./scripts/run_week1_stabilization.sh --mode demo --config configs/week1_stabilization_demo_matrix.yaml`
- Output root:
  - `outputs/demo-reference` (linked to timestamped week1 run)
- Observed total runtime:
  - `574150 ms` (about `9m 34s`)
- Exit code:
  - `0`

## Outcome summary

- Pipeline execution: PASS
- Metrics integrity check: PASS
- FGSM sanity check:
  - PASS in non-strict mode (all-zero FGSM accepted as current stress-test behavior)
- Artifact generation: PASS

Generated files in `outputs/demo-reference/plots`:

- `map50-by-attack.png`
- `precision-recall-by-attack.png`
- `baseline-vs-fgsm-metrics.png`
- `fgsm-epsilon-trend.png`
- `robustness-report-card.png`
- `robustness-report-card-by-epsilon.png`

## Fast pre-demo gate checks (no rerun)

Canonical artifact rebuild command:

- `bash scripts/generate_week1_demo_artifacts.sh --output-root outputs/demo-reference`

Gate commands and latest outcomes:

- Integrity gate:
  - `./.venv/bin/python scripts/check_metrics_integrity.py --csv outputs/demo-reference/metrics_summary.csv --attack fgsm`
  - Result: `PASS`
- FGSM sanity (non-strict):
  - `./.venv/bin/python scripts/check_fgsm_sanity.py --csv outputs/demo-reference/metrics_summary.csv --attack fgsm --use-latest-session`
  - Result: `PASS` (`run_session_id=6ff086c9636f`)
- FGSM strict collapse check:
  - `./.venv/bin/python scripts/check_fgsm_sanity.py --csv outputs/demo-reference/metrics_summary.csv --attack fgsm --use-latest-session --fail-on-all-zero-fgsm`
  - Result: `FAIL (expected narrative signal: all-zero FGSM collapse)`

## Notes for live segment

- Prefer demo-safe matrix for live segment:
  - `configs/week1_stabilization_demo_matrix.yaml`
- Keep fallback presentation root ready:
  - `outputs/demo-reference`
