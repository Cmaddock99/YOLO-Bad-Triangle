# Legacy Runtime Retirement and Rollback Window

This document defines the final retirement protocol for legacy runtime paths.

## Retirement Preconditions

- All surfaces have a passing shadow validation report for two consecutive cycles.
- Demo package commands succeed using framework-backed compatibility artifacts.
- No open P0/P1 migration defects.

## Rollout Sequence

1. **Cycle N (announce):**
   - Mark legacy runtime as deprecated in CLI help and docs.
   - Keep legacy path available behind explicit compatibility flags.
2. **Cycle N+1 (framework-default):**
   - Make framework wrappers default entry for migration-ready surfaces.
   - Keep rollback switches documented and tested.
3. **Cycle N+2 (retire):**
   - Remove legacy runtime execution from default paths.
   - Keep adapter generation and shadow validation scripts for one extra cycle.

## Rollback Switches

- One-run wrapper: `python run_experiment.py` (legacy compatibility behavior retained).
- Demo package: continue to support CSV-driven mode; framework compatibility artifacts can be regenerated.
- Batch flows: keep legacy scripts callable during rollback window.

## Monitoring During Rollback Window

- Track weekly:
  - shadow parity pass/fail counts,
  - demo gate pass rates (`check_metrics_integrity`, `check_fgsm_sanity`),
  - incident count tied to adapter outputs.

## Removal Checklist

- Remove deprecated warnings only after rollback window closes.
- Update `README.md` and runbooks to framework-first examples only.
- Archive final parity evidence report in `READINESS_REPORT.md` references.
