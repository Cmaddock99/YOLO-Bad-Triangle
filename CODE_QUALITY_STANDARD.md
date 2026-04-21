# Code Quality Standard

This repository does not use a single external "industry standard" document as
its source of truth. Instead, it uses a repo-specific standard aligned with
common industry practice:

- explicit public contracts
- small, reviewable changes
- lint, type, and test gates
- severity-ranked review findings
- backwards-compatibility discipline
- honest documentation

Use this file as the quality contract for humans, AI agents, and review.

## Non-Negotiables

1. Prefer the smallest coherent change.
2. Preserve public behavior unless the task explicitly changes it.
3. Do not leave dead code, placeholder code, commented-out logic, or unused
   helpers behind.
4. Keep imports and module boundaries intentional. Prefer concrete modules over
   broad facades unless the facade is part of a documented compatibility
   contract.
5. Compatibility wrappers and shims are allowed only when they are:
   - explicitly marked as compatibility-only
   - covered by import/CLI compatibility tests
   - behavior-preserving
6. New code must not quietly weaken existing errors, contracts, or output
   semantics.
7. Comments and docs must be honest. Do not describe future intent as present
   behavior.
8. Verification is part of the change. A patch that "probably works" is not
   done.

## Definition Of Done

A change is done only when all of the following are true:

- the change is minimal, coherent, and understandable
- affected behavior is tested at the right level
- touched code passes the relevant lint/type/test checks
- compatibility paths are tested when wrappers or shims are involved
- user-facing behavior, paths, and contracts are either preserved or
  intentionally updated
- the final summary states:
  - what changed
  - what was verified
  - any remaining risks or known follow-up

## Review Severity Scale

- `P0`: breaks runtime, artifacts, contracts, safety, or core execution
- `P1`: likely regression, misleading behavior, or broken operator workflow
- `P2`: maintainability, design, or boundary problem that should be fixed
- `P3`: polish, readability, or consistency issue

## Quality Rubric

Score each category `0`, `1`, or `2`.

- `Correctness`
  - `2`: behavior is clearly correct and contract-preserving
  - `1`: probably correct but under-verified or slightly ambiguous
  - `0`: likely regression or unclear behavior
- `Simplicity`
  - `2`: smallest coherent solution
  - `1`: slightly overbuilt but understandable
  - `0`: unnecessary abstraction, indirection, or churn
- `Boundary hygiene`
  - `2`: imports and ownership are clear
  - `1`: acceptable but still somewhat broad or mixed
  - `0`: crosses boundaries carelessly or creates muddled ownership
- `Testability`
  - `2`: changed behavior is directly covered
  - `1`: partial or indirect coverage
  - `0`: no meaningful verification
- `Compatibility discipline`
  - `2`: public paths/contracts preserved and tested
  - `1`: preserved but weakly tested
  - `0`: accidental breakage or undocumented drift
- `Documentation honesty`
  - `2`: docs/comments match reality
  - `1`: mostly accurate with minor drift
  - `0`: misleading or stale

Interpretation:

- `10-12`: good
- `7-9`: acceptable but should be tightened
- `<7`: too sloppy to merge

## Rules By Change Type

### Runtime and orchestration changes

- preserve canonical entrypoints unless explicitly changing them
- preserve artifact paths and schemas unless explicitly changing them
- do not weaken error handling silently
- verify with targeted runtime tests and the relevant smoke path when practical

### Wrapper and shim changes

- wrapper modules must stay behavior-preserving
- old import paths must still resolve to the moved module object when that is
  the compatibility contract
- direct `python scripts/...` execution must keep working for wrapper scripts
- add explicit compatibility tests

### Registry, plugin, and boundary changes

- keep alias strings stable unless the task explicitly changes them
- make ownership explicit at the import layer before moving implementation
- prefer staged extraction over large path-breaking moves

### Docs-only changes

- do not broaden claims beyond what the repo actually enforces
- update top-level docs only when the public contract changed
- keep historical context separate from current runbook guidance

## Verification Matrix

Choose the smallest set that proves the change, but do not skip the relevant
class of checks.

- Code movement with wrappers/shims:
  - targeted compatibility tests
  - direct `--help` smoke for CLI wrappers when applicable
  - `ruff` on touched files
- Runtime/reporting/plugin behavior:
  - targeted `pytest`
  - relevant smoke or dry-run path
  - `ruff`
  - `mypy` when the change touches typed orchestration or contracts.
    Scope is currently limited to `src/lab/eval/`, `src/lab/reporting/`, and
    `src/lab/runners/` (see `[tool.mypy].files` in `pyproject.toml`); changes
    outside these paths are not type-checked by the gate.
- CI/tooling changes:
  - exact contract tests for command shape
  - one real smoke invocation when possible

## Retroactive Audit Commands

Use these commands to audit the repository against this standard.

Quick structural/compatibility audit:

```bash
./.venv/bin/python scripts/ci/run_repo_standards_audit.py --lane compat
```

Broader repo-quality audit:

```bash
./.venv/bin/python scripts/ci/run_repo_standards_audit.py --lane full
```

The `full` lane intentionally includes the repo quality gate and may surface
known repo-wide issues such as current mypy debt.

## Drop-In Agent Prompt

Use this prompt when you want an AI coding agent to work to this repo's quality
bar:

```text
Follow CODE_QUALITY_STANDARD.md as the default quality contract for this repo.

Requirements:
- Prefer the smallest coherent change.
- Preserve public behavior unless the task explicitly changes it.
- Do not leave dead code, placeholder code, commented-out logic, or untested compatibility hacks.
- Keep imports and module boundaries intentional; avoid broad facades when a concrete module is clearer.
- Add or update tests for changed behavior, and add compatibility tests when wrappers or shims are involved.
- Run the relevant lint and test subset before stopping.
- In your final summary, report:
  1. what changed,
  2. what was verified,
  3. any remaining risks.

If the result would score below 10/12 on correctness, simplicity, boundary hygiene, testability, compatibility discipline, and documentation honesty, keep refining before stopping.
```

## PR Checklist

Use the repo PR template and confirm:

- scope is minimal and coherent
- public behavior is preserved or intentionally documented
- wrappers/shims are marked and tested when introduced or changed
- relevant checks were run
- remaining risks are stated explicitly
