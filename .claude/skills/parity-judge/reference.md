# parity-judge reference

## Core decision rule
- Parity is a migration confidence judgment, not a superficial metric diff.
- Comparability preconditions must pass before final parity status can be `pass` or `fail`.

## Comparability checklist
- Experiment intent is equivalent across legacy and framework runs.
- Evaluation scope is equivalent enough for metric comparison.
- Counts and key config assumptions are compatible.

## Status semantics
- `pass`: comparable and all required deltas are within tolerance.
- `fail`: comparable and one or more required deltas violate tolerance.
- `inconclusive`: comparability or evidence requirements are not satisfied.

## Mismatch categories
- `missing_file`
- `schema_shape`
- `count_mismatch`
- `config_mismatch`

## Notes
- Keep this skill strict and read-only.
- TODO: Add project-specific parity thresholds once explicitly standardized.
