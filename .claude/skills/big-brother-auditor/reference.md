# big-brother-auditor reference

## Severity guide

- `P0`: fires under **normal invocation right now** and produces incorrect output, deploys a bad artifact, or corrupts experiment state. A latent bug that requires a future code restructure (e.g. a short-circuit change, argument reorder) to trigger is `P1` at most. Reserve P0 for bugs that execute on the current, unmodified call path with no special conditions.
- `P1`: high-probability correctness bug, provenance gap, comparability break, or missing guard in a high-risk path.
- `P2`: meaningful maintainability or test gap that could mask future correctness issues.
- `P3`: polish, clarity, or low-risk cleanup.

## Mandatory audit checks

- Framework-first integration: no parallel runner or reporting path unless intentionally introduced and justified.
- Artifact contract integrity: required outputs remain valid and machine-parseable.
- Schema/version alignment: `schemas/v1/`, `src/lab/config/contracts.py`, and emitted payloads stay consistent.
- Determinism: seeded randomness is explicit and preserved through orchestration.
- Provenance: checkpoint identity, routing metadata, and reporting context are not guessed or silently dropped.
- Comparability: baseline, attack-only, and defended rows are paired like-for-like before conclusions are drawn.
- Failure visibility: code fails loudly on invalid states instead of returning misleading success.

## Area-specific checks

### `scripts/auto_cycle.py`

- atomic state writes
- lock cleanup on early exit
- idempotent resume behavior
- no stale `cycle_state.json` assumptions
- trainable-defense-only training signals where applicable
- bounded tuning logic and safe handling of missing metrics

### `src/lab/runners/run_experiment.py`

- canonical pipeline semantics preserved
- run artifacts remain complete
- reporting context and provenance are persisted correctly
- optional artifacts do not break required ones

### `src/lab/reporting/` and `src/lab/eval/`

- authoritative Phase 4 rows outrank diagnostic smoke rows
- missing or incomparable rows are surfaced explicitly
- deterministic output ordering
- warnings do not overclaim beyond evidence
- per-class and bootstrap outputs remain aligned with contracts

### `src/lab/attacks/`

- registration works via the framework registry
- objective mode, target class, and ROI are honored correctly
- output image shape/dtype stay unchanged
- randomness is controllable
- invalid params fail loudly

### `src/lab/defenses/`

- registration works via the framework registry
- preprocess and postprocess responsibilities stay clear
- checkpointed defenses expose provenance correctly
- routing heuristics are explainable and surfaced in metadata
- clean-image degradation risk is considered where relevant

## Review style

- Findings first. No summary before findings.
- Prefer "unknown" or "inconclusive" over speculation.
- Minimal fix over broad redesign.
- If no finding is provable, write `No findings.` and then note residual risks or missing tests.
