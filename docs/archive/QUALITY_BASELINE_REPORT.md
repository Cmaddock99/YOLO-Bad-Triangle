# Quality Baseline Report

Date: 2026-03-18  
Scope: `src/lab/runners`, `src/lab/attacks`, `src/lab/defenses`, `src/lab/eval`, `configs`

## Rubric (Pragmatic)

- Naming/structure consistency
- Interface clarity
- Error handling and failure visibility
- Config/schema consistency
- Dead code/duplication hotspots

## Findings Summary

## 1) Naming/Structure Consistency

- **Pass**: Clear package boundaries under `src/lab/*`.
- **Pass**: Legacy and framework stacks are separated in naming (`base.py` vs `base_*` adapters).
- **Gap**: Multiple entrypoints and overlapping config families increase operator ambiguity.

## 2) Interface Clarity

- **Pass**: Framework interfaces are explicit:
  - `BaseModel`
  - `BaseAttack`
  - `BaseDefense`
- **Pass**: Normalized prediction schema (`PredictionRecord`) is consistently used by framework path.
- **Gap**: Legacy runner still relies on dynamic signature inspection for attack model injection (fragile contract).

## 3) Error Handling / Observability

- **Pass**: Legacy runner includes stage-tagged failure reason and row status.
- **Pass**: Framework metrics include explicit validation status (`missing|partial|complete|error`).
- **Gap**: Framework runner did not assert image write success (`cv2.imwrite`) before this hardening phase.
- **Gap**: Plugin discovery in framework registries relied on hardcoded import lists (easy drift risk).

## 4) Config / Schema Consistency

- **Pass**: Legacy and framework schemas are both documented and usable.
- **Gap**: Two active schemas (`experiment_lab`/matrix vs `lab_framework_phase5`) are incompatible and can be mixed accidentally.
- **Gap**: Historical scaffold configs remain in tree and can be mistaken as canonical.

## 5) Duplication / Cleanup Hotspots

- Duplicate semantics across multiple entrypoints:
  - `run_experiment.py`
  - `run_experiment_api.py`
  - `scripts/run_framework.py`
  - `src/lab/runners/run_experiment.py`
- Parallel metrics systems:
  - legacy CSV path
  - framework JSON path

## Scorecard

| Area | Score | Notes |
|---|---:|---|
| Naming/structure | 8/10 | Good modular layout, some historical scaffolding clutter |
| Interface clarity | 8/10 | Strong framework contracts, legacy dynamic behaviors remain |
| Error handling | 7/10 | Good status reporting, some silent degradation paths |
| Config consistency | 6/10 | Dual schema is the main operational complexity |
| Duplication control | 6/10 | Entrypoint and registry overlap still high |

Overall (pragmatic): **7/10** and suitable for stability matrix + targeted hardening.

## High-Value Hardening Targets (Phase 3)

1. Normalize framework plugin discovery to avoid manual registry import drift.
2. Tighten write-path failure checks in framework runner.
3. Keep legacy behavior stable while adding clearer deprecation guidance and framework-first docs.
