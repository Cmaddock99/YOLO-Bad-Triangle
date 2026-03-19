# Repository Hygiene and Documentation Review

Review basis: Python best practices (PEP8-style readability, safety defaults, error handling, CLI ergonomics, and documentation clarity).

## Phase 0 - Checklist and Inventory

Checklist source:

- `docs/REPO_HYGIENE_CHECKLIST.md`

Inventory reviewed:

- `src/lab/runners/`
- `src/lab/eval/`
- `src/lab/reporting/`
- `scripts/`
- `tests/`
- `configs/`
- Top-level documentation (`README.md`, `PROJECT_STATE.md`, `READINESS_REPORT.md`, `scripts/demo/README.md`)

## Phase 1 - Core Execution Paths

Files reviewed:

- `src/lab/runners/run_experiment.py`
- `src/lab/runners/experiment_runner.py`
- `scripts/sweep_and_report.py`
- `scripts/run_overnight_stress.py`

### Findings (severity-ranked)

- **High**: default destructive cleanup in legacy runner flow (`shutil.rmtree(...)`) can remove prior artifacts without explicit force intent.
- **High**: broad exception swallowing in JSON mapping helper reduces diagnosability.
- **Medium**: CLI failure ergonomics rely on uncaught exceptions in several script entrypoints.
- **Medium**: orchestration methods are long and combine many responsibilities.
- **Medium**: observability is mostly print-based and not structured.

### Scores

- Readability: 6.5/10
- Safety defaults: 5.5/10
- Observability: 7.0/10

### Quick wins

- Add top-level exception mapping in script `main()` functions for clean CLI errors.
- Narrow broad `except Exception` blocks to specific exception families.
- Add explicit opt-in clean flags around destructive deletes.

### Deeper refactors

- Split large run orchestration into stage-specific pure helpers.
- Introduce structured logging strategy with run/stage context fields.

## Phase 2 - Evaluation and Reporting

Files reviewed:

- `src/lab/eval/*.py`
- `src/lab/reporting/*.py`
- `scripts/print_summary.py`
- `scripts/generate_team_summary.py`

### Findings (severity-ranked)

- **High**: baseline selection in team summary currently keys only on `attack=none`; should also constrain `defense=none`.
- **High**: none-like normalization differs across modules (`none` vs `identity`/empty).
- **Medium**: interpretation can overstate confidence when required metrics are missing.
- **Medium**: prediction schema checks are shallow for nested value shape/type guarantees.
- **Low**: schema key naming drift (`MODEL` vs `model`, `avg_conf` vs `avg_confidence`) adds adapter complexity.

### Quick wins

- Standardize none-like normalization helper across reporting paths.
- Tighten baseline matching in team-summary payload creation.
- Add explicit insufficient-data interpretation path.

### Deeper refactors

- Introduce a canonical versioned metrics/report schema with translators from legacy/framework payloads.

## Phase 3 - Tests and Maintainability

Files reviewed:

- `tests/*.py`

### Findings (severity-ranked)

- **High**: some recently added runtime surfaces were initially under-tested and required dedicated script-level tests.
- **Medium**: tests often assert private helper internals, increasing brittleness during harmless refactors.
- **Medium**: failure-path orchestration coverage is thinner than happy-path coverage for some scripts.
- **Low/Medium**: random input usage can create backend-dependent nondeterminism if seeds are not consistently controlled.

### Quick wins

- Increase black-box CLI contract tests for script entrypoints.
- Add explicit deterministic seeds where random tensors/images are used.

### Deeper refactors

- Introduce a layered test strategy: unit (pure helpers), integration (artifact contracts), and thin end-to-end smoke suites.

## Phase 4 - Documentation Readability

### Improvements applied

- Added top-level onboarding and operations guide:
  - `README.md`
- Added reusable hygiene checklist:
  - `docs/REPO_HYGIENE_CHECKLIST.md`
- Expanded repository hygiene findings into this phased report:
  - `docs/REPO_HYGIENE_REVIEW.md`
- Improved demo operator documentation in:
  - `scripts/demo/README.md`

### Remaining documentation gaps

- Some state snapshot docs can drift over time without a clear update cadence.
- Cross-doc duplication exists between status reports and architecture notes.

## Phase 5 - Consolidated Action Plan

## Immediate (same-day)

1. Add explicit CLI error wrappers for all operational scripts.
2. Fix baseline matching and none-like normalization inconsistencies in reporting.
3. Add/expand failure-path tests for long-running orchestrators.

## This week (medium refactors)

1. Break long runner methods into stage-oriented helpers.
2. Introduce centralized schema normalization layer for report/eval keys.
3. Add structured logging levels and run-context fields.

## Documentation follow-through

1. Keep `README.md` as canonical onboarding path.
2. Add update metadata (`validated_at`, `commit`) to status snapshots.
3. Reduce duplicate prose by linking to one source of truth per topic.

## Acceptance Criteria for "Hygiene Complete"

- No blocker findings in core paths.
- High findings fixed or accepted with explicit mitigation notes.
- Category scores >= 7/10 for readability, safety defaults, observability, and documentation.
- Onboarding docs allow a new user to execute smoke + full workflows without tribal knowledge.

