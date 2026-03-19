# Repository Hygiene Checklist

Use this checklist for phased repository quality reviews.

## Scoring Rubric (0-10 per category)

- **Readability**: naming, function size, cohesion, comments, type clarity.
- **Safety Defaults**: destructive behavior control, validation, fail-fast behavior.
- **Observability**: logging quality, error messages, traceability artifacts.
- **Documentation Quality**: discoverability, command correctness, human readability.

## Category Checklist

### Code Structure and Readability

- Functions are focused and reasonably sized.
- Naming is descriptive and consistent with module intent.
- Public APIs avoid ambiguous or overloaded behavior.
- Control flow is easy to follow without deep nesting.
- Type hints are present for non-trivial interfaces.

### Error Handling and Safety

- No broad exception swallowing without context.
- User-facing scripts fail with actionable messages.
- Destructive operations are explicit and guarded.
- Input/config validation is early and clear.
- Default behavior is safe and predictable.

### CLI Ergonomics

- `--help` text is complete and understandable.
- Defaults are documented and deterministic.
- Errors include remediation hints.
- Dry-run/resume behavior is explicit.

### Observability and Operations

- Logs show stage, context, and outcomes.
- Long-running jobs include heartbeat/progress.
- Status artifacts are machine-readable.
- Post-run validation checks are available.

### Test Quality

- Critical paths have both happy and failure-path tests.
- Tests minimize direct coupling to private internals.
- Determinism controls are used where randomness appears.
- Contract/schema expectations are asserted.

### Documentation Quality

- Top-level onboarding exists and is current.
- Core command paths are documented with examples.
- Output locations and meanings are explained.
- Operational runbooks exist for smoke and full runs.
- Docs include assumptions/scope and update date where needed.

## Suggested Phase Gate

A phase is considered healthy when:

- No blocker findings.
- High findings have either fixes or accepted mitigations.
- Category scores are all >= 7/10, with at least one improvement action for any lower score.

