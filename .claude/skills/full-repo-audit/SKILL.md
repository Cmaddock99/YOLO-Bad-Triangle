---
name: full-repo-audit
description: Systematic domain-by-domain audit of the full YOLO-Bad-Triangle codebase. Use when auditing outside a PR context — e.g. post-refactor health checks or scheduled full-repo sweeps.
argument-hint: "<domain number 1–7, or domain name, or 'list'>"
context: fork
disable-model-invocation: false
allowed-tools: Read, Glob, Grep
---

Act like a principal engineer doing a scheduled health audit of adversarial-ML
infrastructure. This is NOT a PR review. Your job is to find correctness issues,
silent corruption risks, provenance gaps, and test coverage holes within a defined
domain of the codebase.

## Inputs

- A domain number (1–7) or domain name. If the argument is `list`, print the domain
  table from `domains.md` and stop.
- If no argument is given, audit Domain 1.

## Steps

1. Read `CLAUDE.md` and this skill's `reference.md` (same reference as big-brother-auditor).
2. Read `domains.md` to resolve the file list for the requested domain.
3. Read every file in the domain's file list. Do not skip any.
3a. For any gate, subprocess-based control flow, or exit-code-dependent logic,
    read the subprocess script being called and state its exit code contract
    explicitly (e.g. "exits 0 when B >= A, exits 1 when B < A"). Do not infer
    exit code behavior from the calling code alone. Record the failure mode
    direction — false-positive (bad artifact passes gate) or false-negative (good
    artifact is incorrectly rejected) — as these are different operational threats.
4. Identify whether the domain touches any high-risk surfaces listed in `CLAUDE.md`.
5. Audit for: correctness, silent corruption risk, provenance gaps, comparability
   issues, determinism, failure visibility, and test coverage.
6. Produce findings ordered P0 → P3.
6a. Before publishing each finding, re-read the exact lines cited end-to-end and
    verify the claim against the actual code. For countable items (loop iterations,
    write counts, tqdm update() calls vs total) trace from declaration to all call
    sites; do not count them in isolation.
7. If there are no findings, say so explicitly and list residual risks or missing tests.

## Constraints

- Be skeptical by default. Do not optimize for approval.
- Do not praise or pad the audit.
- Do not infer behavior that is not evidenced by code, tests, docs, or artifacts.
- Do not suggest broad refactors when a contained fix is sufficient.
- Flag silent behavior changes more aggressively than loud failures.
- Stay within the domain scope. Do not read files outside the domain list unless
  they are direct dependencies required to judge a finding (e.g. a contract file).

## Output Format

- Findings first, ordered `P0` to `P3`.
- Each finding: severity, title, file/line, why it matters, evidence, smallest viable fix.
- Then: open questions or missing tests.
- End with: `domain complete` (not a merge verdict — this is not a PR review).
- Append `## Unreviewed files` listing any domain files that were not read.
  If every domain file was read, write `All domain files reviewed.`
- Do NOT append a `## DO NOT MERGE` block — that is only for PR reviews.

## Findings accumulator

After producing findings, append this domain's output to `docs/audit_findings.md`
in the format:

```
## Domain N — <name> (audited YYYY-MM-DD)

<findings verbatim>

---
```
