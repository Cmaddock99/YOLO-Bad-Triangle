# Week1 Demo Rehearsal Log

## Rehearsal run

- Date (UTC): `2026-03-17`
- Command:
  - `./scripts/run_week1_stabilization.sh --profile week1-demo --mode demo`
- Output root:
  - `outputs/yolo26_repo_readiness_week1`
- Total wall clock:
  - `real 604.30s` (`10m 04s`)

## Stage timing windows (observed)

The run completed in about `10 minutes` on the current machine profile.
For planning purposes, budget:

- Preflight + setup: `< 1 min`
- Matrix compute + validation: `8-10 min`
- Integrity/sanity/table/plots finalization: `< 1 min`

## Outcome summary

- Pipeline completed end-to-end and generated all demo artifacts.
- FGSM sanity checks passed (including strict no-all-zero gate).
- Demo-profile epsilons (`0.0005`, `0.006`, `0.01`) produced a non-zero monotonic degradation trend under YOLO26.

## Presenter guidance

- For a 20+ minute segment, budget `~10 minutes` for compute + `~5-10 minutes` for walkthrough and Q&A.
- Keep `docs/WEEK1_DEMO_BASELINE.md` open for immediate fallback if runtime/environment instability appears.
