# Repository Agent Instructions

Use [CODE_QUALITY_STANDARD.md](CODE_QUALITY_STANDARD.md) as the default quality
contract for this repository.

Non-negotiable expectations:

- prefer the smallest coherent change
- preserve public behavior unless the task explicitly changes it
- do not leave dead code, placeholder code, commented-out logic, or untested
  compatibility hacks
- keep imports and module boundaries intentional
- when wrappers or shims are involved, preserve old paths and add compatibility
  tests
- run the relevant lint and test subset before stopping
- report:
  - what changed
  - what was verified
  - any remaining risks

Repo-specific guidance:

- canonical runtime entrypoints are `scripts/run_unified.py run-one|sweep`
- `scripts/sweep_and_report.py` is a supported compatibility backend
- root `scripts/*.py` workflow entrypoints may be compatibility wrappers; new
  code should prefer the moved implementation packages when the wrapper docstring
  says so
- `lab.reporting` umbrella imports are compatibility-only; prefer
  `lab.reporting.framework`, `lab.reporting.local`, or
  `lab.reporting.aggregate`

If a result would score below `10/12` on the rubric in
`CODE_QUALITY_STANDARD.md`, keep refining before stopping.
