# Week1 Demo Rehearsal Log

## Rehearsal run

- Date (UTC): `2026-03-15`
- Command:
  - `./scripts/run_week1_stabilization.sh --mode demo --config configs/week1_stabilization_demo_matrix.yaml`
- Output root:
  - `outputs/demo-reference` (linked to timestamped rehearsal run)
- Total wall clock:
  - `real 574.15s` (`9m 34s`)

## Stage timing windows (observed)

These windows are based on `run_started_at_utc`, per-row timestamps in `metrics_summary.csv`,
and final command wall-clock output.

- Preflight + setup: ~`0m 00s` to `0m 03s`
- Baseline run complete: ~`1m 50s`
- FGSM `epsilon=0.0005` complete: ~`4m 20s`
- FGSM `epsilon=0.001` complete: ~`6m 52s`
- FGSM `epsilon=0.002` complete: ~`9m 27s`
- Integrity/sanity/table/plots finalization: ~`9m 27s` to `9m 34s`

## Outcome summary

- Pipeline completed end-to-end and generated all demo artifacts.
- FGSM sanity check failed (all-zero FGSM validation metrics), but demo mode continued as expected.
- Calibrated epsilons (`0.0005`, `0.001`, `0.002`) still collapsed validation metrics to zero.

## Presenter guidance

- For a 20+ minute segment, budget `~10 minutes` for compute + `~5-10 minutes` for walkthrough and Q&A.
- Keep `docs/WEEK1_DEMO_BASELINE.md` open for immediate fallback if runtime/environment instability appears.
